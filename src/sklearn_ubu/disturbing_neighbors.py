from .homogeneous_ensemble import HomogeneousEnsemble
from .base_disturbing_neighbors import BaseDisturbingNeighbors
from sklearn.tree import DecisionTreeClassifier

class DisturbingNeighbors(HomogeneousEnsemble):
    """A Disturbing Neighbors.
    
    Disturbing neighbors is a multi-label ensemble, this method alters the
    normal training process of the base classifiers in an ensemble, improving
    their diversity and accuracy. DN creates new features using a 1-NN
    classifier, these characteristics are the 1-NN output plus a set of Boolean
    attributes indicated by the nearest neighbor.
    
    The 1-NN classifier is created using a small subset of training instances,
    chosen at random from the original set. The dimensions to calculate the
    Euclidean distance are also random. With these characteristics created when
    we train base classifiers with them, diversity increases.
    """
    def __init__(self,
                 base_estimator=DecisionTreeClassifier(),
                 n_estimators=10,
                 random_state=None,
                 estimator_params=tuple()):
        self.base_estimator = base_estimator
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.estimator_params = estimator_params

    def _validate_estimator(self):
        self.base_estimator_ = BaseDisturbingNeighbors(
                base_estimator=self.base_estimator)
