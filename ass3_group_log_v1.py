#!/usr/bin/env python
# coding: utf-8

# In[1]:


from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.sql.functions import split
from pyspark.ml.feature import StringIndexer
from pyspark.sql.functions import col
import time
import numpy as np

spark = SparkSession.builder.appName("DecisionTree").getOrCreate()
kdd = spark.read.csv("data/kdd.data")
print(kdd)
print(kdd.show())



# In[2]:


# Set the number of runs
seeds = [123,1234,777,888,1000,9876545,123456,3333,88,1000]

# Initialize lists to store accuracy results
train_accuracies = []
test_accuracies = []
run = 1



# In[3]:


feature_columns = kdd.columns[:-1]  # Select all columns except the last one
label_column = kdd.columns[-1] 


# Create a StringIndexer to encode the label column
label_indexer = StringIndexer(inputCol=label_column, outputCol="indexed_lab")
data = label_indexer.fit(kdd).transform(kdd)


# # List of columns to convert
columns_to_convert = ["_c0","_c1", "_c2", "_c3", "_c4", "_c5", "_c6", "_c7", "_c8", "_c9", "_c10",
                      "_c11", "_c12", "_c13", "_c14", "_c15", "_c16", "_c17", "_c18", "_c19", "_c20",
                      "_c21", "_c22", "_c23", "_c24", "_c25", "_c26", "_c27", "_c28", "_c29", "_c30",
                      "_c31", "_c32", "_c33", "_c34", "_c35", "_c36", "_c37", "_c38", "_c39", "_c40"]

# Convert columns to numerical types
for column in columns_to_convert:
    data = data.withColumn(column, col(column).cast("double"))
# Create a vector assembler to combine the feature columns into a single vector column
assembler = VectorAssembler(inputCols=feature_columns, outputCol="features")
kdd_vec = assembler.transform(data)
kdd_vec.select("features").show(truncate=False)


# In[4]:


def dt_main(seed,run):
    (training_data, test_data) = kdd_vec.randomSplit([0.7, 0.3],seed=seed)
#     trainingData.show()
#     testData.show()
    print(run ," - seed =", seed)
    start_time = time.time()
    dt = LogisticRegression(labelCol="indexed_lab", featuresCol="features")
    dtModel = dt.fit(training_data)

    train_pred = dtModel.transform(training_data)
    test_pred = dtModel.transform(test_data)



    # Evaluation
    evaluator = MulticlassClassificationEvaluator(
        labelCol="indexed_lab", predictionCol="prediction", metricName="accuracy"
    )
    train_accuracy = evaluator.evaluate(train_pred)
    test_accuracy =  evaluator.evaluate(test_pred)

    print("Training Accuracy:", train_accuracy)
    print("Test Accuracy:", test_accuracy)

    train_accuracies.append(train_accuracy)
    test_accuracies.append(test_accuracy)

    running_time = time.time() - start_time
    print("Running Time:", running_time, "seconds")
    run = run+1
    return run



 


# In[5]:


for seed in seeds:
    
    run = dt_main(seed, run)
print("Training Accuracy - Max:", np.max(train_accuracies))
print("Training Accuracy - Min:", np.min(train_accuracies))
print("Training Accuracy - Average:", np.mean(train_accuracies))
print("Training Accuracy - Standard Deviation:", np.std(train_accuracies))
print("Test Accuracy - Max:", np.max(test_accuracies))
print("Test Accuracy - Min:", np.min(test_accuracies))
print("Test Accuracy - Average:", np.mean(test_accuracies))
print("Test Accuracy - Standard Deviation:", np.std(test_accuracies))


# In[35]:


spark.stop()


# In[ ]:





