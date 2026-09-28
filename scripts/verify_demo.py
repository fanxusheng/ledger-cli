"""使用独立数据库运行验收并保存真实命令、输出及检查结果。"""
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from datetime import datetime


ROOT = Path(__file__).resolve().parent.parent


def ps_quote(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_./:\\=-]+", value):
        return value
    return "'" + value.replace("'", "''") + "'"


def main() -> int:
    demo_root = ROOT / "demo_runs"
    demo_root.mkdir(exist_ok=True)
    demo_dir = Path(tempfile.mkdtemp(prefix="acceptance_", dir=demo_root))
    database = demo_dir / "ledger.sqlite3"
    db_arg = database.relative_to(ROOT).as_posix()
    report = ROOT / "docs" / "verification.md"
    report.parent.mkdir(exist_ok=True)
    log = [
        "# 实际验证记录\n",
        f"运行时间：{datetime.now().astimezone().isoformat(timespec='seconds')}\n",
        f"Python：{sys.version.split()[0]}\n",
        f"独立演示数据库：`{db_arg}`。每个命令均启动新进程并等待退出。\n",
        "以下命令按 PowerShell 语法记录；输出为实际捕获的标准输出和标准错误。\n",
        f"```powershell\nSet-Location {ps_quote(str(ROOT))}\n$env:PYTHONIOENCODING = 'utf-8'\n```\n",
    ]

    def emit(value):
        print(value, flush=True)
        log.append(value + "\n")

    def check(condition, message):
        if not condition:
            raise AssertionError(message)
        emit(f"检查通过：{message}")

    def run(arguments, expected_code=0):
        command = [sys.executable, *arguments]
        emit("```powershell\nPS> & " + " ".join(ps_quote(arg) for arg in command))
        result = subprocess.run(
            command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        if result.stdout:
            emit(result.stdout.rstrip("\n"))
        emit(f"退出码：{result.returncode}\n```")
        if result.returncode != expected_code:
            raise AssertionError(f"预期退出码 {expected_code}，实际 {result.returncode}")
        return result.stdout

    def ledger(*args, expected_code=0):
        return run(["-m", "ledger", "--db", db_arg, *args], expected_code)

    def fingerprint():
        return hashlib.sha256(database.read_bytes()).hexdigest()

    try:
        emit("## 1. 空数据查询及汇总")
        check(ledger("list") == "暂无记录。\n", "空数据查询提示暂无记录")
        check(ledger("summary") == "收入总额：0.00\n支出总额：0.00\n净收入：0.00\n", "空数据的三项汇总均为 0.00")

        emit("## 2. 新增指定的三条记录")
        entries = [
            ["add", "--date", "2026-09-01", "--type", "收入", "--category", "工资", "--amount", "1000.00"],
            ["add", "--date", "2026-09-02", "--type", "支出", "--category", "餐饮", "--amount", "25.50", "--note", "午餐"],
            ["add", "--date", "2026-09-02", "--type", "支出", "--category", "交通", "--amount", "10.00"],
        ]
        for index, entry in enumerate(entries, 1):
            check(ledger(*entry) == f"新增成功，编号：{index}\n", f"第 {index} 条记录新增成功")

        expected_list = (
            '编号 | 日期 | 类型 | 分类 | 金额 | 备注\n'
            '1 | 2026-09-01 | 收入 | "工资" | 1000.00 | ""\n'
            '2 | 2026-09-02 | 支出 | "餐饮" | 25.50 | "午餐"\n'
            '3 | 2026-09-02 | 支出 | "交通" | 10.00 | ""\n'
        )
        expected_summary = "收入总额：1000.00\n支出总额：35.50\n净收入：964.50\n"
        emit("## 3. 完整字段、顺序和汇总")
        check(ledger("list") == expected_list, "三条记录的完整字段及日期、编号顺序正确")
        check(ledger("summary") == expected_summary, "收入 1000.00，支出 35.50，净收入 964.50")

        emit("## 4. 进程退出后再次启动")
        check(ledger("list") == expected_list, "上一次进程已退出；新进程仍能查询到三条记录")

        emit("## 5. 四种非法新增，逐次检查数据不变")
        before_hash = fingerprint()
        emit(f"原始数据库 SHA-256：`{before_hash}`")
        invalid_cases = [
            ("不存在的日期", ["--date=2026-02-30", "--type=支出", "--category=餐饮", "--amount=1.00"], "日期不存在"),
            ("负数金额", ["--date=2026-09-03", "--type=支出", "--category=餐饮", "--amount=-1.00"], "金额必须大于零"),
            ("超过两位小数", ["--date=2026-09-03", "--type=支出", "--category=餐饮", "--amount=1.001"], "最多两位小数"),
            ("空分类", ["--date=2026-09-03", "--type=支出", "--category=", "--amount=1.00"], "分类不能为空"),
        ]
        for label, arguments, error_text in invalid_cases:
            emit(f"### {label}")
            output = ledger("add", *arguments, expected_code=2)
            check(error_text in output, f"{label}被拒绝并给出明确提示，退出码为 2")
            check(fingerprint() == before_hash, f"{label}被拒绝后数据库 SHA-256 不变：{before_hash}")
            check(ledger("list") == expected_list, f"{label}被拒绝后仍为原有三条完整记录")
            check(ledger("summary") == expected_summary, f"{label}被拒绝后汇总不变")

        emit("## 6. 自动化测试")
        run(["-m", "unittest", "discover", "-s", "tests", "-v"])
        emit("全部验收项目及自动化测试通过。")
        return 0
    except Exception as exc:
        emit(f"验证失败：{type(exc).__name__}: {exc}")
        return 1
    finally:
        report.write_text("\n".join(log), encoding="utf-8")
        print(f"验证报告：{report}", flush=True)
        print(f"演示数据库：{database}", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
