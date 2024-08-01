import os

import gspread
from google.oauth2.service_account import Credentials

MOCK_STOCKS = [
  {
    "rowNumber":2,
    "market":"NSE",
    "symbol":"NIFTYBEES",
    "ltp":273.08,
    "previousClose":271.92,
    "change":1.16,
    "changePercent":-1,
    "belowPercent":-1,
    "belowPercentInterval":-1,
    "notifyBelowPercent":-1,
    "dataDelay":0
  },
  {
    "rowNumber":3,
    "market":"NSE",
    "symbol":"GOLDBEES",
    "ltp":59.42,
    "previousClose":59.37,
    "change":0.05,
    "changePercent":-2,
    "belowPercent":-1,
    "belowPercentInterval":-1,
    "notifyBelowPercent":-1,
    "dataDelay":0
  },
  {
    "rowNumber":4,
    "market":"NSE",
    "symbol":"BANKBEES",
    "ltp":520.82,
    "previousClose":521.82,
    "change":-1,
    "changePercent":-0.19,
    "belowPercent":-1,
    "belowPercentInterval":-1,
    "notifyBelowPercent":-1,
    "dataDelay":0
  }
]

class TrackStocks:
  def __init__(self):
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(
      "credentials.json",
      scopes=scopes
    )
    client = gspread.authorize(creds)
    workbook = client.open_by_key(os.environ['SHEET_ID'])
    self.worksheet = workbook.worksheet(os.environ['SHEET_NAME'])
    self.corrected_stocks = []


  def get_all_stocks(self):
    # return MOCK_STOCKS
    all_stocks = self.worksheet.get_all_records()
    return [
      { "rowNumber": index, **stock }
      for index, stock in enumerate(all_stocks, start=2)
    ]


  def get_corrected_stocks(self):
    stocks = self.get_all_stocks()
    corrected_stocks = [
      s for s in stocks
      if float(s["changePercent"]) <= float(s["notifyBelowPercent"])
    ]
    self.corrected_stocks = sorted(corrected_stocks, key=lambda s: s["changePercent"])

    return self.corrected_stocks


  def get_stock_info(self, stock):
    return f"{stock['symbol']} {stock['changePercent']}% LTP: {stock['ltp']} PC: {stock['previousClose']} ({stock['change']})"

  def get_corrections_info(self):
    corrected_stocks = self.get_corrected_stocks()

    if len(corrected_stocks) > 0:
      info = [self.get_stock_info(s) for s in corrected_stocks]
      return "\n".join(info)
    else:
      return None


  def get_all_info(self):
    stocks = self.get_all_stocks()
    info = [self.get_stock_info(s) for s in stocks]
    return "\n".join(info)


  def update_notify_percent(self):
    for stock in self.corrected_stocks:
      new_notify_percent = max(
        stock["notifyBelowPercent"] + stock["belowPercentInterval"],
        int(stock["changePercent"])
      )
      self.worksheet.update_cell(stock["rowNumber"], 9, new_notify_percent)

    self.corrected_stocks = []


  def reset_notify_percent(self):
    for stock in self.get_all_stocks():
      self.worksheet.update_cell(stock["rowNumber"], 9, stock["belowPercent"])
