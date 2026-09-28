"""CSV 导出：保留原始文本，排他创建文件，不覆盖已有目标。"""
import csv
from collections.abc import Iterable
from pathlib import Path

from .models import Record, format_amount


CSV_HEADER = ("编号", "日期", "类型", "分类", "金额", "备注")


def export_csv(records: Iterable[Record], output: Path) -> int:
    output = Path(output).expanduser()
    count = 0
    try:
        # x 模式将存在性检查与创建合并为一次操作，避免检查后覆盖的竞态。
        with output.open("x", encoding="utf-8-sig", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(CSV_HEADER)
            for record in records:
                writer.writerow((record.id, record.date, record.kind, record.category,
                                 format_amount(record.amount_cents), record.note))
                count += 1
    except FileExistsError:
        raise OSError(f"导出失败：目标文件已存在，拒绝覆盖：{output}") from None
    except FileNotFoundError:
        raise OSError(f"导出失败：父目录不存在：{output.parent}") from None
    except OSError as exc:
        raise OSError(f"导出失败：无法写入目标文件 {output}：{exc}") from exc
    return count
