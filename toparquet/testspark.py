import os, sys

os.environ['SPARK_HOME'] = "/opt/spark"  #path to spark
sys.path.append(os.path.join(os.environ['SPARK_HOME'], 'python'))
sys.path.append(os.path.join(os.environ['SPARK_HOME'], 'python/lib/py4j-0.10.9.7-src.zip'))
#
# import pyspark
#
# spark = pyspark.sql.SparkSession.builder.appName("pysaprk_python").getOrCreate()
#
# print(spark.version, spark.sparkContext.master)

from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .master("local") \
    .appName("RAPIDS Spark Example") \
    .config("spark.executor.instances", "1") \
    .config("spark.executor.cores", "1") \
    .config("spark.rapids.sql.concurrentGpuTasks", "1") \
    .config("spark.driver.memory", "10g") \
    .config("spark.rapids.memory.pinnedPool.size", "2G") \
    .config("spark.sql.files.maxPartitionBytes", "512m") \
    .config("spark.plugins", "com.nvidia.spark.SQLPlugin") \
    .config("spark.jars", "/opt/rapids-4-spark_2.13-24.04.0.jar") \
    .getOrCreate()

# 创建 DataFrame
df1 = spark.range(0, 10000000, 1, 6).toDF("value").withColumnRenamed("value", "a")
df2 = spark.range(0, 10000000, 1, 6).toDF("value").withColumnRenamed("value", "b")

# 执行连接操作
join_df = df1.join(df2, df1.a == df2.b)
count = join_df.count()

# 打印结果
print(f"The count of join results is: {count}")


# Your Spark code here
input("Press Enter to exit...")  # 在调用 spark.stop() 之前添加这行

spark.stop()


