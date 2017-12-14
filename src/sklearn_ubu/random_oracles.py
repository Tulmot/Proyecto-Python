from homogeneous_ensemble import HomogeneousEnsemble
from base_random_oracles import BaseRandomOracles

class RandomOracles(HomogeneousEnsemble):

    def __init__(self,
                 base_estimator_=BaseRandomOracles(),
                 n_estimators=10,
                 random_state=None,
                 estimator_params=tuple()):
        self.base_estimator_ = base_estimator_
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.estimator_params = estimator_params