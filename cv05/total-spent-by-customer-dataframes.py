from pyspark.sql import SparkSession
from pyspark.sql import functions as func

spark = SparkSession.builder.master("local").appName("TotalSpenByCustomerDataFrames").getOrCreate()

columns = ["customer_id", "order_id", "price"]
people = spark.read.option("header", "false").option("inferSchema", "true").csv("/files/customer-orders.csv").toDF(*columns)

grouped_people = people.groupBy("customer_id")
total_spent = grouped_people.sum("price").withColumnRenamed("sum(price)", "total_spent")
total_spent = total_spent.withColumn("total_spent", func.round("total_spent", 2))

total_spent.orderBy(func.desc("total_spent")).show()

spark.stop()