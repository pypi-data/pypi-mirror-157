import numpy as np


def cosine(x, y, eps=1e-10):
    x = x.astype(np.float32)
    y = y.astype(np.float32)
    den = (np.dot(x, x) * np.dot(y, y)) ** 0.5
    return np.dot(x, y) / (den + eps)


def vecs_similarity(old_vecs, new_vecs, corpus):
    return np.mean([cosine(old_vecs[w], new_vecs[w]) for w in corpus])
