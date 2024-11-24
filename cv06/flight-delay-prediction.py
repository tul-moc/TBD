from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when
from pyspark.sql.types import DoubleType, IntegerType
from pyspark.ml import Pipeline
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.classification import LogisticRegression, GBTClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator


def get_vector_assembler_columns(columns, columns_to_index):
    assembler_col = []
    for col in columns:
        if col in columns_to_index:
            assembler_col.append(f"{col}_index")
        else:
            assembler_col.append(col)
    return assembler_col

def get_string_indexer_columns(columns_to_index):
    stages = []
    for column in columns_to_index:
        indexer = StringIndexer(
            inputCol=column,
            outputCol=f"{column}_index",
            handleInvalid="skip"
        ).fit(df)
        stages.append(indexer)
    return stages




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

df = df_2006.union(df_2007).union(df_2008)

df = df.select(main_columns + ["Cancelled", "ArrDelay"])

df = df.filter((col("Cancelled") == 0) & (col("ArrDelay").isNotNull()))

df = df.withColumn("label", when(col("ArrDelay") > 0, 1).otherwise(0).cast(DoubleType()))

df = df.withColumn("CRSElapsedTime", col("CRSElapsedTime").cast(IntegerType()))

stages = get_string_indexer_columns(columns_to_index)

pipeline = Pipeline(stages=stages)

df = pipeline.fit(df).transform(df)

df = df.repartition(100)

assembler = VectorAssembler(
    inputCols=get_vector_assembler_columns(main_columns, columns_to_index),
    outputCol="features",
    handleInvalid="skip",
)

df = assembler.transform(df)
train_data, test_data = df.randomSplit([0.9, 0.1], seed=42)

logistic_regression = LogisticRegression(featuresCol="features", labelCol="label")
logistic_regression_model = logistic_regression.fit(train_data)
predictions = logistic_regression_model.transform(test_data)

evaluator = MulticlassClassificationEvaluator(
    labelCol="label", predictionCol="prediction", metricName="accuracy"
)

accuracy = evaluator.evaluate(predictions)
print(f"Logistic Regression Accuracy: {accuracy}")

# Použítí Gradient Boosted Trees, který je výpočetně náročnější, ale používá gradientní booting, 
# což znamená, že se učí z chyb minulých modelů a zlepšuje se. Dá se mu určit počet iterací (stromů)
if accuracy < 0.55:
    gbt_classifier = GBTClassifier(featuresCol="features", labelCol="label", maxIter=50)
    gbt_classifier_model = gbt_classifier.fit(train_data)
    predictions = gbt_classifier_model.transform(test_data)
    accuracy = evaluator.evaluate(predictions)
    print(f"Random Forest Accuracy: {accuracy}")

spark.stop()

