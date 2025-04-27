import requests
import pandas as pd
import talib
import time
from telegram import Bot

# ====== CẤU HÌNH ======
SYMBOL = "BTCUSDT"          # Cặp coin muốn trade
INTERVAL = "1m"             # Khung thời gian nến
LIMIT = 50                  # Số nến lấy (càng nhiều càng ổn định tín hiệu)
RSI_PERIOD = 14             # Chu kỳ RSI

TELEGRAM_TOKEN = "7258798991:AAGO69jf0DNL-yIc-QVirm3gTYwab1ssjWk"   # <-- điền token bot vào đây
TELEGRAM_CHAT_ID = "6357023076"            # <-- điền chat id vào đây

DELAY_SECONDS = 60         # Sau bao lâu quét lại (60 giây = 1 phút)

# ====== HÀM LẤY DỮ LIỆU NẾN ======
def get_binance_candles(symbol, interval, limit):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])
    df["open_time"] = pd.to_datetime(df["open_time"], unit='ms')
    df["close"] = df["close"].astype(float)
    return df

# ====== HÀM PHÂN TÍCH RSI ======
def calculate_rsi(candles, period):
    closes = candles['close'].values
    rsi = talib.RSI(closes, timeperiod=period)
    return rsi[-1]

# ====== HÀM GỬI TÍN HIỆU TELEGRAM ======
def send_telegram_signal(signal, rsi_value):
    bot = Bot(TELEGRAM_TOKEN)
    message = f"📈 Tín hiệu Trade:\nSignal: {signal}\nRSI: {rsi_value:.2f}"
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

# ====== CHƯƠNG TRÌNH CHÍNH ======
def main():
    while True:
        try:
            candles = get_binance_candles(SYMBOL, INTERVAL, LIMIT)
            rsi_value = calculate_rsi(candles, RSI_PERIOD)

            # Xác định tín hiệu
            if rsi_value < 30:
                signal = "MUA ⬆️"
            elif rsi_value > 70:
                signal = "BÁN ⬇️"
            else:
                signal = "CHỜ 💤"

            print(f"RSI: {rsi_value:.2f} -> {signal}")

            # Gửi tín hiệu nếu là MUA/BÁN rõ ràng
            if signal != "CHỜ 💤":
                send_telegram_signal(signal, rsi_value)

        except Exception as e:
            print("Lỗi:", e)

        time.sleep(DELAY_SECONDS)

if __name__ == "__main__":
    main()