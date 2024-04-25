from sklearn.cluster import KMeans
import numpy as np

# Sample data
X = np.array([[1, 2], [1, 4], [1, 0],
              [4, 2], [4, 4], [4, 0]])

# Creating a KMeans instance
kmeans = KMeans(n_clusters=2, random_state=10)

# Fitting the model to the data
kmeans.fit(X)

# Getting the cluster centers
print("Cluster centers:")
print(kmeans.cluster_centers_)

# Predicting the clusters for the data points
print("\nPredicted clusters:")
print(kmeans.predict(X))
