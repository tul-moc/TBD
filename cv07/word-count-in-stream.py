from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, split,window, regexp_replace, lower, current_timestamp


spark = SparkSession.builder.appName("WordCountInStream").getOrCreate()

lines = spark.readStream.format("socket").option("host", "localhost").option("port", 9999).load()

words = lines.select(
    explode(split(lower(regexp_replace(col("value"), "[^a-zA-Z0-9\\s]", "")), "\\s+")).alias("word"),
    current_timestamp().alias("timestamp"),
)

word_counts = words.groupBy(
    window(col("timestamp"), "30 seconds", "15 seconds"),
    col("word"),
).count()

sorted_word_counts = word_counts.select(
    col("window.start").alias("start"),
    col("window.end").alias("end"),
    col("word"),
    col("count"),
).orderBy(col("start"), col("count").desc())

query = sorted_word_counts.writeStream.outputMode("complete").format("console").option("truncate", "false").start()

query.awaitTermination()