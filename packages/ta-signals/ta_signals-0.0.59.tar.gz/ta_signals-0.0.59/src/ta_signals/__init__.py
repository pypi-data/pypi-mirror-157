from .main import TaSignals

def go(ohlc, key, window=2):
    t = TaSignals(window)

    ma_data, ohlc = t.ma(ohlc, key)
    ema_data, ohlc = t.ema(ohlc, key)
    bollinger_data, ohlc = t.bollinger(ohlc, key)
    rsi_data, ohlc = t.rsi(ohlc, key)
    macd_data, ohlc = t.macd_slope(ohlc, key)
    div_data, ohlc = t.divergence(ohlc, key)
    volume_data, ohlc = t.volume(ohlc, key)
    key_data, ohlc = t.key(ohlc, key)
    pi_cycle_data, ohlc = t.pi_cycle(ohlc, key)
    #obv_data, ohlc = t.on_balance_volume(ohlc, 5, key)

    data = div_data + bollinger_data + macd_data + ma_data + ema_data + rsi_data + volume_data + key_data + pi_cycle_data

    return data, ohlc

