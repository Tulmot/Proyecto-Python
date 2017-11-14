"""   """

# Author: Eduardo Tubilleja Calvo

import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils import check_random_state
from sklearn.base import ClassifierMixin
from sklearn.base import BaseEstimator


class DisturbingNeighbors(BaseEstimator,ClassifierMixin):
    """A Disturbing Neighbors.

     Parameters
    ----------
    base_estimator : It is the classifier that we will use to train our data
        set, what it receives is either empty or an object, if it is empty by
        default the DecisionTreeClassifier is used.

    n_neighbors : They are the neighbors that we want to choose from the data
        set, by default if nothing happens, 10 are chosen.

    n_features : It is the size of the random sub-space, according to which
        the random features that we are going to use to train our
        classifier are chosen, by default it is 0.5, that is, half of the
        features are taken, if the value that is passed is greater than
        1, that number of features is taken.

    _rnd_dimensions : A Boolean random array, its size is equal to the number
        of features of the set, but then the number of TRUE values it contains
        will be equal to the value of the variable n_features, the TRUE values,
        indicate which features are chosen to evaluate the set.

    _rnd_neighbors : A random array of integers, the size of this array depends
        on the variable n_neighbors, will select random rows of the data set,
        is what we will call disturbing neighbors.

    """
    def __init__(self,
                 base_estimator=DecisionTreeClassifier(),
                 n_neighbors=10,
                 n_features=0.5,
                 random_state=None):
        self.base_estimator = base_estimator
        self.n_neighbors = n_neighbors
        self.n_features = n_features
        self.random_state = random_state
        self._rnd_dimensions = None
        self._rnd_neighbors = None
        
    def _calculate_features(self, X):
        """Calculamos el numero de caracteristicas que usaremos"""
        if self.n_features < 1:
            return round(X.shape[1]*self.n_features)
        else:
            return self.n_features

    def _random_boolean(self):
        """Calculamos un array random boolean que es el que nos indicara que
        caracteristicas que valoraremos"""
        self._rnd_dimensions = self.random_state.randint(0, 2, self.n_features)
        return self._rnd_dimensions.astype(bool)

    def _random_array(self, X):
        """Calculamos un array random para seleccionar unas instancias
        aleatorias"""
        tam = X.shape[0]
        return self.random_state.choice(tam, self.n_neighbors, replace=False)

    def _reduce_data(self, X):
        """Reducimos los datos obtenidos a las caracteristicas que vamos a
        evaluar, que seran las que hemos obtenido segun el array random
        boolean"""
        return X[:, self._rnd_dimensions]

    def _disturbing(self,_m_reduce):
        """Calculamos la matriz de los vecinos molestones."""
        print(_m_reduce)
        print(self._rnd_neighbors)
        m_disturbing=_m_reduce[self._rnd_neighbors,:]
        return m_disturbing

    def _nearest_neighbor(self,_m_reduce):
        """Calculamos los vecinos mas cercanos a las instancias escogidas
        antes aleatoriamente"""
        m_disturbing=self._disturbing(_m_reduce)
        euc_dis_func = lambda t: euclidean_distances([t],m_disturbing).argmin()
        dn_nn = lambda inst : np.apply_along_axis(euc_dis_func,1,[inst])
        m_nearest=np.apply_along_axis(dn_nn,1,_m_reduce)
        neighbors = lambda vec : np.concatenate((np.concatenate((np.zeros(vec), [1]), axis=0), np.zeros(len(m_disturbing)-vec-1)), axis=0)
        m_neighbors= np.apply_along_axis(neighbors,1,m_nearest)
        return m_neighbors

    def fit(self, X, y):
        """Build a Bagging ensemble of estimators from the training set (X, y).

        Parameters
        ----------
        X : It's a matrix of form = [n_instances, n_features]
            The training input samples. Sparse matrices are accepted only if
            they are supported by the base estimator.

        y : It's a matrix of form = [n_class]
            The target values (class labels in classification, real numbers in
            regression).

        Returns
        -------
        self : object
            Returns self.
        """
        self.random_state = check_random_state(self.random_state)
        self.n_features = self._calculate_features(X)
        self._rnd_dimensions = self._random_boolean()
        self._rnd_neighbors = self._random_array(X)
        _m_reduce = self._reduce_data(X)
        m_neighbors = self._nearest_neighbor(_m_reduce)
        m_train = np.concatenate((X, m_neighbors), axis=1)
        return self.base_estimator.fit(m_train, y)

    def predict(self, X):
        """Predict class for X.
        The predicted class of an input sample is computed as the class with
        the highest mean predicted probability.

        Parameters
        ----------
        X : It's a matrix of form = [n_instances, n_features]
            The training input samples. Sparse matrices are accepted only if
            they are supported by the base estimator.

        Returns
        -------
        y : It's a matrix of form = [n_class]
            The predicted classes.
        """
        x_reduce = self._reduce_data(X)
        m_neighbors = self._nearest_neighbor(x_reduce)
        m_train = np.concatenate((X, m_neighbors), axis=1)
        return self.base_estimator.predict(m_train)

    def predict_proba(self, X):
        """The predicted class probabilities of an input sample is computed as
        the mean predicted class probabilities of the base estimators in the
        ensemble.

         Parameters
        ----------
        X : It's a matrix of form = [n_instances, n_features]
            The training input samples. Sparse matrices are accepted only if
            they are supported by the base estimator.

        Returns
        -------
        p : It's a matrix of form = [n_samples, n_classes]
            The class probabilities of the input samples. The order of the
            classes corresponds to that in the attribute `classes_`.
        """
        x_reduce2= self._reduce_data(X)
        m_neighbors = self._nearest_neighbor(x_reduce2)
        m_train = np.concatenate((X, m_neighbors), axis=1)
        return self.base_estimator.predict_proba(m_train)
    
    def score(self, X, y, sample_weight=None):
        """Returns the mean accuracy on the given test data and labels.
        In multi-label classification, this is the subset accuracy
        which is a harsh metric since you require for each sample that
        each label set be correctly predicted.
        Parameters
        ----------
        X : array-like, shape = (n_samples, n_features)
            Test samples.
        y : array-like, shape = (n_samples) or (n_samples, n_outputs)
            True labels for X.
        sample_weight : array-like, shape = [n_samples], optional
            Sample weights.
        Returns
        -------
        score : float
            Mean accuracy of self.predict(X) wrt. y.
        """
        from sklearn.metrics import accuracy_score
        return accuracy_score(y, self.predict(X), sample_weight=sample_weight)
