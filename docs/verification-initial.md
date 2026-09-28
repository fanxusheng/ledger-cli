# 首轮验证记录（已修复的测试清理问题）

本文件保留首次运行的原始命令及输出。功能验收全部通过，但一项测试因测试代码未显式关闭 SQLite 连接而无法清理 Windows 临时文件。该问题已修复；完整重跑后的通过结果见 [verification.md](verification.md)。

运行时间：2026-09-28T20:38:19+08:00

Python：3.13.5

独立演示数据库：`demo_runs/acceptance_zluuk9hi/ledger.sqlite3`。每个命令均启动新进程并等待退出。

以下命令按 PowerShell 语法记录；输出为实际捕获的标准输出和标准错误。

```powershell
Set-Location C:\Users\PC\Desktop\1111
$env:PYTHONIOENCODING = 'utf-8'
```

## 1. 空数据查询及汇总

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/acceptance_zluuk9hi/ledger.sqlite3 list

暂无记录。

退出码：0
```

检查通过：空数据查询提示暂无记录

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/acceptance_zluuk9hi/ledger.sqlite3 summary

收入总额：0.00
支出总额：0.00
净收入：0.00

退出码：0
```

检查通过：空数据的三项汇总均为 0.00

## 2. 新增指定的三条记录

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/acceptance_zluuk9hi/ledger.sqlite3 add --date 2026-09-01 --type '收入' --category '工资' --amount 1000.00

新增成功，编号：1

退出码：0
```

检查通过：第 1 条记录新增成功

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/acceptance_zluuk9hi/ledger.sqlite3 add --date 2026-09-02 --type '支出' --category '餐饮' --amount 25.50 --note '午餐'

新增成功，编号：2

退出码：0
```

检查通过：第 2 条记录新增成功

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/acceptance_zluuk9hi/ledger.sqlite3 add --date 2026-09-02 --type '支出' --category '交通' --amount 10.00

新增成功，编号：3

退出码：0
```

检查通过：第 3 条记录新增成功

## 3. 完整字段、顺序和汇总

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/acceptance_zluuk9hi/ledger.sqlite3 list

编号 | 日期 | 类型 | 分类 | 金额 | 备注
1 | 2026-09-01 | 收入 | "工资" | 1000.00 | ""
2 | 2026-09-02 | 支出 | "餐饮" | 25.50 | "午餐"
3 | 2026-09-02 | 支出 | "交通" | 10.00 | ""

退出码：0
```

检查通过：三条记录的完整字段及日期、编号顺序正确

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/acceptance_zluuk9hi/ledger.sqlite3 summary

收入总额：1000.00
支出总额：35.50
净收入：964.50

退出码：0
```

检查通过：收入 1000.00，支出 35.50，净收入 964.50

## 4. 进程退出后再次启动

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/acceptance_zluuk9hi/ledger.sqlite3 list

编号 | 日期 | 类型 | 分类 | 金额 | 备注
1 | 2026-09-01 | 收入 | "工资" | 1000.00 | ""
2 | 2026-09-02 | 支出 | "餐饮" | 25.50 | "午餐"
3 | 2026-09-02 | 支出 | "交通" | 10.00 | ""

退出码：0
```

检查通过：上一次进程已退出；新进程仍能查询到三条记录

## 5. 四种非法新增，逐次检查数据不变

原始数据库 SHA-256：`3a7dbe17598781e50d244c51c1bda7474af19b8986bae825aec891e965d7de1c`

### 不存在的日期

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/acceptance_zluuk9hi/ledger.sqlite3 add --date=2026-02-30 '--type=支出' '--category=餐饮' --amount=1.00

输入错误：日期不存在：2026-02-30。

退出码：2
```

检查通过：不存在的日期被拒绝并给出明确提示，退出码为 2

检查通过：不存在的日期被拒绝后数据库 SHA-256 不变：3a7dbe17598781e50d244c51c1bda7474af19b8986bae825aec891e965d7de1c

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/acceptance_zluuk9hi/ledger.sqlite3 list

编号 | 日期 | 类型 | 分类 | 金额 | 备注
1 | 2026-09-01 | 收入 | "工资" | 1000.00 | ""
2 | 2026-09-02 | 支出 | "餐饮" | 25.50 | "午餐"
3 | 2026-09-02 | 支出 | "交通" | 10.00 | ""

退出码：0
```

检查通过：不存在的日期被拒绝后仍为原有三条完整记录

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/acceptance_zluuk9hi/ledger.sqlite3 summary

收入总额：1000.00
支出总额：35.50
净收入：964.50

退出码：0
```

检查通过：不存在的日期被拒绝后汇总不变

### 负数金额

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/acceptance_zluuk9hi/ledger.sqlite3 add --date=2026-09-03 '--type=支出' '--category=餐饮' --amount=-1.00

输入错误：金额必须大于零，最多两位小数（例如 10、10.5、10.50）。

退出码：2
```

检查通过：负数金额被拒绝并给出明确提示，退出码为 2

检查通过：负数金额被拒绝后数据库 SHA-256 不变：3a7dbe17598781e50d244c51c1bda7474af19b8986bae825aec891e965d7de1c

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/acceptance_zluuk9hi/ledger.sqlite3 list

编号 | 日期 | 类型 | 分类 | 金额 | 备注
1 | 2026-09-01 | 收入 | "工资" | 1000.00 | ""
2 | 2026-09-02 | 支出 | "餐饮" | 25.50 | "午餐"
3 | 2026-09-02 | 支出 | "交通" | 10.00 | ""

退出码：0
```

检查通过：负数金额被拒绝后仍为原有三条完整记录

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/acceptance_zluuk9hi/ledger.sqlite3 summary

收入总额：1000.00
支出总额：35.50
净收入：964.50

退出码：0
```

检查通过：负数金额被拒绝后汇总不变

### 超过两位小数

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/acceptance_zluuk9hi/ledger.sqlite3 add --date=2026-09-03 '--type=支出' '--category=餐饮' --amount=1.001

输入错误：金额必须大于零，最多两位小数（例如 10、10.5、10.50）。

退出码：2
```

检查通过：超过两位小数被拒绝并给出明确提示，退出码为 2

检查通过：超过两位小数被拒绝后数据库 SHA-256 不变：3a7dbe17598781e50d244c51c1bda7474af19b8986bae825aec891e965d7de1c

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/acceptance_zluuk9hi/ledger.sqlite3 list

编号 | 日期 | 类型 | 分类 | 金额 | 备注
1 | 2026-09-01 | 收入 | "工资" | 1000.00 | ""
2 | 2026-09-02 | 支出 | "餐饮" | 25.50 | "午餐"
3 | 2026-09-02 | 支出 | "交通" | 10.00 | ""

退出码：0
```

检查通过：超过两位小数被拒绝后仍为原有三条完整记录

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/acceptance_zluuk9hi/ledger.sqlite3 summary

收入总额：1000.00
支出总额：35.50
净收入：964.50

退出码：0
```

检查通过：超过两位小数被拒绝后汇总不变

### 空分类

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/acceptance_zluuk9hi/ledger.sqlite3 add --date=2026-09-03 '--type=支出' --category= --amount=1.00

输入错误：分类不能为空或仅包含空白字符。

退出码：2
```

检查通过：空分类被拒绝并给出明确提示，退出码为 2

检查通过：空分类被拒绝后数据库 SHA-256 不变：3a7dbe17598781e50d244c51c1bda7474af19b8986bae825aec891e965d7de1c

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/acceptance_zluuk9hi/ledger.sqlite3 list

编号 | 日期 | 类型 | 分类 | 金额 | 备注
1 | 2026-09-01 | 收入 | "工资" | 1000.00 | ""
2 | 2026-09-02 | 支出 | "餐饮" | 25.50 | "午餐"
3 | 2026-09-02 | 支出 | "交通" | 10.00 | ""

退出码：0
```

检查通过：空分类被拒绝后仍为原有三条完整记录

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/acceptance_zluuk9hi/ledger.sqlite3 summary

收入总额：1000.00
支出总额：35.50
净收入：964.50

退出码：0
```

检查通过：空分类被拒绝后汇总不变

## 6. 自动化测试

```powershell
PS> & D:\anaconda\python.exe -m unittest discover -s tests -v

test_bad_database_path_reports_error (test_ledger.CliTests.test_bad_database_path_reports_error) ... ok
test_corrupt_database_reports_error (test_ledger.CliTests.test_corrupt_database_reports_error) ... ok
test_each_rejection_preserves_database_bytes (test_ledger.CliTests.test_each_rejection_preserves_database_bytes) ... ok
test_empty_outputs (test_ledger.CliTests.test_empty_outputs) ... ok
test_invalid_input_does_not_create_database (test_ledger.CliTests.test_invalid_input_does_not_create_database) ... ok
test_missing_required_argument (test_ledger.CliTests.test_missing_required_argument) ... ok
test_process_restart_persistence_and_all_fields (test_ledger.CliTests.test_process_restart_persistence_and_all_fields) ... ok
test_special_characters_display_on_one_line (test_ledger.CliTests.test_special_characters_display_on_one_line) ... ok
test_database_constraint_rejects_nonpositive_amount (test_ledger.StorageTests.test_database_constraint_rejects_nonpositive_amount) ... ERROR
test_dates_then_ids_ordered_and_ids_unique (test_ledger.StorageTests.test_dates_then_ids_ordered_and_ids_unique) ... ok
test_empty_database (test_ledger.StorageTests.test_empty_database) ... ok
test_reopen_retains_all_fields (test_ledger.StorageTests.test_reopen_retains_all_fields) ... ok
test_required_summary (test_ledger.StorageTests.test_required_summary) ... ok
test_small_amounts_and_negative_net (test_ledger.StorageTests.test_small_amounts_and_negative_net) ... ok
test_special_text_roundtrip (test_ledger.StorageTests.test_special_text_roundtrip) ... ok
test_summary_beyond_single_sqlite_integer (test_ledger.StorageTests.test_summary_beyond_single_sqlite_integer) ... ok
test_amount_converted_exactly (test_ledger.ValidationTests.test_amount_converted_exactly) ... ok
test_amount_limit_and_long_input (test_ledger.ValidationTests.test_amount_limit_and_long_input) ... ok
test_category_trim_and_optional_note (test_ledger.ValidationTests.test_category_trim_and_optional_note) ... ok
test_empty_category (test_ledger.ValidationTests.test_empty_category) ... ok
test_impossible_dates (test_ledger.ValidationTests.test_impossible_dates) ... ok
test_invalid_amounts (test_ledger.ValidationTests.test_invalid_amounts) ... ok
test_invalid_type (test_ledger.ValidationTests.test_invalid_type) ... ok
test_money_format (test_ledger.ValidationTests.test_money_format) ... ok
test_real_leap_day (test_ledger.ValidationTests.test_real_leap_day) ... ok
test_strict_date_format (test_ledger.ValidationTests.test_strict_date_format) ... ok

======================================================================
ERROR: test_database_constraint_rejects_nonpositive_amount (test_ledger.StorageTests.test_database_constraint_rejects_nonpositive_amount)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "D:\anaconda\Lib\shutil.py", line 625, in _rmtree_unsafe
    os.unlink(fullname)
    ~~~~~~~~~^^^^^^^^^^
PermissionError: [WinError 32] 另一个程序正在使用此文件，进程无法访问。: 'C:\\Users\\PC\\AppData\\Local\\Temp\\tmpxo5ldbis\\nested\\账本.sqlite3'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "D:\anaconda\Lib\tempfile.py", line 954, in cleanup
    self._rmtree(self.name, ignore_errors=self._ignore_cleanup_errors)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\anaconda\Lib\tempfile.py", line 934, in _rmtree
    _shutil.rmtree(name, onexc=onexc)
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "D:\anaconda\Lib\shutil.py", line 790, in rmtree
    return _rmtree_unsafe(path, onexc)
  File "D:\anaconda\Lib\shutil.py", line 629, in _rmtree_unsafe
    onexc(os.unlink, fullname, err)
    ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\anaconda\Lib\tempfile.py", line 909, in onexc
    _os.unlink(path)
    ~~~~~~~~~~^^^^^^
PermissionError: [WinError 32] 另一个程序正在使用此文件，进程无法访问。: 'C:\\Users\\PC\\AppData\\Local\\Temp\\tmpxo5ldbis\\nested\\账本.sqlite3'

----------------------------------------------------------------------
Ran 26 tests in 2.341s

FAILED (errors=1)

退出码：1
```

验证失败：AssertionError: 预期退出码 0，实际 1
