# 本地收支记账工具

使用 Python 标准库的命令行程序，支持新增收入/支出、查询和筛选历史记录、收支汇总及 CSV 导出。数据保存到本地 SQLite 文件，每条新增在成功提示前提交事务；进程退出后数据仍然保留。无需安装第三方包或联网。第二阶段在原有模块上增量扩展，数据库表结构和原有 `add`、`list`、`summary`、全局 `--db` 用法保持兼容，无需迁移数据。

## 启动

需要 Python 3.10 或更新版本。在 Windows PowerShell 中进入本项目目录：

```powershell
Set-Location C:\Users\PC\Desktop\1111
python --version
python -m ledger --help
```

如果系统使用 `py` 启动器，也可以把示例中的 `python` 换成 `py -3`。这是子命令式工具，每执行一条命令启动一次，执行完自动退出。

## 使用

```powershell
# 新增收入：不传 --note 时备注为空
python -m ledger add --date 2026-09-01 --type 收入 --category 工资 --amount 1000.00

# 新增支出
python -m ledger add --date 2026-09-02 --type 支出 --category 餐饮 --amount 25.50 --note 午餐
python -m ledger add --date 2026-09-02 --type 支出 --category 交通 --amount 10.00

# 查询全部记录、查看汇总
python -m ledger list
python -m ledger summary

# 查看新增参数说明
python -m ledger add --help
```

有空格的分类或备注请加引号，例如 `--note "与朋友一起午餐"`。在 PowerShell 中传入空分类进行校验时使用 `--category=`，避免旧版 PowerShell 丢弃空字符串参数。

默认数据库为**项目目录下的 `data/ledger.sqlite3`**，首次合法新增或无筛选查询/汇总自动创建，不受执行时工作目录影响。可以指定独立数据文件，`--db` 必须放在子命令前；相对路径以执行命令时的工作目录为准：

```powershell
python -m ledger --db .\my-ledger.sqlite3 list
python -m ledger --db "C:\Users\PC\Desktop\个人账本.sqlite3" summary
```

此工具不会自动删除历史数据。关闭所有命令后，复制 `.sqlite3` 文件即可备份；使用 `--db` 指向该副本即可查询。

## 筛选查询和汇总

`list`、`summary`、`export` 共用以下可选参数，可单独使用或组合使用；每条记录必须同时满足全部条件。

| 参数 | 规则 |
| --- | --- |
| `--start-date YYYY-MM-DD` | 起始日期，包含当天；省略则不限制最早日期 |
| `--end-date YYYY-MM-DD` | 结束日期，包含当天；省略则不限制最晚日期 |
| `--type 收入` 或 `--type 支出` | 仅匹配所选类型 |
| `--category 分类名称` | 去除参数首尾空白后按完整名称匹配，不支持模糊匹配或通配符 |

日期必须真实存在且格式严格，起始日期不得晚于结束日期。非法类型、明确传入的空分类或纯空白分类均报错，退出码为 `2`。例如 `--category=` 和 `--category "   "` 都会被拒绝。

```powershell
# 日期区间，包含 9 月 1 日和 9 月 2 日
python -m ledger list --start-date 2026-09-01 --end-date 2026-09-02

# 同一天的全部支出
python -m ledger list --start-date 2026-09-02 --end-date 2026-09-02 --type 支出
python -m ledger summary --start-date 2026-09-02 --end-date 2026-09-02 --type 支出

# 四项条件组合，并使用独立账本
python -m ledger --db .\my-ledger.sqlite3 list --start-date 2026-09-01 --end-date 2026-09-30 --type 支出 --category 餐饮
```

对于第一阶段的三条演示记录，筛选 `2026-09-02` 的支出得到编号 `2`、`3` 两条记录，汇总为：

```text
收入总额：0.00
支出总额：35.50
净收入：-35.50
```

查询结果仍按日期、编号升序排列。有筛选条件但无匹配记录时，`list` 显示 `无匹配记录。`，`summary` 三项显示 `0.00`。不传筛选参数时保留第一阶段行为，包括空账本显示 `暂无记录。`。

## 导出 CSV

`export` 必须传入 `--output`。输出文件的父目录必须已存在，目标文件必须尚不存在；以下示例将文件写入当前目录：

```powershell
# 导出全部记录
python -m ledger export --output .\all-records.csv

# 导出同一天的支出；筛选参数和 list、summary 完全相同
python -m ledger export --output .\expenses-20260902.csv --start-date 2026-09-02 --end-date 2026-09-02 --type 支出

# 按完整分类名称筛选
python -m ledger export --output .\food.csv --category 餐饮
```

CSV 使用带 BOM 的 UTF-8 编码，字段依次为 `编号、日期、类型、分类、金额、备注`，包含表头，金额固定两位小数。记录及排序与相同条件的 `list` 一致。标准库 `csv` 负责逗号、双引号和换行的转义，字段保存原始文本；字段内换行可以使一条 CSV 记录跨越多行。无匹配记录时仍生成带 BOM、仅含表头的文件。

目标已存在时拒绝覆盖，原文件保持不变。父目录不存在、目标无法写入或导出路径与账本相同时会明确报错，退出码为 `1`；不会自动创建导出目录。重复导出请使用新的文件名。

对已有账本的查询、汇总和导出采用 SQLite 只读连接，不修改账本数据。筛选或导出不存在的账本时视为零条记录，不创建数据库或其父目录；无筛选 `list`、`summary` 保留第一阶段首次初始化空账本的行为。

## 数据与输入规则

- 每条记录包含自动分配且持久保存的唯一整数编号、日期、类型、分类、金额和备注。
- 日期必须严格为 `YYYY-MM-DD`，并且真实存在，包括闰年校验。
- 类型必须为 `收入` 或 `支出`。分类去掉首尾空白后不能为空；备注可以为空。
- 金额必须是大于零的十进制数，最多两位小数，例如 `10`、`10.5`、`10.50`；不接受负数、零、科学计数法、千位分隔符或多余小数位。
- 金额存为整数“分”，计算不使用浮点数。受 SQLite 整数范围限制，单笔上限为 `92233720368547758.07`；超限会明确拒绝。汇总使用 Python 整数，可以超过单笔上限。
- 查询按日期升序，再按编号升序，显示所有字段。分类和备注用双引号显示，空备注为 `""`；换行等字符转义，竖线显示为 `\u007c`，存储内容保持原样。
- 汇总显示收入总额、支出总额、净收入（收入减支出），统一保留两位小数；净收入可以为负。没有记录时查询显示 `暂无记录。`，三项汇总均为 `0.00`。
- 新增参数全部校验后才打开数据库；非法新增不创建或修改数据文件。成功退出码为 `0`，输入错误为 `2`，文件或数据库操作失败为 `1`。

## 实际验证与复现

第二阶段的实际命令、输出、退出码、CSV 解析结果和账本 SHA-256 检查见 [docs/verification-stage2.md](docs/verification-stage2.md)。运行第二阶段完整验收：

```powershell
python -X utf8 scripts/verify_stage2.py
```

本次在 Windows、Python 3.13.5 下实际运行通过：47 项测试（原有 26 项、新增 21 项）全部通过；指定日期支出汇总为 `0.00 / 35.50 / -35.50`。筛选、导出前后的账本哈希一致，运行前已有的三个账本也均未改变。

脚本每次新建 `demo_runs/stage2_随机后缀/`，其中保留三条指定演示记录的账本、单独的特殊字符账本，以及 `all.csv`、`expenses.csv`、`combined.csv`、`empty.csv`、`special.csv`。它验证日期两端、单边和组合筛选、三个命令的一致输入校验、无匹配记录、指定支出汇总、CSV 内容及特殊字符、拒绝覆盖、路径错误和原有行为，再运行全部新旧测试。每次读取/导出后检查账本哈希，最后检查运行前已有的所有 `.sqlite3` 文件未改变。报告更新到 `docs/verification-stage2.md`，不覆盖第一阶段报告。

新增测试还覆盖区间外记录排除、完整分类匹配、乱序插入后排序、CRLF 换行保存、数据库路径包含空格和特殊字符、未创建账本时的无副作用查询。权限不足异常使用模拟 `PermissionError` 验证；真实文件系统验证父目录缺失、目录目标和已有文件的拒绝行为。

第一阶段保留的实际命令、输出、退出码及检查结果见 [docs/verification.md](docs/verification.md)。各报告注明独立演示数据库路径，可用 `--db` 直接查询。验收不会往默认个人账本写入数据。

第一阶段在 Windows PowerShell、Python 3.13.5 下实际执行：六项功能验收通过，26 项自动化测试全部通过。首轮测试曾因测试代码未关闭 SQLite 连接而在 Windows 清理临时文件时失败，现已修复并完整重跑；原始输出也保存在 [docs/verification-initial.md](docs/verification-initial.md)。

运行第一阶段验收（也会执行当前全部自动化测试）：

```powershell
python -X utf8 scripts/verify_demo.py
```

脚本每次在 `demo_runs/acceptance_随机后缀/` 中创建一个全新的数据库，保留演示数据并更新 `docs/verification.md`。逐项断言空数据输出、指定三条记录的完整字段和排序、`1000.00 / 35.50 / 964.50` 汇总、进程退出重启后的持久化，以及四种非法新增。每次非法新增后检查数据库 SHA-256、完整查询和汇总均未改变。随后运行自动化测试，任何检查失败返回非零退出码并写入报告。

仅运行全部新旧测试，或仅运行原有测试：

```powershell
python -m unittest discover -s tests -v
python -m unittest discover -s tests -p test_ledger.py -v
```

自动化测试使用临时数据库，覆盖日期和金额边界、空白分类、输入失败时数据不变、乱序插入后的排序、唯一编号、跨进程持久化、精确金额与负净收入、特殊备注以及数据库错误提示。

如果终端重定向输出时中文乱码，可以先执行 `$env:PYTHONIOENCODING = 'utf-8'`；验证脚本已为子进程设置 UTF-8。

## 项目结构

```text
ledger/
  __main__.py       模块启动入口
  cli.py            命令行参数、输出与错误处理
  models.py         记录、筛选、汇总模型与金额显示
  validation.py     新增和筛选的共用校验
  storage.py        SQLite 持久化、筛选查询与汇总
  exporter.py       带 BOM 的 CSV 导出，排他创建文件
tests/
  test_ledger.py    标准库 unittest 自动化测试
  test_filters_export.py 第二阶段筛选、导出测试
scripts/
  verify_demo.py   可复现验收与真实输出报告生成
  verify_stage2.py 第二阶段验收，保留独立数据和导出文件
docs/
  verification.md  第一阶段实际验收报告
  verification-stage2.md 第二阶段实际验收报告
demo_runs/         独立演示数据库
data/              默认个人账本（首次使用时创建）
```
