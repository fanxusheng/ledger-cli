# 第二阶段实际验证记录

运行时间：2026-09-28T21:00:03+08:00

Python：3.13.5；平台：win32

独立验收目录：`demo_runs/stage2__fr1i1ri`

下列命令以 PowerShell 语法记录，每条 Python 命令均实际启动独立进程，捕获输出和退出码。

```powershell
Set-Location C:\Users\PC\Desktop\1111
$env:PYTHONIOENCODING = 'utf-8'
```

## 1. 保留已有数据，验证原有命令

已有账本：`demo_runs/acceptance_wmf7lppa/ledger.sqlite3`，SHA-256：`3a7dbe17598781e50d244c51c1bda7474af19b8986bae825aec891e965d7de1c`

已有账本：`demo_runs/acceptance_z1zhzfkh/ledger.sqlite3`，SHA-256：`3a7dbe17598781e50d244c51c1bda7474af19b8986bae825aec891e965d7de1c`

已有账本：`demo_runs/acceptance_zluuk9hi/ledger.sqlite3`，SHA-256：`3a7dbe17598781e50d244c51c1bda7474af19b8986bae825aec891e965d7de1c`

已有账本：`demo_runs/stage2_3y7knivw/ledger.sqlite3`，SHA-256：`3a7dbe17598781e50d244c51c1bda7474af19b8986bae825aec891e965d7de1c`

已有账本：`demo_runs/stage2_3y7knivw/special.sqlite3`，SHA-256：`f2c0eb876640406f7a823801208a14cad83f71f56f19dd62b85b420f43fa7eb1`

已有账本：`demo_runs/stage2_fnu56f_f/ledger.sqlite3`，SHA-256：`3a7dbe17598781e50d244c51c1bda7474af19b8986bae825aec891e965d7de1c`

已有账本：`demo_runs/stage2_fnu56f_f/special.sqlite3`，SHA-256：`f2c0eb876640406f7a823801208a14cad83f71f56f19dd62b85b420f43fa7eb1`

已有账本：`demo_runs/stage2_un5inxaw/ledger.sqlite3`，SHA-256：`3a7dbe17598781e50d244c51c1bda7474af19b8986bae825aec891e965d7de1c`

已有账本：`demo_runs/stage2_un5inxaw/special.sqlite3`，SHA-256：`f2c0eb876640406f7a823801208a14cad83f71f56f19dd62b85b420f43fa7eb1`

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 list

暂无记录。

退出码：0
```

检查通过：原有空账本查询行为保持不变

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 summary

收入总额：0.00
支出总额：0.00
净收入：0.00

退出码：0
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：原有空账本汇总保持不变

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 add --date=2026-09-01 '--type=收入' '--category=工资' --amount=1000.00 --note=

新增成功，编号：1

退出码：0
```

检查通过：原有 add 新增第 1 条指定演示记录

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 add --date=2026-09-02 '--type=支出' '--category=餐饮' --amount=25.50 '--note=午餐'

新增成功，编号：2

退出码：0
```

检查通过：原有 add 新增第 2 条指定演示记录

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 add --date=2026-09-02 '--type=支出' '--category=交通' --amount=10.00 --note=

新增成功，编号：3

退出码：0
```

检查通过：原有 add 新增第 3 条指定演示记录

三条演示记录建立后的 SHA-256：`3a7dbe17598781e50d244c51c1bda7474af19b8986bae825aec891e965d7de1c`

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 list

编号 | 日期 | 类型 | 分类 | 金额 | 备注
1 | 2026-09-01 | 收入 | "工资" | 1000.00 | ""
2 | 2026-09-02 | 支出 | "餐饮" | 25.50 | "午餐"
3 | 2026-09-02 | 支出 | "交通" | 10.00 | ""

退出码：0
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：原有无筛选 list 及跨进程持久化可用

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 summary

收入总额：1000.00
支出总额：35.50
净收入：964.50

退出码：0
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：原有无筛选 summary 结果正确

## 2. 包含日期两端、单边日期、组合筛选

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 list --start-date=2026-09-01 --end-date=2026-09-02

编号 | 日期 | 类型 | 分类 | 金额 | 备注
1 | 2026-09-01 | 收入 | "工资" | 1000.00 | ""
2 | 2026-09-02 | 支出 | "餐饮" | 25.50 | "午餐"
3 | 2026-09-02 | 支出 | "交通" | 10.00 | ""

退出码：0
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：起始日和结束日均包含在范围内

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 list --end-date=2026-09-01

编号 | 日期 | 类型 | 分类 | 金额 | 备注
1 | 2026-09-01 | 收入 | "工资" | 1000.00 | ""

退出码：0
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：只传结束日期

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 list --start-date=2026-09-02

编号 | 日期 | 类型 | 分类 | 金额 | 备注
2 | 2026-09-02 | 支出 | "餐饮" | 25.50 | "午餐"
3 | 2026-09-02 | 支出 | "交通" | 10.00 | ""

退出码：0
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：只传起始日期

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 list --start-date=2026-09-02 --end-date=2026-09-02 '--type=支出'

编号 | 日期 | 类型 | 分类 | 金额 | 备注
2 | 2026-09-02 | 支出 | "餐饮" | 25.50 | "午餐"
3 | 2026-09-02 | 支出 | "交通" | 10.00 | ""

退出码：0
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：2026-09-02 支出筛选得到两条完整记录，编号升序

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 summary --start-date=2026-09-02 --end-date=2026-09-02 '--type=支出'

收入总额：0.00
支出总额：35.50
净收入：-35.50

退出码：0
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：指定筛选汇总为 0.00 / 35.50 / -35.50

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 list --start-date=2026-09-02 --end-date=2026-09-02 '--type=支出' '--category=餐饮'

编号 | 日期 | 类型 | 分类 | 金额 | 备注
2 | 2026-09-02 | 支出 | "餐饮" | 25.50 | "午餐"

退出码：0
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：四项条件同时满足，仅匹配餐饮

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 summary --start-date=2026-09-02 --end-date=2026-09-02 '--type=支出' '--category=餐饮'

收入总额：0.00
支出总额：25.50
净收入：-25.50

退出码：0
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：四项组合筛选汇总一致

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 list '--category=餐'

无匹配记录。

退出码：0
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：分类按完整名称匹配

## 3. CSV 与同条件 list 一致

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 export --output demo_runs/stage2__fr1i1ri/expenses.csv --start-date=2026-09-02 --end-date=2026-09-02 '--type=支出'

导出成功：2 条记录，文件：demo_runs\stage2__fr1i1ri\expenses.csv

退出码：0
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：expenses.csv 带 UTF-8 BOM

实际 CSV 解析结果（JSON 中的 \n 表示字段内换行）：
```json
[
  [
    "编号",
    "日期",
    "类型",
    "分类",
    "金额",
    "备注"
  ],
  [
    "2",
    "2026-09-02",
    "支出",
    "餐饮",
    "25.50",
    "午餐"
  ],
  [
    "3",
    "2026-09-02",
    "支出",
    "交通",
    "10.00",
    ""
  ]
]
```

检查通过：expenses.csv 表头、顺序及全部字段与预期/list 一致

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 export --output demo_runs/stage2__fr1i1ri/combined.csv --start-date=2026-09-02 --end-date=2026-09-02 '--type=支出' '--category=餐饮'

导出成功：1 条记录，文件：demo_runs\stage2__fr1i1ri\combined.csv

退出码：0
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：combined.csv 带 UTF-8 BOM

实际 CSV 解析结果（JSON 中的 \n 表示字段内换行）：
```json
[
  [
    "编号",
    "日期",
    "类型",
    "分类",
    "金额",
    "备注"
  ],
  [
    "2",
    "2026-09-02",
    "支出",
    "餐饮",
    "25.50",
    "午餐"
  ]
]
```

检查通过：combined.csv 表头、顺序及全部字段与预期/list 一致

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 export --output demo_runs/stage2__fr1i1ri/all.csv

导出成功：3 条记录，文件：demo_runs\stage2__fr1i1ri\all.csv

退出码：0
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：all.csv 带 UTF-8 BOM

实际 CSV 解析结果（JSON 中的 \n 表示字段内换行）：
```json
[
  [
    "编号",
    "日期",
    "类型",
    "分类",
    "金额",
    "备注"
  ],
  [
    "1",
    "2026-09-01",
    "收入",
    "工资",
    "1000.00",
    ""
  ],
  [
    "2",
    "2026-09-02",
    "支出",
    "餐饮",
    "25.50",
    "午餐"
  ],
  [
    "3",
    "2026-09-02",
    "支出",
    "交通",
    "10.00",
    ""
  ]
]
```

检查通过：all.csv 表头、顺序及全部字段与预期/list 一致

## 4. 没有匹配记录

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 list '--category=不存在'

无匹配记录。

退出码：0
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：无匹配记录时提示明确

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 summary '--category=不存在'

收入总额：0.00
支出总额：0.00
净收入：0.00

退出码：0
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：无匹配记录汇总全为 0.00

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 export --output demo_runs/stage2__fr1i1ri/empty.csv '--category=不存在'

导出成功：0 条记录，文件：demo_runs\stage2__fr1i1ri\empty.csv

退出码：0
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：empty.csv 带 UTF-8 BOM

实际 CSV 解析结果（JSON 中的 \n 表示字段内换行）：
```json
[
  [
    "编号",
    "日期",
    "类型",
    "分类",
    "金额",
    "备注"
  ]
]
```

检查通过：empty.csv 表头、顺序及全部字段与预期/list 一致

## 5. 三个命令使用相同的非法参数校验

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 list --start-date=2026-02-30

输入错误：起始日期不存在：2026-02-30。

退出码：2
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：list 拒绝非法筛选并提示：起始日期不存在

检查通过：非法筛选没有生成导出文件

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 list --end-date=2026-02-30

输入错误：结束日期不存在：2026-02-30。

退出码：2
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：list 拒绝非法筛选并提示：结束日期不存在

检查通过：非法筛选没有生成导出文件

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 list --start-date=2026-9-01

输入错误：起始日期必须使用 YYYY-MM-DD 格式。

退出码：2
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：list 拒绝非法筛选并提示：YYYY-MM-DD

检查通过：非法筛选没有生成导出文件

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 list --start-date=2026-09-03 --end-date=2026-09-02

输入错误：起始日期不得晚于结束日期。

退出码：2
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：list 拒绝非法筛选并提示：起始日期不得晚于结束日期

检查通过：非法筛选没有生成导出文件

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 list '--type=转账'

输入错误：类型必须为“收入”或“支出”。

退出码：2
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：list 拒绝非法筛选并提示：类型必须

检查通过：非法筛选没有生成导出文件

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 list --category=

输入错误：分类不能为空或仅包含空白字符。

退出码：2
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：list 拒绝非法筛选并提示：分类不能为空

检查通过：非法筛选没有生成导出文件

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 list '--category=   '

输入错误：分类不能为空或仅包含空白字符。

退出码：2
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：list 拒绝非法筛选并提示：分类不能为空

检查通过：非法筛选没有生成导出文件

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 summary --start-date=2026-02-30

输入错误：起始日期不存在：2026-02-30。

退出码：2
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：summary 拒绝非法筛选并提示：起始日期不存在

检查通过：非法筛选没有生成导出文件

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 summary --end-date=2026-02-30

输入错误：结束日期不存在：2026-02-30。

退出码：2
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：summary 拒绝非法筛选并提示：结束日期不存在

检查通过：非法筛选没有生成导出文件

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 summary --start-date=2026-9-01

输入错误：起始日期必须使用 YYYY-MM-DD 格式。

退出码：2
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：summary 拒绝非法筛选并提示：YYYY-MM-DD

检查通过：非法筛选没有生成导出文件

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 summary --start-date=2026-09-03 --end-date=2026-09-02

输入错误：起始日期不得晚于结束日期。

退出码：2
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：summary 拒绝非法筛选并提示：起始日期不得晚于结束日期

检查通过：非法筛选没有生成导出文件

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 summary '--type=转账'

输入错误：类型必须为“收入”或“支出”。

退出码：2
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：summary 拒绝非法筛选并提示：类型必须

检查通过：非法筛选没有生成导出文件

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 summary --category=

输入错误：分类不能为空或仅包含空白字符。

退出码：2
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：summary 拒绝非法筛选并提示：分类不能为空

检查通过：非法筛选没有生成导出文件

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 summary '--category=   '

输入错误：分类不能为空或仅包含空白字符。

退出码：2
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：summary 拒绝非法筛选并提示：分类不能为空

检查通过：非法筛选没有生成导出文件

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 export --output demo_runs/stage2__fr1i1ri/invalid.csv --start-date=2026-02-30

输入错误：起始日期不存在：2026-02-30。

退出码：2
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：export 拒绝非法筛选并提示：起始日期不存在

检查通过：非法筛选没有生成导出文件

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 export --output demo_runs/stage2__fr1i1ri/invalid.csv --end-date=2026-02-30

输入错误：结束日期不存在：2026-02-30。

退出码：2
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：export 拒绝非法筛选并提示：结束日期不存在

检查通过：非法筛选没有生成导出文件

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 export --output demo_runs/stage2__fr1i1ri/invalid.csv --start-date=2026-9-01

输入错误：起始日期必须使用 YYYY-MM-DD 格式。

退出码：2
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：export 拒绝非法筛选并提示：YYYY-MM-DD

检查通过：非法筛选没有生成导出文件

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 export --output demo_runs/stage2__fr1i1ri/invalid.csv --start-date=2026-09-03 --end-date=2026-09-02

输入错误：起始日期不得晚于结束日期。

退出码：2
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：export 拒绝非法筛选并提示：起始日期不得晚于结束日期

检查通过：非法筛选没有生成导出文件

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 export --output demo_runs/stage2__fr1i1ri/invalid.csv '--type=转账'

输入错误：类型必须为“收入”或“支出”。

退出码：2
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：export 拒绝非法筛选并提示：类型必须

检查通过：非法筛选没有生成导出文件

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 export --output demo_runs/stage2__fr1i1ri/invalid.csv --category=

输入错误：分类不能为空或仅包含空白字符。

退出码：2
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：export 拒绝非法筛选并提示：分类不能为空

检查通过：非法筛选没有生成导出文件

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 export --output demo_runs/stage2__fr1i1ri/invalid.csv '--category=   '

输入错误：分类不能为空或仅包含空白字符。

退出码：2
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：export 拒绝非法筛选并提示：分类不能为空

检查通过：非法筛选没有生成导出文件

## 6. 拒绝覆盖及导出路径错误

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 export --output demo_runs/stage2__fr1i1ri/expenses.csv

数据文件操作失败：导出失败：目标文件已存在，拒绝覆盖：demo_runs\stage2__fr1i1ri\expenses.csv

退出码：1
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：已有目标明确拒绝覆盖

检查通过：已有 CSV 内容逐字节不变，SHA-256：54150e64b44974bf9bb0a73368cb42358a9c74a8475f48af447f2ffeb8b27301

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 export --output demo_runs/stage2__fr1i1ri/missing/out.csv

数据文件操作失败：导出失败：父目录不存在：demo_runs\stage2__fr1i1ri\missing

退出码：1
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：父目录不存在时返回非零退出码

检查通过：不自动创建导出父目录

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 export --output demo_runs/stage2__fr1i1ri

数据文件操作失败：导出失败：无法写入目标文件 demo_runs\stage2__fr1i1ri：[Errno 13] Permission denied: 'demo_runs\\stage2__fr1i1ri'

退出码：1
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：目录不能作为 CSV 文件写入，返回非零退出码

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 export --output demo_runs/stage2__fr1i1ri/ledger.sqlite3

数据文件操作失败：导出失败：导出目标不能与账本文件相同。

退出码：1
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：禁止将 CSV 写入账本自身

## 7. 独立特殊字符数据集，CSV 无损往返及排序

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/special.sqlite3 add --date=2026-09-04 '--type=支出' '--category=礼物,"朋友"
回礼' --amount=1.20 '--note=朋友,说"谢谢"
第二行'

新增成功，编号：1

退出码：0
```

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/special.sqlite3 add --date=2026-09-03 '--type=支出' '--category=礼物,"朋友"
回礼' --amount=2.30 '--note=较早记录'

新增成功，编号：2

退出码：0
```

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/special.sqlite3 add --date=2026-09-03 '--type=支出' '--category=礼物' --amount=9.00 '--note=完整分类名称不同'

新增成功，编号：3

退出码：0
```

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/special.sqlite3 list '--category=礼物,"朋友"
回礼'

编号 | 日期 | 类型 | 分类 | 金额 | 备注
2 | 2026-09-03 | 支出 | "礼物,\"朋友\"\n回礼" | 2.30 | "较早记录"
1 | 2026-09-04 | 支出 | "礼物,\"朋友\"\n回礼" | 1.20 | "朋友,说\"谢谢\"\n第二行"

退出码：0
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：特殊分类完整匹配，乱序插入后仍按日期排序

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/special.sqlite3 export --output demo_runs/stage2__fr1i1ri/special.csv '--category=礼物,"朋友"
回礼'

导出成功：2 条记录，文件：demo_runs\stage2__fr1i1ri\special.csv

退出码：0
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：special.csv 带 UTF-8 BOM

实际 CSV 解析结果（JSON 中的 \n 表示字段内换行）：
```json
[
  [
    "编号",
    "日期",
    "类型",
    "分类",
    "金额",
    "备注"
  ],
  [
    "2",
    "2026-09-03",
    "支出",
    "礼物,\"朋友\"\n回礼",
    "2.30",
    "较早记录"
  ],
  [
    "1",
    "2026-09-04",
    "支出",
    "礼物,\"朋友\"\n回礼",
    "1.20",
    "朋友,说\"谢谢\"\n第二行"
  ]
]
```

检查通过：special.csv 表头、顺序及全部字段与预期/list 一致

检查通过：特殊字符账本在筛选导出后保持不变

## 8. 完整回归测试及最终数据保护检查

```powershell
PS> & D:\anaconda\python.exe -m unittest discover -s tests -v

test_all_four_conditions_are_anded (test_filters_export.FilterExportTests.test_all_four_conditions_are_anded) ... ok
test_category_exact_match_and_sql_parameters (test_filters_export.FilterExportTests.test_category_exact_match_and_sql_parameters) ... ok
test_csv_preserves_commas_quotes_crlf_and_newlines (test_filters_export.FilterExportTests.test_csv_preserves_commas_quotes_crlf_and_newlines) ... ok
test_every_command_rejects_bad_filters_without_side_effects (test_filters_export.FilterExportTests.test_every_command_rejects_bad_filters_without_side_effects) ... ok
test_existing_output_is_never_overwritten (test_filters_export.FilterExportTests.test_existing_output_is_never_overwritten) ... ok
test_export_bom_header_money_and_all_fields_match_list (test_filters_export.FilterExportTests.test_export_bom_header_money_and_all_fields_match_list) ... ok
test_filtered_order_is_date_then_id (test_filters_export.FilterExportTests.test_filtered_order_is_date_then_id) ... ok
test_interval_inclusive_and_one_sided_bounds (test_filters_export.FilterExportTests.test_interval_inclusive_and_one_sided_bounds) ... ok
test_missing_ledger_not_created_by_filters_or_export (test_filters_export.FilterExportTests.test_missing_ledger_not_created_by_filters_or_export) ... ok
test_missing_parent_and_directory_target_report_errors (test_filters_export.FilterExportTests.test_missing_parent_and_directory_target_report_errors) ... ok
test_no_matches_list_summary_and_header_only_export (test_filters_export.FilterExportTests.test_no_matches_list_summary_and_header_only_export) ... ok
test_output_cannot_be_database_even_when_missing (test_filters_export.FilterExportTests.test_output_cannot_be_database_even_when_missing) ... ok
test_permission_error_has_clear_message (test_filters_export.FilterExportTests.test_permission_error_has_clear_message) ... ok
test_read_operations_preserve_entire_database (test_filters_export.FilterExportTests.test_read_operations_preserve_entire_database) ... ok
test_required_output_parameter (test_filters_export.FilterExportTests.test_required_output_parameter) ... ok
test_same_day_expenses_and_summary (test_filters_export.FilterExportTests.test_same_day_expenses_and_summary) ... ok
test_unfiltered_legacy_behavior_and_add_still_work (test_filters_export.FilterExportTests.test_unfiltered_legacy_behavior_and_add_still_work) ... ok
test_both_dates_are_strict_and_real (test_filters_export.FilterValidationTests.test_both_dates_are_strict_and_real) ... ok
test_no_filters_distinct_from_explicit_empty (test_filters_export.FilterValidationTests.test_no_filters_distinct_from_explicit_empty) ... ok
test_reversed_dates_rejected (test_filters_export.FilterValidationTests.test_reversed_dates_rejected) ... ok
test_type_and_category_validation (test_filters_export.FilterValidationTests.test_type_and_category_validation) ... ok
test_bad_database_path_reports_error (test_ledger.CliTests.test_bad_database_path_reports_error) ... ok
test_corrupt_database_reports_error (test_ledger.CliTests.test_corrupt_database_reports_error) ... ok
test_each_rejection_preserves_database_bytes (test_ledger.CliTests.test_each_rejection_preserves_database_bytes) ... ok
test_empty_outputs (test_ledger.CliTests.test_empty_outputs) ... ok
test_invalid_input_does_not_create_database (test_ledger.CliTests.test_invalid_input_does_not_create_database) ... ok
test_missing_required_argument (test_ledger.CliTests.test_missing_required_argument) ... ok
test_process_restart_persistence_and_all_fields (test_ledger.CliTests.test_process_restart_persistence_and_all_fields) ... ok
test_special_characters_display_on_one_line (test_ledger.CliTests.test_special_characters_display_on_one_line) ... ok
test_database_constraint_rejects_nonpositive_amount (test_ledger.StorageTests.test_database_constraint_rejects_nonpositive_amount) ... ok
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

----------------------------------------------------------------------
Ran 47 tests in 12.702s

OK

退出码：0
```

权限不足异常由测试模拟 PermissionError 验证；真实文件系统另验证了父目录缺失、目录目标和已有文件。

检查通过：三条演示记录账本在全部筛选和导出前后 SHA-256 不变：3a7dbe17598781e50d244c51c1bda7474af19b8986bae825aec891e965d7de1c

```powershell
PS> & D:\anaconda\python.exe -m ledger --db demo_runs/stage2__fr1i1ri/ledger.sqlite3 list

编号 | 日期 | 类型 | 分类 | 金额 | 备注
1 | 2026-09-01 | 收入 | "工资" | 1000.00 | ""
2 | 2026-09-02 | 支出 | "餐饮" | 25.50 | "午餐"
3 | 2026-09-02 | 支出 | "交通" | 10.00 | ""

退出码：0
```

检查通过：本次查询/汇总/导出后账本 SHA-256 不变

检查通过：最终仍为原有三条完整演示记录

检查通过：已有账本未改变：demo_runs/acceptance_wmf7lppa/ledger.sqlite3，SHA-256：3a7dbe17598781e50d244c51c1bda7474af19b8986bae825aec891e965d7de1c

检查通过：已有账本未改变：demo_runs/acceptance_z1zhzfkh/ledger.sqlite3，SHA-256：3a7dbe17598781e50d244c51c1bda7474af19b8986bae825aec891e965d7de1c

检查通过：已有账本未改变：demo_runs/acceptance_zluuk9hi/ledger.sqlite3，SHA-256：3a7dbe17598781e50d244c51c1bda7474af19b8986bae825aec891e965d7de1c

检查通过：已有账本未改变：demo_runs/stage2_3y7knivw/ledger.sqlite3，SHA-256：3a7dbe17598781e50d244c51c1bda7474af19b8986bae825aec891e965d7de1c

检查通过：已有账本未改变：demo_runs/stage2_3y7knivw/special.sqlite3，SHA-256：f2c0eb876640406f7a823801208a14cad83f71f56f19dd62b85b420f43fa7eb1

检查通过：已有账本未改变：demo_runs/stage2_fnu56f_f/ledger.sqlite3，SHA-256：3a7dbe17598781e50d244c51c1bda7474af19b8986bae825aec891e965d7de1c

检查通过：已有账本未改变：demo_runs/stage2_fnu56f_f/special.sqlite3，SHA-256：f2c0eb876640406f7a823801208a14cad83f71f56f19dd62b85b420f43fa7eb1

检查通过：已有账本未改变：demo_runs/stage2_un5inxaw/ledger.sqlite3，SHA-256：3a7dbe17598781e50d244c51c1bda7474af19b8986bae825aec891e965d7de1c

检查通过：已有账本未改变：demo_runs/stage2_un5inxaw/special.sqlite3，SHA-256：f2c0eb876640406f7a823801208a14cad83f71f56f19dd62b85b420f43fa7eb1

第二阶段全部验收检查及完整回归测试通过。
