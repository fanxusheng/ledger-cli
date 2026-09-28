"""第二阶段独立验收；保留数据库、CSV 及完整的实际命令输出。"""
import codecs
import csv
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from verify_demo import ps_quote


ROOT = Path(__file__).resolve().parent.parent
HEADER = ["编号", "日期", "类型", "分类", "金额", "备注"]
ZERO = "收入总额：0.00\n支出总额：0.00\n净收入：0.00\n"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode_list(output):
    rows = []
    for line in output.splitlines()[1:]:
        number, day, kind, category, amount, note = line.split(" | ")
        rows.append([number, day, kind, json.loads(category), amount, json.loads(note)])
    return rows


def main():
    # 在创建本轮数据前记录已有账本，只读计算哈希，绝不作为写入目标。
    originals = {path: sha256(path) for path in ROOT.rglob("*.sqlite3")}
    demo_root = ROOT / "demo_runs"
    demo_root.mkdir(exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix="stage2_", dir=demo_root))
    database = directory / "ledger.sqlite3"
    report = ROOT / "docs" / "verification-stage2.md"
    report.parent.mkdir(exist_ok=True)
    log = [
        "# 第二阶段实际验证记录\n",
        f"运行时间：{datetime.now().astimezone().isoformat(timespec='seconds')}\n",
        f"Python：{sys.version.split()[0]}；平台：{sys.platform}\n",
        f"独立验收目录：`{directory.relative_to(ROOT).as_posix()}`\n",
        "下列命令以 PowerShell 语法记录，每条 Python 命令均实际启动独立进程，捕获输出和退出码。\n",
        f"```powershell\nSet-Location {ps_quote(str(ROOT))}\n$env:PYTHONIOENCODING = 'utf-8'\n```\n",
    ]

    def emit(text):
        print(text, flush=True)
        log.append(text + "\n")

    def check(condition, message):
        if not condition:
            raise AssertionError(message)
        emit(f"检查通过：{message}")

    def relative(path):
        return path.relative_to(ROOT).as_posix()

    def run(arguments, expected_code=0):
        command = [sys.executable, *map(str, arguments)]
        emit("```powershell\nPS> & " + " ".join(ps_quote(arg) for arg in command))
        result = subprocess.run(
            command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            encoding="utf-8", text=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        if result.stdout:
            emit(result.stdout.rstrip("\n"))
        emit(f"退出码：{result.returncode}\n```")
        if result.returncode != expected_code:
            raise AssertionError(f"预期退出码 {expected_code}，实际 {result.returncode}")
        return result.stdout

    def ledger(*arguments, db=database, expected_code=0):
        before = sha256(db) if db.exists() else None
        result = run(["-m", "ledger", "--db", relative(db), *arguments], expected_code)
        if arguments[0] != "add" and before is not None:
            check(sha256(db) == before, "本次查询/汇总/导出后账本 SHA-256 不变")
        return result

    def inspect_csv(path, expected_rows):
        check(path.read_bytes().startswith(codecs.BOM_UTF8), f"{path.name} 带 UTF-8 BOM")
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.reader(stream))
        emit(f"实际 CSV 解析结果（JSON 中的 \\n 表示字段内换行）：\n```json\n{json.dumps(rows, ensure_ascii=False, indent=2)}\n```")
        check(rows == [HEADER, *expected_rows], f"{path.name} 表头、顺序及全部字段与预期/list 一致")

    try:
        emit("## 1. 保留已有数据，验证原有命令")
        for path, digest in originals.items():
            emit(f"已有账本：`{relative(path)}`，SHA-256：`{digest}`")
        check(ledger("list") == "暂无记录。\n", "原有空账本查询行为保持不变")
        check(ledger("summary") == ZERO, "原有空账本汇总保持不变")
        initial_rows = [
            ["1", "2026-09-01", "收入", "工资", "1000.00", ""],
            ["2", "2026-09-02", "支出", "餐饮", "25.50", "午餐"],
            ["3", "2026-09-02", "支出", "交通", "10.00", ""],
        ]
        for number, day, kind, category, amount, note in initial_rows:
            check(ledger("add", f"--date={day}", f"--type={kind}", f"--category={category}",
                         f"--amount={amount}", f"--note={note}") == f"新增成功，编号：{number}\n",
                  f"原有 add 新增第 {number} 条指定演示记录")
        before_hash = sha256(database)
        emit(f"三条演示记录建立后的 SHA-256：`{before_hash}`")
        check(decode_list(ledger("list")) == initial_rows, "原有无筛选 list 及跨进程持久化可用")
        check(ledger("summary") == "收入总额：1000.00\n支出总额：35.50\n净收入：964.50\n",
              "原有无筛选 summary 结果正确")

        emit("## 2. 包含日期两端、单边日期、组合筛选")
        interval = ["--start-date=2026-09-01", "--end-date=2026-09-02"]
        check(decode_list(ledger("list", *interval)) == initial_rows, "起始日和结束日均包含在范围内")
        check(decode_list(ledger("list", "--end-date=2026-09-01")) == initial_rows[:1], "只传结束日期")
        check(decode_list(ledger("list", "--start-date=2026-09-02")) == initial_rows[1:], "只传起始日期")
        expenses = ["--start-date=2026-09-02", "--end-date=2026-09-02", "--type=支出"]
        expense_rows = decode_list(ledger("list", *expenses))
        check(expense_rows == initial_rows[1:], "2026-09-02 支出筛选得到两条完整记录，编号升序")
        check(ledger("summary", *expenses) == "收入总额：0.00\n支出总额：35.50\n净收入：-35.50\n",
              "指定筛选汇总为 0.00 / 35.50 / -35.50")
        combined = [*expenses, "--category=餐饮"]
        check(decode_list(ledger("list", *combined)) == initial_rows[1:2], "四项条件同时满足，仅匹配餐饮")
        check(ledger("summary", *combined) == "收入总额：0.00\n支出总额：25.50\n净收入：-25.50\n",
              "四项组合筛选汇总一致")
        check(ledger("list", "--category=餐") == "无匹配记录。\n", "分类按完整名称匹配")

        emit("## 3. CSV 与同条件 list 一致")
        for filename, arguments, rows in (
            ("expenses.csv", expenses, expense_rows),
            ("combined.csv", combined, initial_rows[1:2]),
            ("all.csv", [], initial_rows),
        ):
            output = directory / filename
            ledger("export", "--output", relative(output), *arguments)
            inspect_csv(output, rows)

        emit("## 4. 没有匹配记录")
        no_match = ["--category=不存在"]
        check(ledger("list", *no_match) == "无匹配记录。\n", "无匹配记录时提示明确")
        check(ledger("summary", *no_match) == ZERO, "无匹配记录汇总全为 0.00")
        empty_output = directory / "empty.csv"
        ledger("export", "--output", relative(empty_output), *no_match)
        inspect_csv(empty_output, [])

        emit("## 5. 三个命令使用相同的非法参数校验")
        invalid_output = directory / "invalid.csv"
        invalid_cases = [
            (["--start-date=2026-02-30"], "起始日期不存在"),
            (["--end-date=2026-02-30"], "结束日期不存在"),
            (["--start-date=2026-9-01"], "YYYY-MM-DD"),
            (["--start-date=2026-09-03", "--end-date=2026-09-02"], "起始日期不得晚于结束日期"),
            (["--type=转账"], "类型必须"),
            (["--category="], "分类不能为空"),
            (["--category=   "], "分类不能为空"),
        ]
        for command in ("list", "summary", "export"):
            for arguments, message in invalid_cases:
                base = [command] + (["--output", relative(invalid_output)] if command == "export" else [])
                check(message in ledger(*base, *arguments, expected_code=2), f"{command} 拒绝非法筛选并提示：{message}")
                check(not invalid_output.exists(), "非法筛选没有生成导出文件")

        emit("## 6. 拒绝覆盖及导出路径错误")
        existing = directory / "expenses.csv"
        original_bytes = existing.read_bytes()
        check("已存在，拒绝覆盖" in ledger("export", "--output", relative(existing), expected_code=1), "已有目标明确拒绝覆盖")
        check(existing.read_bytes() == original_bytes, f"已有 CSV 内容逐字节不变，SHA-256：{sha256(existing)}")
        missing_parent = directory / "missing" / "out.csv"
        check("父目录不存在" in ledger("export", "--output", relative(missing_parent), expected_code=1), "父目录不存在时返回非零退出码")
        check(not missing_parent.parent.exists(), "不自动创建导出父目录")
        check("导出失败" in ledger("export", "--output", relative(directory), expected_code=1), "目录不能作为 CSV 文件写入，返回非零退出码")
        check("不能与账本文件相同" in ledger("export", "--output", relative(database), expected_code=1), "禁止将 CSV 写入账本自身")

        emit("## 7. 独立特殊字符数据集，CSV 无损往返及排序")
        special_db = directory / "special.sqlite3"
        category = '礼物,"朋友"\n回礼'
        note = '朋友,说"谢谢"\n第二行'
        for day, current_category, amount, current_note in (
            ("2026-09-04", category, "1.20", note),
            ("2026-09-03", category, "2.30", "较早记录"),
            ("2026-09-03", "礼物", "9.00", "完整分类名称不同"),
        ):
            ledger("add", f"--date={day}", "--type=支出", f"--category={current_category}",
                   f"--amount={amount}", f"--note={current_note}", db=special_db)
        special_hash = sha256(special_db)
        special_filter = [f"--category={category}"]
        special_rows = decode_list(ledger("list", *special_filter, db=special_db))
        check(special_rows == [
            ["2", "2026-09-03", "支出", category, "2.30", "较早记录"],
            ["1", "2026-09-04", "支出", category, "1.20", note],
        ], "特殊分类完整匹配，乱序插入后仍按日期排序")
        special_csv = directory / "special.csv"
        ledger("export", "--output", relative(special_csv), *special_filter, db=special_db)
        inspect_csv(special_csv, special_rows)
        check(sha256(special_db) == special_hash, "特殊字符账本在筛选导出后保持不变")

        emit("## 8. 完整回归测试及最终数据保护检查")
        run(["-m", "unittest", "discover", "-s", "tests", "-v"])
        emit("权限不足异常由测试模拟 PermissionError 验证；真实文件系统另验证了父目录缺失、目录目标和已有文件。")
        check(sha256(database) == before_hash, f"三条演示记录账本在全部筛选和导出前后 SHA-256 不变：{before_hash}")
        check(decode_list(ledger("list")) == initial_rows, "最终仍为原有三条完整演示记录")
        for path, digest in originals.items():
            check(path.exists() and sha256(path) == digest, f"已有账本未改变：{relative(path)}，SHA-256：{digest}")
        emit("第二阶段全部验收检查及完整回归测试通过。")
        return 0
    except Exception as exc:
        emit(f"验证失败：{type(exc).__name__}: {exc}")
        return 1
    finally:
        report.write_text("\n".join(log), encoding="utf-8", newline="\n")
        print(f"验证报告：{report}", flush=True)
        print(f"独立验收目录：{directory}", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
