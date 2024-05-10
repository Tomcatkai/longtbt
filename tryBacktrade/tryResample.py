import pandas as pd


# resample函数的使用
# 转换周期
# 获取秒k， 获取日k
if __name__ == "__main__":
    df = pd.read_parquet(
        '/media/longt/fdisk/binance_parquet/data/spot/monthly/klines/BTCUSDT/1s/BTCUSDT-1s-2024-02.parquet')
    print(df)

    df['open_time'] = pd.to_datetime(df['open_time'])
    df.set_index('open_time', inplace=True)

    df_day = pd.DataFrame()
    df_day['open'] = df['open'].resample('D').first()
    df_day['close'] = df['close'].resample('D').last()
    df_day['high'] = df['high'].resample('D').max()
    df_day['low'] = df['low'].resample('D').min()
    df_day['volume'] = df['volume'].resample('D').sum()
    df_day['quote_asset_volume'] = df['quote_asset_volume'].resample('D').sum()
    df_day['number_of_trades'] = df['number_of_trades'].resample('D').sum()
    df_day['taker_buy_base_asset_volume'] = df['taker_buy_base_asset_volume'].resample('D').sum()
    df_day['taker_buy_quote_asset_volume'] = df['taker_buy_quote_asset_volume'].resample('D').sum()
    df_day['ignore'] = df['ignore'].resample('D').sum()

    print(df_day)


    # 汇总统计