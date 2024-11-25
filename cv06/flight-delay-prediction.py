from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
from pyspark.sql.types import DoubleType, IntegerType
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, VectorAssembler, OneHotEncoder
from pyspark.ml.classification import LogisticRegression, GBTClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

spark = (
    SparkSession.builder.appName("FlightDelayPrediction")
    .config("spark.executor.memory", "8g")
    .config("spark.driver.memory", "8g")
    .config("spark.memory.fraction", "0.8")
    .getOrCreate()
)

main_columns = [
    "Year",
    "Month",
    "DayofMonth",
    "DayOfWeek",
    "CRSDepTime",
    "CRSArrTime",
    "UniqueCarrier",
    "CRSElapsedTime",
    "Origin",
    "Dest",
    "Distance",
]

columns_to_index = ["UniqueCarrier", "Origin", "Dest"]

df_2006 = spark.read.option("header", "true").option("inferSchema", "true").csv("/files/2006.csv")
df_2007 = spark.read.option("header", "true").option("inferSchema", "true").csv("/files/2007.csv")
df_2008 = spark.read.option("header", "true").option("inferSchema", "true").csv("/files/2008.csv")

df = df_2006.union(df_2007).union(df_2008).repartition(10)

df = df.select(main_columns + ["Cancelled", "ArrDelay"])
df = df.filter((col("Cancelled") == 0) & (col("ArrDelay").isNotNull()))
df = df.withColumn("label", when(col("ArrDelay") > 0, 1).otherwise(0))
df = df.withColumn("CRSElapsedTime", col("CRSElapsedTime")).cast(IntegerType())

unique_carrier_index = StringIndexer(inputCol="UniqueCarrier", outputCol="UniqueCarrierIndex", handleInvalid="skip").fit(df)
origin_index = StringIndexer(inputCol="Origin", outputCol="OriginIndex", handleInvalid="skip").fit(df)
dest_index = StringIndexer(inputCol="Dest", outputCol="DestIndex", handleInvalid="skip").fit(df)

unique_carrier_vec = OneHotEncoder(inputCol="UniqueCarrierIndex", outputCol="UniqueCarrierVec")
origin_vec = OneHotEncoder(inputCol="OriginIndex", outputCol="OriginVec")
dest_vec = OneHotEncoder(inputCol="DestIndex", outputCol="DestVec")

assembler_columns = []
for col in main_columns:
    if col in columns_to_index:
        assembler_columns.append(f"{col}Vec")
    else:
        assembler_columns.append(col)

assembler = VectorAssembler(inputCols=assembler_columns, outputCol="features", handleInvalid="skip")

log_reg = LogisticRegression(featuresCol="features", labelCol="label")

pipeline = Pipeline(stages=[unique_carrier_index, origin_index, dest_index, unique_carrier_vec, origin_vec, dest_vec, assembler, log_reg])

train_data, test_data = df.randomSplit([0.9, 0.1], seed=42)

pipeline_model =  pipeline.fit(train_data)

predictions = pipeline_model.transform(test_data)

evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")

accuracy = evaluator.evaluate(predictions)
print(f"Logistic Regression Accuracy: {accuracy}")

if accuracy < 0.55:
    gbt_classifier = GBTClassifier(featuresCol="features", labelCol="label", maxIter=50)
    gbt_classifier_model = gbt_classifier.fit(train_data)
    predictions = gbt_classifier_model.transform(test_data)
    accuracy = evaluator.evaluate(predictions)
    print(f"Random Forest Accuracy: {accuracy}")

spark.stop()

