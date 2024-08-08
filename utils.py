def format_currency(value):
  try:
    value = float(value)
    if value >= 1_000_000_000:
      truncated_value = value / 1_000_000_000
      return f"{truncated_value:.2f}B ISK"
    elif value >= 1_000_000:
      truncated_value = value / 1_000_000
      return f"{truncated_value:.2f}M ISK"
    else:
      return f"{value:,.2f} ISK"
  except (ValueError, TypeError):
    return 'N/A'