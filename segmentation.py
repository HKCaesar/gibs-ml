# Copyright 2018 California Institute of Technology.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
from imageio import imread
from scipy.spatial.distance import cdist

def get_img_feature_vector(img):
    # Create the feature vector for the images
    features = np.zeros((img.shape[0] * img.shape[1], 5))
    for row in xrange(img.shape[0]):
        for col in xrange(img.shape[1]):
            features[row*img.shape[1] + col, :] = np.array([row, col, 
                img[row, col, 0], img[row, col, 1], img[row, col, 2]])
    features_normalized = features / features.max(axis = 0)
    return features_normalized

'''
KMEANS_SEGMENTATION: Image segmentation using kmeans 
Arguments:
    im - the image being segmented, given as a (H, W, 3) ndarray

    features - ndarray of size (#pixels, M) that are the feature vectors 
        associated with each pixel. The #pixels are arranged in such a way
        that calling reshape((H,W)) will correspond to the image im.

    num_clusters - The parameter "K" in K-means that tells the number of 
        clusters we will be using.

Returns:
    pixel_clusters - H by W matrix where each index tells what cluster the
        pixel belongs to. The clusters must range from 0 to N-1, where N is
        the total number of clusters.

The K-means algorithm can be done in the following steps:
(1) Randomly choose the initial centroids from the features
(2) Repeat until convergence:
    - Assign each feature vector to its nearest centroid
    - Compute the new centroids as the average of all features assigned to it
    - Convergence happens when the centroids do not change
'''
def kmeans_segmentation(im, features, num_clusters):
    H, W = im.shape[0], im.shape[1]
    num_pixels = features.shape[0]

    # (1) Randomly choose the initial centroids from the features
    curr_centroids = features[np.random.randint(num_pixels, size=num_clusters)]

    # (2) Repeat until convergence
    while True:
        # Assign each feature vector to its nearest centroid
        distances = np.zeros((num_pixels, num_clusters))
        for cluster_idx in range(num_clusters):
            distances[:,cluster_idx] = np.linalg.norm(features - curr_centroids[cluster_idx,:], axis=1)
        nearest_clusters = np.argmin(distances, axis=1)

        # Keep track of previous state of centroids
        prev_centroids = curr_centroids

        # Compute the new centroids as the average of all features assigned to it
        for cluster_idx in range(num_clusters):
            pixel_idx = np.where(nearest_clusters == cluster_idx)
            curr_centroids[cluster_idx,:] = np.mean(features[pixel_idx], axis=0)

        # Convergence happens when the centroids do not change
        if np.array_equal(curr_centroids, prev_centroids):
            break

    # H by W matrix where each index tells what cluster the pixel belongs to
    pixel_clusters = np.reshape(nearest_clusters, (H, W))
    return pixel_clusters

'''
MEANSHIFT_SEGMENTATION: Image segmentation using meanshift
Arguments:
    im - the image being segmented, given as a (H, W, 3) ndarray

    features - ndarray of size (#pixels, M) that are the feature vectors 
        associated with each pixel. The #pixels are arranged in such a way
        that calling reshape((H,W)) will correspond to the image im.

    bandwidth - A parameter that determines the radius of what particpates
       in the mean computation

Returns:
    pixel_clusters - H by W matrix where each index tells what cluster the
        pixel belongs to. The clusters must range from 0 to N-1, where N is
        the total number of clusters.

The meanshift algorithm can be done in the following steps:
(1) Keep track of an array whether we have seen each pixel or not.
Initialize it such that we haven't seen any.
(2) While there are still pixels we haven't seen do the following:
    - Pick a random pixel we haven't seen
    - Until convergence (mean is within 1% of the bandwidth of the old
        mean), mean shift. The output of this step will be a mean vector.
        For each iteration of the meanshift, if another pixel is within the
        bandwidth circle (in feature space), then that pixel should also be
        marked as seen
    - If the output mean vector from the mean shift step is
        sufficiently close (within half a bandwidth) to another cluster
        center, say it's part of that cluster
    - If it's not sufficiently close to any other cluster center, make
        a new cluster
(3) After finding all clusters, assign every pixel to the nearest cluster
in feature space.

To perform mean shift:
    - Once a random pixel has been selected, pretend it is the current mean
        vector.
    - Find the feature vectors of the other pixels that are within the
        bandwidth distance from the mean feature vector according to EUCLIDEAN
        distance (in feature space).
    - Compute the mean feature vector among all feature vectors within the
        bandwidth.
    - Repeat until convergence, using the newly computed mean feature vector
        as the current mean feature vector.
'''
def meanshift_segmentation(im, features, bandwidth):
    # initialize some parameters
    H, W = im.shape[0], im.shape[1]
    pixel_num, M = features.shape
    mask = np.ones(pixel_num)
    clusters = []

    while np.sum(mask) > 0:
        loc = np.argwhere(mask > 0)
        idx = loc[int(np.random.choice(loc.shape[0], 1)[0])][0]
        mask[idx] = 0

        current_mean = features[idx]
        prev_mean = current_mean

        while True:
            dist = np.linalg.norm(features - prev_mean, axis=1)
            incircle = dist < bandwidth
            mask[incircle] = 0
            # update current_mean
            current_mean = np.mean(features[incircle], axis=0)
            if np.linalg.norm(current_mean - prev_mean) < 0.01 * bandwidth:
                break
            prev_mean = current_mean

        isValid = True
        for cluster in clusters:
            if np.linalg.norm(cluster - current_mean) < 0.5 * bandwidth:
                isValid = False
        if isValid:
            clusters.append(current_mean)

    pixel_clusters = np.zeros((H, W))
    clusters = np.array(clusters)
    for i in range(pixel_num):
        idx = np.argmin(np.linalg.norm(features[i, :] - clusters, axis=1))
        pixel_clusters[i / W, i % W] = idx
    return pixel_clusters.astype(int)


def draw_clusters_on_image(im, pixel_clusters):
    num_clusters = int(pixel_clusters.max()) + 1
    average_color = np.zeros((num_clusters, 3))
    cluster_count = np.zeros(num_clusters)

    for i in xrange(im.shape[0]):
        for j in xrange(im.shape[1]):
            c = pixel_clusters[i,j]
            cluster_count[c] += 1
            average_color[c, :] += im[i, j, :]

    for c in xrange(num_clusters):
        average_color[c,:] /= float(cluster_count[c])
        
    out_im = np.zeros_like(im)
    for i in xrange(im.shape[0]):
        for j in xrange(im.shape[1]):
            c = pixel_clusters[i,j]
            out_im[i,j,:] = average_color[c,:]

    return out_im