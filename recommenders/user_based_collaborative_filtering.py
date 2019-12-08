import numpy as np
import similaripy
import similaripy.normalization
from sklearn.preprocessing import normalize


class UserBasedCollaborativeFiltering(object):
    def __init__(self, top_k=1000, shrink=5):
        # 0.041994304234260246
        self.top_k = top_k
        self.shrink = shrink
        self.training_urm = None
        self.recommendations = None

    def fit(self, training_urm):
        self.training_urm = training_urm
        # TODO testare combinazioni di normalizzazioni e distanze
        self.training_urm = similaripy.normalization.bm25plus(self.training_urm)
        similarity_matrix = similaripy.cosine(self.training_urm, k=self.top_k, shrink=self.shrink, binary=False)
        similarity_matrix = similarity_matrix.transpose().tocsr()
        self.recommendations = similarity_matrix.dot(self.training_urm)

    def get_expected_ratings(self, user_id):
        expected_ratings = self.recommendations[user_id]
        expected_ratings = normalize(expected_ratings, axis=1, norm='max').tocsr()
        expected_ratings = expected_ratings.toarray().ravel()
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
