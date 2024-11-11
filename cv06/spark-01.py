from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler

spark = SparkSession.builder.master("local").appName("SparkSQL").getOrCreate()

realestate = spark.read.option("header", "true").option("inferSchema", "true").csv("/files/realestate.csv")

assembler = VectorAssembler(inputCols=["No", "TransactionDate", "HouseAge", "DistanceToMRT", "NumberConvenienceStores", "Latitude", "Longitude", "PriceOfUnitArea"])

df = assembler.transform(realestate).select("PriceOfUnitArea", "Features")

real_data, test_data = df.randomSplit([0.9, 0.1])

dtr = DecisionTreeRegressor(labelCol="PriceOfUnitArea", featuresCol="Features")

model = dtr.fit(real_data)

predictions = model.transform(test_data)

predictions.show()

spark.stop()