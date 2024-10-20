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
def log_time(start_time, killmail_id=None):
  end_time = time.time()
  elapsed_time = end_time - start_time
  minutes = int(elapsed_time // 60)
  seconds = int(elapsed_time % 60)
  if killmail_id:
    print(f"{killmail_id}:Completed in: {minutes:02d}:{seconds:02d}")
  else:
    print(f"Operation completed in: {minutes:02d}:{seconds:02d}")

def get_current_time():
  return time.time()