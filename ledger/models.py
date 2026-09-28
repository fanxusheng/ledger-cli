from dataclasses import dataclass


@dataclass(frozen=True)
class NewRecord:
    date: str
    kind: str
    category: str
    amount_cents: int
    note: str = ""


@dataclass(frozen=True)
class Record(NewRecord):
    id: int = 0


@dataclass(frozen=True)
class RecordFilters:
    start_date: str | None = None
    end_date: str | None = None
    kind: str | None = None
    category: str | None = None

    @property
    def active(self) -> bool:
        return any(value is not None for value in (
            self.start_date, self.end_date, self.kind, self.category
        ))


@dataclass(frozen=True)
class Summary:
    income_cents: int
    expense_cents: int

    @property
    def net_cents(self) -> int:
        return self.income_cents - self.expense_cents


def format_amount(cents: int) -> str:
    """始终使用整数计算，避免浮点误差，包括负净收入。"""
    sign = "-" if cents < 0 else ""
    whole, fraction = divmod(abs(cents), 100)
    return f"{sign}{whole}.{fraction:02d}"
