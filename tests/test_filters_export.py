import codecs
import csv
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from ledger.exporter import CSV_HEADER, export_csv
from ledger.storage import Ledger
from ledger.validation import validate_filters, validate_record


ROOT = Path(__file__).resolve().parent.parent
ZERO_SUMMARY = "收入总额：0.00\n支出总额：0.00\n净收入：0.00\n"


def list_rows(output):
    """将 CLI 的全部字段还原，逐字段比较 CSV，不依赖列宽。"""
    rows = []
    for line in output.splitlines()[1:]:
        number, day, kind, category, amount, note = line.split(" | ")
        rows.append([number, day, kind, json.loads(category), amount, json.loads(note)])
    return rows


class FilterValidationTests(unittest.TestCase):
    def test_no_filters_distinct_from_explicit_empty(self):
        self.assertFalse(validate_filters().active)
        for name in ("start_date", "end_date", "kind", "category"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate_filters(**{name: ""})

    def test_both_dates_are_strict_and_real(self):
        for name in ("start_date", "end_date"):
            for value in ("2026-02-29", "2026-9-01", "20260901", "2026-09-01 ", "0000-01-01"):
                with self.subTest(name=name, value=value), self.assertRaises(ValueError):
                    validate_filters(**{name: value})
        self.assertTrue(validate_filters("2024-02-29", "2024-02-29").active)

    def test_reversed_dates_rejected(self):
        with self.assertRaisesRegex(ValueError, "起始日期不得晚于结束日期"):
            validate_filters("2026-09-02", "2026-09-01")

    def test_type_and_category_validation(self):
        with self.assertRaisesRegex(ValueError, "类型"):
            validate_filters(kind="转账")
        for value in ("", " ", "\t\n", "　"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "分类不能为空"):
                validate_filters(category=value)
        self.assertEqual(validate_filters(category=" 餐饮 ").category, "餐饮")


class FilterExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ledger stage2 # % ")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.database = self.directory / "账本.sqlite3"
        self.ledger = Ledger(self.database)
        for day, kind, category, amount, note in (
            ("2026-09-01", "收入", "工资", "1000.00", ""),
            ("2026-09-02", "支出", "餐饮", "25.50", "午餐"),
            ("2026-09-02", "支出", "交通", "10.00", ""),
        ):
            self.add(day, kind, category, amount, note)

    def add(self, day, kind, category, amount="1.00", note=""):
        return self.ledger.add(validate_record(day, kind, category, amount, note))

    def run_cli(self, *args, db=None, expected_code=0):
        result = subprocess.run(
            [sys.executable, "-m", "ledger", "--db", str(db or self.database), *map(str, args)],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        self.assertEqual(result.returncode, expected_code, result.stdout + result.stderr)
        return result

    def csv_rows(self, path):
        self.assertTrue(path.read_bytes().startswith(codecs.BOM_UTF8))
        with path.open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.reader(stream))

    def test_interval_inclusive_and_one_sided_bounds(self):
        self.add("2026-08-31", "收入", "边界外")
        self.add("2026-09-03", "支出", "边界外")
        for arguments, expected in (
            (["--start-date=2026-09-01", "--end-date=2026-09-02"], ["1", "2", "3"]),
            (["--start-date=2026-09-02"], ["2", "3", "5"]),
            (["--end-date=2026-09-01"], ["4", "1"]),
        ):
            with self.subTest(arguments=arguments):
                rows = list_rows(self.run_cli("list", *arguments).stdout)
                self.assertEqual([row[0] for row in rows], expected)

    def test_same_day_expenses_and_summary(self):
        arguments = ["--start-date=2026-09-02", "--end-date=2026-09-02", "--type=支出"]
        rows = list_rows(self.run_cli("list", *arguments).stdout)
        self.assertEqual([row[0] for row in rows], ["2", "3"])
        self.assertEqual(self.run_cli("summary", *arguments).stdout,
                         "收入总额：0.00\n支出总额：35.50\n净收入：-35.50\n")

    def test_all_four_conditions_are_anded(self):
        self.add("2026-09-02", "收入", "餐饮")
        self.add("2026-09-02", "支出", "餐饮外卖")
        self.add("2026-09-03", "支出", "餐饮")
        arguments = ["--start-date=2026-09-02", "--end-date=2026-09-02", "--type=支出", "--category=餐饮"]
        self.assertEqual([r[0] for r in list_rows(self.run_cli("list", *arguments).stdout)], ["2"])
        self.assertEqual(self.run_cli("summary", *arguments).stdout,
                         "收入总额：0.00\n支出总额：25.50\n净收入：-25.50\n")
        output = self.directory / "combined.csv"
        self.run_cli("export", "--output", output, *arguments)
        self.assertEqual(self.csv_rows(output)[1:], list_rows(self.run_cli("list", *arguments).stdout))

    def test_category_exact_match_and_sql_parameters(self):
        self.add("2026-09-02", "支出", "餐饮外卖")
        self.add("2026-09-02", "支出", "%")
        self.add("2026-09-02", "支出", "' OR 1=1 --")
        for category, ids in (("餐", []), (" 餐饮 ", ["2"]), ("%", ["5"]), ("' OR 1=1 --", ["6"])):
            with self.subTest(category=category):
                result = self.run_cli("list", f"--category={category}")
                self.assertEqual([r[0] for r in list_rows(result.stdout)], ids)

    def test_filtered_order_is_date_then_id(self):
        self.add("2026-08-31", "支出", "交通")
        self.add("2026-09-02", "支出", "交通")
        arguments = ["--type=支出", "--category=交通"]
        rows = list_rows(self.run_cli("list", *arguments).stdout)
        self.assertEqual([row[0] for row in rows], ["4", "3", "5"])
        output = self.directory / "ordered.csv"
        self.run_cli("export", "--output", output, *arguments)
        self.assertEqual(self.csv_rows(output)[1:], rows)

    def test_every_command_rejects_bad_filters_without_side_effects(self):
        before = self.database.read_bytes()
        output = self.directory / "invalid.csv"
        for command in ("list", "summary", "export"):
            base = [command] + (["--output", output] if command == "export" else [])
            for arguments, message in (
                (["--start-date=2026-02-30"], "起始日期不存在"),
                (["--end-date=2026-02-30"], "结束日期不存在"),
                (["--start-date=2026-9-01"], "YYYY-MM-DD"),
                (["--start-date=2026-09-03", "--end-date=2026-09-02"], "起始日期不得晚于"),
                (["--type=转账"], "类型"),
                (["--type="], "类型"),
                (["--category="], "分类不能为空"),
                (["--category= \t　"], "分类不能为空"),
            ):
                with self.subTest(command=command, arguments=arguments):
                    result = self.run_cli(*base, *arguments, expected_code=2)
                    self.assertIn(message, result.stderr)
                    self.assertEqual(self.database.read_bytes(), before)
                    self.assertFalse(output.exists())

    def test_no_matches_list_summary_and_header_only_export(self):
        arguments = ["--category=不存在"]
        self.assertEqual(self.run_cli("list", *arguments).stdout, "无匹配记录。\n")
        self.assertEqual(self.run_cli("summary", *arguments).stdout, ZERO_SUMMARY)
        output = self.directory / "empty.csv"
        self.run_cli("export", "--output", output, *arguments)
        self.assertEqual(self.csv_rows(output), [list(CSV_HEADER)])

    def test_missing_ledger_not_created_by_filters_or_export(self):
        database = self.directory / "missing" / "new.sqlite3"
        self.assertEqual(self.run_cli("list", "--type=支出", db=database).stdout, "无匹配记录。\n")
        self.assertEqual(self.run_cli("summary", "--type=支出", db=database).stdout, ZERO_SUMMARY)
        output = self.directory / "new-empty.csv"
        self.run_cli("export", "--output", output, db=database)
        self.assertEqual(self.csv_rows(output), [list(CSV_HEADER)])
        self.assertFalse(database.parent.exists())

    def test_export_bom_header_money_and_all_fields_match_list(self):
        output = self.directory / "收支记录.csv"
        self.run_cli("export", "--output", output)
        rows = self.csv_rows(output)
        self.assertEqual(rows[0], list(CSV_HEADER))
        self.assertEqual(rows[1:], list_rows(self.run_cli("list").stdout))
        self.assertEqual([r[4] for r in rows[1:]], ["1000.00", "25.50", "10.00"])

    def test_csv_preserves_commas_quotes_crlf_and_newlines(self):
        category = '礼物,"朋友"\n回礼'
        note = '逗号, 双引号"内容"\r\n第二行\n第三行|末尾'
        self.run_cli("add", "--date=2026-09-03", "--type=支出", f"--category={category}",
                     "--amount=1.20", f"--note={note}")
        output = self.directory / "special.csv"
        self.run_cli("export", "--output", output, f"--category={category}")
        self.assertEqual(self.csv_rows(output)[1:], [["4", "2026-09-03", "支出", category, "1.20", note]])
        self.assertEqual(self.csv_rows(output)[1:], list_rows(self.run_cli("list", f"--category={category}").stdout))

    def test_existing_output_is_never_overwritten(self):
        output = self.directory / "existing.csv"
        original = b"original content\x00\xff"
        output.write_bytes(original)
        result = self.run_cli("export", "--output", output, expected_code=1)
        self.assertIn("已存在，拒绝覆盖", result.stderr)
        self.assertEqual(output.read_bytes(), original)

    def test_missing_parent_and_directory_target_report_errors(self):
        output = self.directory / "missing" / "export.csv"
        result = self.run_cli("export", "--output", output, expected_code=1)
        self.assertIn("父目录不存在", result.stderr)
        self.assertFalse(output.parent.exists())
        result = self.run_cli("export", "--output", self.directory, expected_code=1)
        self.assertIn("导出失败", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_permission_error_has_clear_message(self):
        with patch.object(Path, "open", side_effect=PermissionError("permission denied")):
            with self.assertRaisesRegex(OSError, "无法写入目标文件"):
                export_csv([], self.directory / "denied.csv")

    def test_output_cannot_be_database_even_when_missing(self):
        before = self.database.read_bytes()
        result = self.run_cli("export", "--output", self.database, expected_code=1)
        self.assertIn("不能与账本文件相同", result.stderr)
        self.assertEqual(self.database.read_bytes(), before)
        missing = self.directory / "nonexistent.sqlite3"
        self.run_cli("export", "--output", missing, db=missing, expected_code=1)
        self.assertFalse(missing.exists())

    def test_required_output_parameter(self):
        result = self.run_cli("export", expected_code=2)
        self.assertIn("--output", result.stderr)

    def test_read_operations_preserve_entire_database(self):
        before = self.database.read_bytes()
        for i, arguments in enumerate(([], ["--type=支出"], ["--category=不存在"])):
            self.run_cli("list", *arguments)
            self.run_cli("summary", *arguments)
            self.run_cli("export", "--output", self.directory / f"readonly-{i}.csv", *arguments)
            self.assertEqual(self.database.read_bytes(), before)

    def test_unfiltered_legacy_behavior_and_add_still_work(self):
        self.assertEqual(len(list_rows(self.run_cli("list").stdout)), 3)
        self.assertEqual(self.run_cli("summary").stdout,
                         "收入总额：1000.00\n支出总额：35.50\n净收入：964.50\n")
        self.run_cli("add", "--date=2026-09-04", "--type=收入", "--category=奖金", "--amount=1")
        self.assertEqual([r[0] for r in list_rows(self.run_cli("list").stdout)], ["1", "2", "3", "4"])


if __name__ == "__main__":
    unittest.main()
