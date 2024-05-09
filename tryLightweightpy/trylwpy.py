from decimal import Decimal

import pandas as pd
from lightweight_charts import Chart

if __name__ == '__main__':
    chart = Chart()

    # Columns: time | open | high | low | close | volume
    df = pd.read_parquet('/media/longt/fdisk/binance_parquet/data/spot/monthly/klines/BTCUSDT/1s/BTCUSDT-1s-2024-02.parquet')
    selected_columns = df[['open_time','open','high','low','close','volume']]
    renamed_columns = selected_columns.rename(columns={'open_time':'time'})
    renamed_columns = renamed_columns.apply(pd.to_numeric, downcast='float')



    chart.set(renamed_columns)

    chart.show(block=True)
