import os
import zipfile
import pandas as pd
from loguru import logger
from multiprocessing import Pool, Lock


# 设置日志
logger.add("to_parquet_info.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", encoding="utf-8")
logger.add("to_parquet_error.log", format="{time} {level} {message}", level="ERROR", rotation="10 MB", encoding="utf-8")

converted_files_path = "converted_files_list.parquet"
tmp_directory = "/home/longt/temp"
lock = Lock()


def find_zip_files(directory):
    """
    生成器函数：递归遍历给定目录，逐个返回.zip文件的路径。
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.zip'):
                yield os.path.join(root, file)


def is_file_converted(zip_file_path, df_converted):
    """
    检查文件是否已经被转换成parquet过了
    :return: 转换过了:TRUE 没转换过: FALSE
    """
    contains_given_value = (df_converted['file_path'].isin([zip_file_path])).any()
    return contains_given_value


def process_file(zip_file_path):
    """
    处理单个ZIP文件：解压、转换CSV为Parquet，并清理临时文件。
    """
    trading_pair = os.path.basename(os.path.dirname(os.path.dirname(zip_file_path)))
    parquet_directory = f"fdisk/binance_parquet/data/spot/monthly/klines/{trading_pair}/1s/"
    if not os.path.exists(parquet_directory):
        os.makedirs(parquet_directory)

    csv_file_path = zip_file_path.replace('.zip', '.csv').replace(
        f'fdisk/binance/data/spot/monthly/klines/{trading_pair}/1s/', '/home/longt/temp/')
    try:
        # 解压ZIP文件
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_directory)
            zip_ref.close()
        # 使用Pandas读取CSV文件
        column_names = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume',
                        'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
        dtype_spec = {'open': 'float64',
                      'high': 'float64',
                      'low': 'float64',
                      'close': 'float64',
                      'volume': 'float64',
                      'quote_asset_volume': 'float64',
                      'number_of_trades': 'float64',
                      'taker_buy_base_asset_volume': 'float64',
                      'taker_buy_quote_asset_volume': 'float64',
                      'ignore': 'int64'}
        # 使用Pandas读取CSV文件,并为其设定列名
        df = pd.read_csv(csv_file_path, header=None, names=column_names, dtype=dtype_spec)
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
        # 替换文件路径和扩展名，准备写入Parquet文件
        parquet_path = zip_file_path.replace('.zip', '.parquet').replace('fdisk/binance', 'fdisk/binance_parquet')
        # 使用Zstandard压缩保存为Parquet文件
        df.to_parquet(parquet_path, engine='pyarrow', compression='zstd')
        # 重新读取parquet数据,比对新数据和老数据进行校验
        df_reread = pd.read_parquet(parquet_path)
        if df.equals(df_reread):
            logger.info(f"成功处理 {zip_file_path}")

            with lock:
                df_converted = pd.read_parquet(converted_files_path)
                # 创建一个新的 DataFrame 来添加数据
                new_data = pd.DataFrame({
                    'file_path': [zip_file_path]
                })
                # 将新数据追加到现有 DataFrame
                df_converted = pd.concat([df_converted, new_data], ignore_index=True)
                df_converted.to_parquet(converted_files_path, engine='pyarrow', compression='zstd')
        else:
            raise Exception("数据核对不一致")
    except Exception as e:
        logger.error(f"处理文件时出错 {zip_file_path}: {e}")
    finally:
        if os.path.exists(csv_file_path):
            # 删除csv文件
            os.remove(csv_file_path)


if __name__ == "__main__":

    base_path = "fdisk/binance/data/spot/monthly/klines/"
    if not os.path.exists(converted_files_path):
        df_converted_list = pd.DataFrame(columns=['file_path'])
        df_converted_list.to_parquet(converted_files_path, engine='pyarrow', compression='zstd')
    df_history_converted = pd.read_parquet(converted_files_path)
    if not os.path.exists(tmp_directory):
        os.makedirs(tmp_directory)

    with Pool(processes=4) as pool:
        for zip_file_path_dir in find_zip_files(base_path):
            if not is_file_converted(zip_file_path_dir, df_history_converted):
                pool.apply_async(process_file, args=(zip_file_path_dir,))
        pool.close()
        pool.join()
    logger.info("所有文件已处理")
