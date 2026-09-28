import re
from datetime import date

from .models import NewRecord, RecordFilters, format_amount


# SQLite INTEGER 的最大值；汇总使用 Python 整数，不受此单笔上限影响。
MAX_CENTS = 2**63 - 1


def validate_date(date_text: str, label: str = "日期") -> str:
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", date_text):
        raise ValueError(f"{label}必须使用 YYYY-MM-DD 格式。")
    try:
        date.fromisoformat(date_text)
    except ValueError:
        raise ValueError(f"{label}不存在：{date_text}。") from None
    return date_text


def validate_kind(kind: str) -> str:
    if kind not in ("收入", "支出"):
        raise ValueError("类型必须为“收入”或“支出”。")
    return kind


def validate_category(category: str) -> str:
    category = category.strip()
    if not category:
        raise ValueError("分类不能为空或仅包含空白字符。")
    return category


def validate_filters(
    start_date: str | None = None, end_date: str | None = None,
    kind: str | None = None, category: str | None = None,
) -> RecordFilters:
    if start_date is not None:
        validate_date(start_date, "起始日期")
    if end_date is not None:
        validate_date(end_date, "结束日期")
    if start_date is not None and end_date is not None and start_date > end_date:
        raise ValueError("起始日期不得晚于结束日期。")
    if kind is not None:
        validate_kind(kind)
    if category is not None:
        category = validate_category(category)
    return RecordFilters(start_date, end_date, kind, category)


def validate_record(
    date_text: str, kind: str, category: str, amount_text: str, note: str = ""
) -> NewRecord:
    validate_date(date_text)
    validate_kind(kind)
    category = validate_category(category)

    if not re.fullmatch(r"[0-9]+(?:\.[0-9]{1,2})?", amount_text):
        raise ValueError("金额必须大于零，最多两位小数（例如 10、10.5、10.50）。")
    whole, _, fraction = amount_text.partition(".")
    # 先比较字符串长度，超长数字也能明确拒绝，避免 int() 的位数限制。
    digits = (whole + fraction.ljust(2, "0")).lstrip("0") or "0"
    maximum = str(MAX_CENTS)
    if len(digits) > len(maximum) or (
        len(digits) == len(maximum) and digits > maximum
    ):
        raise ValueError(f"单笔金额不能超过 {format_amount(MAX_CENTS)}。")
    cents = int(digits)
    if cents <= 0:
        raise ValueError("金额必须大于零。")

    return NewRecord(date_text, kind, category, cents, note)
