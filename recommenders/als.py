import os

import numpy as np
from implicit.als import AlternatingLeastSquares

from recommenders.base_recommender import BaseRecommender


class ALS(BaseRecommender):
    name = 'als'

    def __init__(self, session, user_interactions_threshold=0, item_interactions_threshold=2,
                 factors=1024, regularization=100, iterations=35, alpha=21):
        super().__init__(session, user_interactions_threshold, item_interactions_threshold)

        self.factors = factors
        self.regularization = regularization
        self.iterations = iterations
        self.alpha = alpha
        self.user_factors = None
        self.item_factors = None

    def fit(self, training_urm):
        training_urm = super().fit(training_urm)
        sparse_item_user = training_urm.transpose().tocsr()
        os.environ['OPENBLAS_NUM_THREADS'] = '1'
        model = AlternatingLeastSquares(factors=self.factors,
                                        regularization=self.regularization,
                                        iterations=self.iterations)
        data_confidence = (sparse_item_user * self.alpha).astype(np.float32)
        model.fit(data_confidence, show_progress=False)
        self.user_factors = model.user_factors
        self.item_factors = model.item_factors

    def get_ratings(self, training_urm, user_id):
        ratings = np.dot(self.user_factors[user_id], self.item_factors.T)
        ratings = ratings - np.min(ratings)
        ratings = ratings.reshape(1, -1)
        if np.max(ratings) != 0:
            ratings = ratings / np.max(ratings)
        ratings = ratings.ravel()
        interacted_items = training_urm[user_id]
        ratings[interacted_items.indices] = -100
        return ratings
