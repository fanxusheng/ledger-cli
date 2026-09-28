import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path

from .models import NewRecord, Record, RecordFilters, Summary


def _where_clause(filters: RecordFilters | None) -> tuple[str, list[str]]:
    if filters is None:
        return "", []
    conditions = []
    parameters = []
    for condition, value in (
        ("date >= ?", filters.start_date),
        ("date <= ?", filters.end_date),
        ("kind = ?", filters.kind),
        ("category = ?", filters.category),
    ):
        if value is not None:
            conditions.append(condition)
            parameters.append(value)
    return (" WHERE " + " AND ".join(conditions) if conditions else ""), parameters


class Ledger:
    def __init__(self, path: Path):
        self.path = Path(path).expanduser()

    @contextmanager
    def _connect(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path, timeout=5)) as connection:
            connection.row_factory = sqlite3.Row
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT NOT NULL,
                        kind TEXT NOT NULL CHECK (kind IN ('收入', '支出')),
                        category TEXT NOT NULL CHECK (length(trim(category)) > 0),
                        amount_cents INTEGER NOT NULL
                            CHECK (typeof(amount_cents) = 'integer' AND amount_cents > 0),
                        note TEXT NOT NULL DEFAULT ''
                    )
                    """
                )
                yield connection

    @contextmanager
    def _read_connect(self, filters: RecordFilters | None):
        if not self.path.exists():
            if filters is None:
                # 保留第一版无筛选查询首次初始化空账本的行为。
                with self._connect() as connection:
                    yield connection
            else:
                # 筛选和导出不创建账本或父目录。
                yield None
            return
        uri = self.path.resolve().as_uri() + "?mode=ro"
        with closing(sqlite3.connect(uri, uri=True, timeout=5)) as connection:
            connection.row_factory = sqlite3.Row
            yield connection

    def add(self, record: NewRecord) -> int:
        with self._connect() as connection:
            cursor = connection.execute(
                """INSERT INTO records (date, kind, category, amount_cents, note)
                   VALUES (?, ?, ?, ?, ?)""",
                (record.date, record.kind, record.category, record.amount_cents, record.note),
            )
            return cursor.lastrowid

    def list_records(self, filters: RecordFilters | None = None) -> list[Record]:
        where, parameters = _where_clause(filters)
        with self._read_connect(filters) as connection:
            if connection is None:
                return []
            rows = connection.execute(
                """SELECT id, date, kind, category, amount_cents, note
                   FROM records""" + where + " ORDER BY date ASC, id ASC",
                parameters,
            ).fetchall()
        return [Record(**dict(row)) for row in rows]

    def summarize(self, filters: RecordFilters | None = None) -> Summary:
        income = expense = 0
        where, parameters = _where_clause(filters)
        with self._read_connect(filters) as connection:
            if connection is None:
                return Summary(0, 0)
            # Python 整数累加，避免 SQLite SUM 在多笔大额记录下溢出。
            for row in connection.execute("SELECT kind, amount_cents FROM records" + where, parameters):
                if row["kind"] == "收入":
                    income += row["amount_cents"]
                else:
                    expense += row["amount_cents"]
        return Summary(income, expense)
