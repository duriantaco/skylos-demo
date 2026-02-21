from app.utils.formatters import format_date
from app.utils.formatters import format_money as fmt_money


def generate_report():
    # We use format_date
    print(format_date("2024-01-01"))

    # We do NOT use fmt_money.
    # But Vulture might see "format_money" in the import line
    # and mark the definition in formatters.py as used just because it was imported.
