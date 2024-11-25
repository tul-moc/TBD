from pyspark.sql import SparkSession

spark = SparkSession.builder.master("local").appName("SparkSQL").getOrCreate()

people = spark.read.option("header", "true").option("inferSchema", "true").csv("/files/fakefriends-header.csv")

people.createOrReplaceTempView("people")

avarage_friends_by_age = spark.sql("""
    SELECT age, AVG(friends) AS average_friends
    FROM people
    GROUP BY age
    ORDER BY age
""")

avarage_friends_by_age.show()


spark.stop()

