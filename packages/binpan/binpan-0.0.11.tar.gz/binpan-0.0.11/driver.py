import binpan

btcusdt = binpan.Symbol(symbol='btcusdt',
                        tick_interval='1h',
                        time_zone='Europe/Madrid')

btcusdt.stoch_rsi(14, 14, 3, 3)

btcusdt.plot()
