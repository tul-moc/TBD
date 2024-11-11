from pyspark.sql import SparkSession
from pyspark.sql import functions as func
from pyspark.sql.types import StructType, StructField, IntegerType, StringType

spark = SparkSession.builder.master("local").appName("MostObscureSuperheroes").getOrCreate()

schema = StructType([ \
                     StructField("id", IntegerType(), True), \
                     StructField("name", StringType(), True)])

names = spark.read.schema(schema).option("sep", " ").csv("/files/marvel-names.txt")

lines = spark.read.text("/files/marvel-graph.txt")

connections = lines.withColumn("id", func.split(func.trim(func.col("value")), " ")[0]) \
    .withColumn("connections", func.size(func.split(func.trim(func.col("value")), " ")) - 1) \
    .groupBy("id").agg(func.sum("connections").alias("connections"))

hero_connections = names.join(connections, "id")

heroes_with_one_connection = hero_connections.filter(func.col("connections") == 1).select("name", "connections")

heroes_with_one_connection.show(truncate=False)

# Bonus
filtered_connections = connections.filter(func.col("connections") > 0)

min_connections = filtered_connections.agg(func.min("connections")).first()[0]
most_obscure_heroes = hero_connections.filter(func.col("connections") == min_connections).select("name", "connections")

most_obscure_heroes.show(truncate=False)

spark.stop()