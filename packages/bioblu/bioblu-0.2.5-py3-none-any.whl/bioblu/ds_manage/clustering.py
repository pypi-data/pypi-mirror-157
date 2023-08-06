#!/usr/bin/env python3

import matplotlib.pyplot as plt
import pandas as pd


def plot_coordinates(lat: list, long: list, scale=None):
    fig, ax = plt.subplots()
    plt.scatter(long, lat, c=scale, label="Predictions")
    plt.gray()
    plt.legend()
    plt.show()


if __name__ == "__main__":
    csv_fpath = "/home/findux/Desktop/Next/tests/yolo_vid_pipeline/geolocated_predictions.csv"
    points_df = pd.read_csv("/home/findux/Desktop/yolo_pipeline_results_tono/prediction_results.csv")
    plot_coordinates(points_df["box_latitude_deg"], points_df["box_longitude_deg"], scale=points_df["confidence"])

# import numpy as np
# import matplotlib.pyplot as plt
#
# from sklearn.cluster import KMeans
# from sklearn.datasets.samples_generator import make_blobs
#
# ##############################################################################
# # Generate sample data
# np.random.seed(0)
#
# batch_size = 45
# centers = [[1, 1], [-1, -1], [1, -1]]
# n_clusters = len(centers)
# X, labels_true = make_blobs(n_samples=3000, centers=centers, cluster_std=0.7)
#
# ##############################################################################
# # Compute clustering with Means
#
# k_means = KMeans(init='k-means++', n_clusters=3, n_init=10)
# k_means.fit(X)
# k_means_labels = k_means.labels_
# k_means_cluster_centers = k_means.cluster_centers_
# k_means_labels_unique = np.unique(k_means_labels)
#
# ##############################################################################
# # Plot result
#
# colors = ['#4EACC5', '#FF9C34', '#4E9A06']
# plt.figure()
# plt.hold(True)
# for k, col in zip(range(n_clusters), colors):
#     my_members = k_means_labels == k
#     cluster_center = k_means_cluster_centers[k]
#     plt.plot(X[my_members, 0], X[my_members, 1], 'w',
#             markerfacecolor=col, marker='.')
#     plt.plot(cluster_center[0], cluster_center[1], 'o', markerfacecolor=col,
#             markeredgecolor='k', markersize=6)
# plt.title('KMeans')
# plt.grid(True)
# plt.show()
