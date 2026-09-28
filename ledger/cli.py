import argparse
import json
import sqlite3
import sys
from pathlib import Path

from .exporter import export_csv
from .models import format_amount
from .storage import Ledger
from .validation import validate_filters, validate_record


DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "ledger.sqlite3"


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2, f"错误：{message}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = ArgumentParser(description="本地收支记账：新增记录、筛选历史、查看收支汇总、导出 CSV。")
    parser.add_argument(
        "--db", type=Path, default=DEFAULT_DB,
        help="数据库文件路径（放在子命令前；默认：项目目录/data/ledger.sqlite3）",
    )
    commands = parser.add_subparsers(dest="command", required=True, title="命令")
    add = commands.add_parser("add", help="新增一条收入或支出")
    add.add_argument("--date", required=True, help="真实日期，格式 YYYY-MM-DD")
    add.add_argument("--type", dest="kind", required=True, help="收入 或 支出")
    add.add_argument("--category", required=True, help="非空分类")
    add.add_argument("--amount", required=True, help="大于零，最多两位小数")
    add.add_argument("--note", default="", help="备注，可省略，默认为空")
    list_parser = commands.add_parser("list", help="按日期、编号升序显示记录，可筛选")
    summary_parser = commands.add_parser("summary", help="显示收入总额、支出总额、净收入，可筛选")
    export_parser = commands.add_parser("export", help="导出 CSV，可筛选，拒绝覆盖已有文件")
    export_parser.add_argument("--output", type=Path, required=True, help="CSV 文件路径（父目录必须存在）")
    for command_parser in (list_parser, summary_parser, export_parser):
        command_parser.add_argument("--start-date", help="起始日期 YYYY-MM-DD，包含当天")
        command_parser.add_argument("--end-date", help="结束日期 YYYY-MM-DD，包含当天")
        command_parser.add_argument("--type", dest="kind", help="收入 或 支出")
        command_parser.add_argument("--category", help="按完整分类名称匹配，不能为空")
    return parser


def display_text(value: str) -> str:
    # 引号区分空备注；转义换行及分隔符，确保每条记录占一行。
    return json.dumps(value, ensure_ascii=False).replace("|", r"\u007c")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        # 必须先完成校验，再接触数据库。非法新增不创建或修改数据文件。
        if args.command == "add":
            record = validate_record(args.date, args.kind, args.category, args.amount, args.note)
            record_id = Ledger(args.db).add(record)
            print(f"新增成功，编号：{record_id}")
            return 0

        filters = validate_filters(args.start_date, args.end_date, args.kind, args.category)
        ledger = Ledger(args.db)
        query_filters = filters if filters.active or args.command == "export" else None
        if args.command == "list":
            records = ledger.list_records(query_filters)
            if not records:
                print("无匹配记录。" if filters.active else "暂无记录。")
            else:
                print("编号 | 日期 | 类型 | 分类 | 金额 | 备注")
                for record in records:
                    print(
                        f"{record.id} | {record.date} | {record.kind} | "
                        f"{display_text(record.category)} | {format_amount(record.amount_cents)} | "
                        f"{display_text(record.note)}"
                    )
        elif args.command == "summary":
            summary = ledger.summarize(query_filters)
            print(f"收入总额：{format_amount(summary.income_cents)}")
            print(f"支出总额：{format_amount(summary.expense_cents)}")
            print(f"净收入：{format_amount(summary.net_cents)}")
        elif args.command == "export":
            if args.output.expanduser().resolve() == ledger.path.resolve():
                raise OSError("导出失败：导出目标不能与账本文件相同。")
            records = ledger.list_records(query_filters)
            count = export_csv(records, args.output)
            print(f"导出成功：{count} 条记录，文件：{args.output}")
        return 0
    except ValueError as exc:
        print(f"输入错误：{exc}", file=sys.stderr)
        return 2
    except (sqlite3.Error, OSError) as exc:
        print(f"数据文件操作失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
