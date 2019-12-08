import numpy as np
from scipy import sparse
from sklearn.preprocessing import normalize
from sklearn.utils.extmath import randomized_svd


class SVD(object):

    # 0.02403678660970901
    def __init__(self, n_factors=100):
        self.n_factors = n_factors
        self.training_urm = None
        self.user_factors = None
        self.item_factors = None

    def fit(self, training_urm):
        self.training_urm = training_urm
        U, s, V = randomized_svd(self.training_urm,
                                 n_components=self.n_factors,
                                 n_oversamples=5,
                                 n_iter=6)
        s_V = sparse.diags(s) * V
        self.user_factors = U
        self.item_factors = s_V.T

    def get_expected_ratings(self, user_id):
        expected_ratings = np.dot(self.user_factors[user_id], self.item_factors.T)
        expected_ratings = expected_ratings - expected_ratings.min()
        expected_ratings = expected_ratings.reshape(1, -1)
        expected_ratings = normalize(expected_ratings, axis=1, norm='max')
        expected_ratings = expected_ratings.ravel()
        interacted_items = self.training_urm[user_id]
        expected_ratings[interacted_items.indices] = -100
        return expected_ratings

    def recommend(self, user_id, k=10):
        expected_ratings = self.get_expected_ratings(user_id)
        recommended_items = np.flip(np.argsort(expected_ratings), 0)
        unseen_items_mask = np.in1d(recommended_items, self.training_urm[user_id].indices, assume_unique=True,
                                    invert=True)
        recommended_items = recommended_items[unseen_items_mask]
        return recommended_items[:k]
