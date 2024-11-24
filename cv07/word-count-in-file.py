from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, split, regexp_replace, lower

spark = SparkSession.builder.appName("WordCountInFiles").getOrCreate()

lines = spark.readStream.format("text").option("path", "/files/data").option("maxFilesPerTrigger", 1).load()


words = lines.select(explode(split(lower(regexp_replace(col("value"), "[^a-zA-Z0-9\\s]", "")), "\\s+")).alias("word"))

word_counts = words.groupBy(col("word")).count()

sorted_word_counts = word_counts.orderBy(col("count").desc())

query = sorted_word_counts.writeStream.outputMode("complete").format("console").option("truncate", "false").start()

query.awaitTermination()