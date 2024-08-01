import time
from datetime import datetime, timedelta

from zoneinfo import ZoneInfo

from trackstocks import TrackStocks

TIMEZONE = 'Asia/Kolkata'
OPEN_HOUR = 9
OPEN_HOUR_MIN = 15
CLOSE_HOUR = 15
CLOSE_HOUR_MIN = 30

track_stocks = TrackStocks()


def is_trading_time():
  today = datetime.now(tz=ZoneInfo(TIMEZONE))
  open_time = today.replace(hour=OPEN_HOUR, minute=OPEN_HOUR_MIN)
  close_time = today.replace(hour=CLOSE_HOUR, minute=CLOSE_HOUR_MIN)
  return open_time <= datetime.now(tz=ZoneInfo(TIMEZONE)) <= close_time


def get_secs_till_open():
  now = datetime.now(tz=ZoneInfo(TIMEZONE))
  days_to_open = 3 if now.weekday() == 4 else 1
  next_open_time = (now + timedelta(days=days_to_open)).replace(
    hour=OPEN_HOUR, minute=OPEN_HOUR_MIN)
  return (next_open_time - now).total_seconds()


while True:
  corrections_info = track_stocks.get_corrections_info()
  record = ''
  
  if corrections_info is not None:
    record = f"Corrections!\n{corrections_info}"
    track_stocks.update_notify_percent()
  else:
    record = f"No corrections\n{track_stocks.get_all_info()}"

  record += f"\n{datetime.now(tz=ZoneInfo(TIMEZONE)).strftime('%Y-%m-%d %H:%M:%S')}\n\n"

  with open("output.txt", "a") as file:
    file.write(record)
  # print(record)

  if is_trading_time():
    time.sleep(5 * 60)
  else:
    track_stocks.reset_notify_percent()
    time.sleep(get_secs_till_open())
