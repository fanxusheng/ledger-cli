import os
from contextlib import closing
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from ledger.models import format_amount
from ledger.storage import Ledger
from ledger.validation import MAX_CENTS, validate_record


ROOT = Path(__file__).resolve().parent.parent


class ValidationTests(unittest.TestCase):
    def record(self, **changes):
        values = dict(date_text="2026-09-01", kind="收入", category="工资", amount_text="1000.00")
        values.update(changes)
        return validate_record(**values)

    def test_real_leap_day(self):
        self.assertEqual(self.record(date_text="2024-02-29").date, "2024-02-29")

    def test_impossible_dates(self):
        for value in ("2026-02-29", "2026-09-31", "2026-13-01", "0000-01-01"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "日期不存在"):
                self.record(date_text=value)

    def test_strict_date_format(self):
        for value in ("2026-9-01", "20260901", "2026/09/01", " 2026-09-01", "２０２６-09-01"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
                self.record(date_text=value)

    def test_invalid_type(self):
        with self.assertRaisesRegex(ValueError, "类型"):
            self.record(kind="转账")

    def test_empty_category(self):
        for value in ("", " ", "\t\n", "　"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "分类不能为空"):
                self.record(category=value)

    def test_category_trim_and_optional_note(self):
        record = self.record(category=" 工资 ")
        self.assertEqual(record.category, "工资")
        self.assertEqual(record.note, "")

    def test_amount_converted_exactly(self):
        for value, expected in (("10", 1000), ("10.5", 1050), ("0.01", 1), ("0001.20", 120)):
            with self.subTest(value=value):
                self.assertEqual(self.record(amount_text=value).amount_cents, expected)

    def test_invalid_amounts(self):
        for value in ("-1", "0", "0.00", "1.001", "1.000", "NaN", "inf", "1e2", ".5", "1.", "1,000", " 1", ""):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "金额"):
                self.record(amount_text=value)

    def test_amount_limit_and_long_input(self):
        self.assertEqual(self.record(amount_text=format_amount(MAX_CENTS)).amount_cents, MAX_CENTS)
        for value in (format_amount(MAX_CENTS + 1), "9" * 5000):
            with self.subTest(length=len(value)), self.assertRaisesRegex(ValueError, "不能超过"):
                self.record(amount_text=value)

    def test_money_format(self):
        for value, expected in ((0, "0.00"), (1, "0.01"), (-1, "-0.01"), (-101, "-1.01"), (100000, "1000.00")):
            with self.subTest(value=value):
                self.assertEqual(format_amount(value), expected)


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "nested" / "账本.sqlite3"
        self.ledger = Ledger(self.path)

    def add(self, date="2026-09-01", kind="收入", amount="1.00", category="工资", note=""):
        return self.ledger.add(validate_record(date, kind, category, amount, note))

    def test_empty_database(self):
        self.assertEqual(self.ledger.list_records(), [])
        summary = self.ledger.summarize()
        self.assertEqual((summary.income_cents, summary.expense_cents, summary.net_cents), (0, 0, 0))

    def test_dates_then_ids_ordered_and_ids_unique(self):
        ids = [self.add(date="2026-09-02"), self.add(date="2026-09-01"), self.add(date="2026-09-02")]
        self.assertEqual(ids, [1, 2, 3])
        self.assertEqual([r.id for r in self.ledger.list_records()], [2, 1, 3])

    def test_reopen_retains_all_fields(self):
        self.add(kind="支出", amount="25.50", category="餐饮", note="午餐")
        record = Ledger(self.path).list_records()[0]
        self.assertEqual((record.id, record.date, record.kind, record.category, record.amount_cents, record.note),
                         (1, "2026-09-01", "支出", "餐饮", 2550, "午餐"))
        self.assertEqual(Ledger(self.path).add(validate_record("2026-09-02", "收入", "工资", "1")), 2)

    def test_required_summary(self):
        self.add(amount="1000.00")
        self.add(date="2026-09-02", kind="支出", amount="25.50", category="餐饮", note="午餐")
        self.add(date="2026-09-02", kind="支出", amount="10.00", category="交通")
        summary = self.ledger.summarize()
        self.assertEqual((summary.income_cents, summary.expense_cents, summary.net_cents), (100000, 3550, 96450))

    def test_small_amounts_and_negative_net(self):
        self.add(amount="0.10")
        self.add(amount="0.20")
        self.add(kind="支出", amount="0.31")
        summary = self.ledger.summarize()
        self.assertEqual(summary.income_cents, 30)
        self.assertEqual(format_amount(summary.net_cents), "-0.01")

    def test_summary_beyond_single_sqlite_integer(self):
        self.add(amount=format_amount(MAX_CENTS))
        self.add(amount=format_amount(MAX_CENTS))
        self.assertEqual(self.ledger.summarize().income_cents, MAX_CENTS * 2)

    def test_special_text_roundtrip(self):
        note = "午餐 '); DROP TABLE records; --\n第二行|备注"
        self.add(category="餐饮'", note=note)
        record = self.ledger.list_records()[0]
        self.assertEqual(record.category, "餐饮'")
        self.assertEqual(record.note, note)

    def test_database_constraint_rejects_nonpositive_amount(self):
        self.ledger.list_records()
        with closing(sqlite3.connect(self.path)) as connection:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute(
                    "INSERT INTO records (date, kind, category, amount_cents) VALUES (?, ?, ?, ?)",
                    ("2026-09-01", "收入", "工资", 0),
                )
        self.assertEqual(self.ledger.list_records(), [])


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ledger tests ")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "账本.sqlite3"

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "ledger", "--db", str(self.path), *args],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )

    def add_args(self, **changes):
        values = {"date": "2026-09-01", "type": "收入", "category": "工资", "amount": "1000.00"}
        values.update(changes)
        return ["add", *(f"--{key}={value}" for key, value in values.items())]

    def test_empty_outputs(self):
        listed = self.run_cli("list")
        summary = self.run_cli("summary")
        self.assertEqual(listed.returncode, 0)
        self.assertEqual(listed.stdout, "暂无记录。\n")
        self.assertEqual(summary.returncode, 0)
        self.assertEqual(summary.stdout, "收入总额：0.00\n支出总额：0.00\n净收入：0.00\n")

    def test_process_restart_persistence_and_all_fields(self):
        result = self.run_cli(*self.add_args())
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli("list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, '编号 | 日期 | 类型 | 分类 | 金额 | 备注\n1 | 2026-09-01 | 收入 | "工资" | 1000.00 | ""\n')

    def test_invalid_input_does_not_create_database(self):
        result = self.run_cli(*self.add_args(category=""))
        self.assertEqual(result.returncode, 2)
        self.assertIn("分类不能为空", result.stderr)
        self.assertFalse(self.path.exists())

    def test_each_rejection_preserves_database_bytes(self):
        self.assertEqual(self.run_cli(*self.add_args()).returncode, 0)
        before = self.path.read_bytes()
        for changes, message in (({"date": "2026-02-30"}, "日期不存在"), ({"amount": "-1"}, "金额"),
                                 ({"amount": "1.001"}, "金额"), ({"category": ""}, "分类不能为空")):
            with self.subTest(changes=changes):
                result = self.run_cli(*self.add_args(**changes))
                self.assertEqual(result.returncode, 2)
                self.assertIn(message, result.stderr)
                self.assertEqual(self.path.read_bytes(), before)

    def test_special_characters_display_on_one_line(self):
        self.assertEqual(self.run_cli(*self.add_args(note="第一行\n第二行|末尾")).returncode, 0)
        result = self.run_cli("list")
        self.assertEqual(len(result.stdout.splitlines()), 2)
        self.assertIn(r'"第一行\n第二行\u007c末尾"', result.stdout)

    def test_missing_required_argument(self):
        result = self.run_cli("add", "--date", "2026-09-01")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--amount", result.stderr)
        self.assertFalse(self.path.exists())

    def test_bad_database_path_reports_error(self):
        self.path.mkdir()
        result = self.run_cli("list")
        self.assertEqual(result.returncode, 1)
        self.assertIn("数据文件操作失败", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_corrupt_database_reports_error(self):
        self.path.write_bytes(b"this is not a sqlite database")
        result = self.run_cli("summary")
        self.assertEqual(result.returncode, 1)
        self.assertIn("数据文件操作失败", result.stderr)
        self.assertEqual(self.path.read_bytes(), b"this is not a sqlite database")


if __name__ == "__main__":
    unittest.main()
