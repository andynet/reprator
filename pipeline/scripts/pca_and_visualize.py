#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 14:38:51 2020

@author: andyb
"""


# %%
import pickle
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
# from sklearn.pipeline import Pipeline
from sklearn.pipeline import make_pipeline
import seaborn as sns
from collections import Counter
import matplotlib.pyplot as plt

# %%
file = '/faststorage/project/reprator/Andrej/reprator2/data/subsampled.pkl'
df = pickle.load(open(file, 'rb'))

# %%
features = df.iloc[:, :-1]
labels = df.iloc[:, -1]


# %%
def transform_data(pca_ncomp, perplexity):
    pipeline = make_pipeline(
        StandardScaler(),
        PCA(n_components=pca_ncomp),
        TSNE(n_components=2, perplexity=perplexity))
    result = pipeline.fit_transform(features)

    tmp = pd.DataFrame(result, index=features.index, columns=['t-SNE1', 't-SNE2'])
    tmp['class'] = labels
    return tmp


# %%
fig, axes = plt.subplots(nrows=3, ncols=3)
for i, pca_ncomp in enumerate([10, 100, 244]):
    for j, perplexity in enumerate([10, 30, 50]):
        data = transform_data(pca_ncomp, perplexity)
        ax = axes[i, j]
        sns.scatterplot(x='t-SNE1', y='t-SNE2', hue='class',
                        data=data, legend=None, ax=ax)
        ax.set_title(str(pca_ncomp) + '_' + str(perplexity))


# %%
def select_ctype(ctype, features, labels):
    return labels[labels == ctype], features[labels == ctype]


# %%
print(Counter(list(labels)))

# %%
selected_features = pd.DataFrame()
selected_labels = pd.Series()
for ctype in ['LUAD', 'PRAD', 'COAD', 'BRCA']:
    lab, fea = select_ctype(ctype, features, labels)
    selected_features = selected_features.append(fea)
    selected_labels = selected_labels.append(lab)

features = selected_features
labels = selected_labels
