from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import DecisionTreeRegressor
import pandas as pd
import numpy as np

spark = SparkSession.builder.master("local").appName("SparkSQL").getOrCreate()

realestate = spark.read.option("header", "true").option("inferSchema", "true").csv("/files/realestate.csv")

assembler = VectorAssembler(
    inputCols=["HouseAge", "DistanceToMRT", "NumberConvenienceStores"], 
    outputCol="Features"
    )

df = assembler.transform(realestate).select("PriceOfUnitArea", "Features")

train_data, test_data = df.randomSplit([0.9, 0.1], seed=1234)

dtr = DecisionTreeRegressor(labelCol="PriceOfUnitArea", featuresCol="Features")

model = dtr.fit(train_data)

predictions = model.transform(test_data)

predictions_pd = predictions.select("prediction", "PriceOfUnitArea").toPandas()

predictions_pd["difference"] = np.abs(predictions_pd["prediction"] - predictions_pd["PriceOfUnitArea"])

print(predictions_pd)

average_difference = predictions_pd["difference"].mean()
print(f"Average Prediction Error: {average_difference}")

spark.stop()