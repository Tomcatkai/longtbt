from typing import List

from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.responses import FileResponse, JSONResponse
import pandas as pd
import pyarrow.parquet as pq

app = FastAPI()

# 静态文件服务挂载在一个子路径
app.mount("/static", StaticFiles(directory="/home/longt/PycharmProjects/longtbt/tryFastapi/static", html=True),
          name="static")


# 根路径请求重定向到 index.html
@app.get("/")
def main():
    return FileResponse("/home/longt/PycharmProjects/longtbt/tryFastapi/static/index.html")

@app.get("/api/BTCUSDT")
def getbtcusdt(page: int = Query(0, ge=0), page_size: int = Query(15000, ge=1)):
    # df = pd.read_parquet(
    #     '/media/longt/fdisk/binance_parquet/data/spot/monthly/klines/BTCUSDT/1s/BTCUSDT-1s-2024-02.parquet')
    table = pq.read_table('/media/longt/fdisk/binance_parquet/data/spot/monthly/klines/BTCUSDT/1s/BTCUSDT-1s-2024-02.parquet',
                          columns=['open_time', 'open', 'high', 'low', 'close', 'volume'])
    # 分页处理
    start = page * page_size
    # end = start + page_size
    table_page = table.slice(start, page_size)
    # df_page = df.iloc[start:end]
    df_page = table_page.to_pandas()
    selected_columns = df_page[['open_time', 'open', 'high', 'low', 'close', 'volume']]
    renamed_columns = selected_columns.rename(columns={'open_time': 'time'})
    for col in renamed_columns.columns:
        if pd.api.types.is_object_dtype(renamed_columns[col]):
            # 对浮点列使用定制的格式转换
            # renamed_columns[col] = renamed_columns[col].map(lambda x: f'{x:.8f}')
            renamed_columns[col] = renamed_columns[col].map(lambda x: float(f'{x:.8f}'))

        else:
            # 其他类型直接转换为字符串
            renamed_columns[col] = renamed_columns[col].astype(str)

    # result = [StockData.parse_obj(item) for item in renamed_columns.to_dict(orient='records')]
    # return result

    # result = renamed_columns.to_dict(orient="records")
    # 确保直接返回序列化的结果
    # return JSONResponse(content=result, media_type="application/json")
    result = renamed_columns.to_json(orient="records")
    return JSONResponse(content=result, media_type="application/json")
