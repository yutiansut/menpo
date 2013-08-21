import abc
import numpy as np
from sklearn.decomposition import PCA as SklearnPCA
from pybug.model.base import StatisticalModel


# TODO: better document what a linear model does.
class LinearModel(StatisticalModel):
    r"""
    Abstract base class representing a linear model.
    """

    __metaclass__ = abc.ABCMeta

    def instance(self, weightings):
        """
        Creates a new instance of the model using the first ``len(weightings)``
        components.

        Parameters
        ----------
        weightings : (N,) ndarray
            The weightings that should be used by the model to create an
            instance of itself.

        Returns
        -------
        instance : ``self.sample_data_class``
            An instance of the model. Created via a linear combination of the
            model vectors and the ``weightings``.
        """
        return self.template_sample.from_vector(self._instance(weightings))

    @abc.abstractmethod
    def _instance(self, weightings):
        """
        Creates a new instance of the model using the first len(weightings)
        components.

        Parameters
        ----------
        weightings : (N,) ndarray
            The weightings that should be used by the model to create an
            instance of itself.

        Returns
        -------
        instance : (N,) ndarray
            The instance vector.
        """
        pass

    def project(self, novel_instance):
        """
        Projects the ``novel_instance`` onto the model, retrieving the optimal
        linear weightings.

        Parameters
        -----------
        novel_instance : :class:`pybug.base.Vectorizable`
            A novel instance.

        Returns
        -------
        projected : (N,)
            A vector of optimal linear weightings
        """
        return self._project(novel_instance.as_vector())


    @abc.abstractmethod
    def _project(self, novel_vectorized_instance):
        """
        Projects the novel_vectorized_instance onto the model, retrieving the
        optimal linear reconstruction weights

        Parameters
        -----------
        novel_instance : (N,) ndarray
            A novel instance.

        Returns
        -------
        projected : (N,)
            A vector of optimal linear weightings
        """
        pass

    def reconstruct(self, novel_instance, n_components=None):
        """
        Project a ``novel_instance`` onto the linear space and rebuild from the
        weightings found.

        Syntactic sugar for:

            >>> pca.instance(pca.project(novel_instance)[:n_components])

        but faster, as it avoids the conversion that takes place each time.

        Parameters
        ----------
        novel_instance : :class:`pybug.base.Vectorizable`
            A novel instance of Vectorizable
        n_components : int, optional
            The number of components to use in the reconstruction.

            Default: ``weightings.shape[0]``

        Returns
        -------
        reconstructed : ``self.sample_data_class``
            The reconstructed object.
        """
        vectorized_reconstruction = self._reconstruct(
            novel_instance.as_vector(), n_components)
        return novel_instance.from_vector(vectorized_reconstruction)

    def _reconstruct(self, novel_vectorized_instance, n_components=None):
        """
        Project a flattened ``novel_instance`` onto the linear space and
        rebuild from the weightings found.

        Syntactic sugar for:

            >>> pca._instance(pca._project(novel_vectorized_instance)[:n_components])

        Parameters
        ----------
        novel_vectorized_instance : (N, ) ndarray
            A vectorized novel instance to project
        n_components : int, optional
            The number of components to use in the reconstruction

            Default: ``weightings.shape[0]``

        Returns
        -------
        reconstructed : (N,) ndarray
            The reconstructed vector.
        """
        weightings = self._project(novel_vectorized_instance)
        if n_components is not None:
            weightings = weightings[:n_components]
        return self._instance(weightings)

    def project_out(self, novel_instance, n_components):
        """
        Returns a version of ``novel_instance`` where all the information in
        the first ``n_components`` of the model has been projected out.

        Parameters
        ----------
        novel_instance : :class:`pybug.base.Vectorizable`
            A novel instance.
        n_components : int, optional
            The number of components to utilize from the model

            Default: ``weightings.shape[0]``

        Returns
        -------
        projected_out : ``self.sample_data_class``
            A copy of ``novel instance``, with all features of the model
            projected out.
        """
        vectorized_instance = self._project_out(novel_instance.as_vector(),
                                                n_components)
        return novel_instance.from_vector(vectorized_instance)

    @abc.abstractmethod
    def _project_out(self, novel_vectorized_instance, n_components):
        """
        Returns a version of ``novel_instance`` where all the information in
        the first ``n_components`` of the model has been projected out.

        Parameters
        ----------
        novel_vectorized_instance : (N,) ndarray
            A novel vector.
        n_components : int, optional
            The number of components to utilize from the model

            Default: ``weightings.shape[0]``

        Returns
        -------
        projected_out : (N,) ndarray
            A copy of ``novel_vectorized_instance`` with all features of the
            model projected out.
        """
        pass


class SimilarityModel(LinearModel):
    """
    Re-parametrization of the similarity transform as a linear model.

    Parameters
    ----------
    reference : :class:`pybug.shape.base.PointCloud`
        A pointcloud to which the similarity transform will be applied to.
    """

    # TODO: remove 2d real data assumption
    def __init__(self, reference):
        self.reference = reference
        self.samples = [self.reference]
        self.n_components = 4
        self.components = self._compute_similarity_components(reference)

    def _compute_similarity_components(self, reference):
        scale = self.reference
        rotation = self.reference.points[:, [1, 0]]
        rotation[:, 1] *= -1
        x_translation = np.zeros_like(reference.points)
        x_translation[:, 1] += 1
        y_translation = x_translation[:, [1, 0]]
        return np.linalg.qr(
            np.array([scale.as_vector(), rotation.flatten(),
                      x_translation.flatten(), y_translation.flatten()]).T)[0]

    def equivalent_similarity_transform(self, weights):
        """
        Returns a :class:`pybug.transform.affine.SimilarityTransform` that
        performs the exact same transformation on the model reference as
        creating an instance of the model using the given ``weights``.

        Parameters
        ----------
        weights: (N,) ndarray
            The weights that should be used in the model.

        Returns
        -------
        transform : :class:`pybug.transform.affine.SimilarityTransform`
            The equivalent transform given the ``weights``.
        """
        return self._equivalent_similarity_transform(self.instance(weights))

    def _equivalent_similarity_transform(self, novel_instance):
        """
        Returns a :class:`pybug.transform.affine.SimilarityTransform` relating
        the given ``novel_instance`` with the model reference.

        Parameters
        ----------
        novel_instance : (N,) ndarray
            A vectorized novel instance of the model.

        Returns
        -------
        transform : :class:`pybug.transform.affine.SimilarityTransform`
            The equivalent transform given the ``novel_instance``.
        """
        ind = [0, 10, 20]
        s = self.reference.points[ind]
        t = novel_instance.points[ind]

        # sik
        # ^^^
        # ||\- the k'th point
        # ||
        # |vector between end (j or k) and i
        # source [target]
        # if i is absent, it is the position of the ijk point.
        # (not a _vector_ between points)
        # get vectors ij ik for source and target
        sij, sik = s[1] - s[0], s[2] - s[0]
        tij, tik = t[1] - t[0], t[2] - t[0]

        # source vertex positions
        si, sj, sk = s[0], s[1], s[2]
        ti = t[0]

        d = (sij[0] * sik[1]) - (sij[1] * sik[0])

        c_x = (sik[1] * tij - sij[1] * tik) / d
        c_y = (sij[0] * tik - sik[0] * tij) / d
        c_t = ti + (tij * (si[1] * sik[0] - si[0] * sik[1]) +
                    tik * (si[0] * sij[1] - si[1] * sij[0])) / d
        ht = np.eye(3)
        ht[:2, 0] = c_x
        ht[:2, 1] = c_y
        ht[:2, 2] = c_t

        return SimilarityTransform(ht)

    def _instance(self, weights):
        if weights.shape[0] > self.n_components:
            raise Exception(
                "Number of weighs cannot be greater than {}".format(
                    self.n_components))
        elif weights.shape[0] < self.n_components:
            full_weights = np.zeros(self.n_components)
            full_weights[:weights.shape[0]] = weights
            weights = full_weights
        return self.reference.as_vector() + np.dot(self.components, weights)

    def _project(self, novel_vectorized_instance):
        return np.dot(self.components.T, (novel_vectorized_instance -
                                          self.reference.as_vector()))

    def _project_out(self, novel_vectorized_instance, n_components):
        #TODO Implement project_out on SimilarityModel
        pass


#TODO: give a description of what it means to be a PCA model
class PCAModel(LinearModel):
    """
    A Linear model based around PCA. Automatically mean centres the input
    data.

    Parameters
    ----------
    samples: list of :class:`pybug.base.Vectorizable`
        List of samples to build the model from.
    n_components: int, optional
        The number of components to internally keep.

        .. note::

            The number of components utilized in the model can be
            curtailed on invocation of methods like reconstruct and instance -
            setting a low number of components here permanently removes other
            components, and should only be used as a memory and performance
            saving measure.
    """

    def __init__(self, samples, n_components=None):
        """

        """
        self.samples = samples
        self.n_samples = len(samples)
        self.n_features = len(samples[0].as_vector())
        self.n_components = n_components
        if self.n_components is None:
            # -1 to prevent us from getting noise in the final component
            self.n_components = min(self.n_samples, self.n_features) - 1
        # flatten one sample to find the n_features we need

        # create and populate the data matrix
        data = np.zeros((self.n_samples, self.n_features))
        for i, sample in enumerate(self.samples):
            data[i] = sample.as_vector()

        # build the SKlearn PCA passing in the number of components.
        self._pca = SklearnPCA(n_components=self.n_components)
        self._pca.fit(data)

    @property
    def explained_variance(self):
        """
        Total variance explained by each of the components.

        :type: (``n_components``,) ndarray
        """
        return self._pca.explained_variance_

    @property
    def explained_variance_ratio(self):
        """
        Percentage of variance explained by each of the components.

        :type: (``n_components``,) ndarray
        """
        return self._pca.explained_variance_ratio_

    @property
    def mean(self):
        """
        The mean of the sample vectors.

        :type: ``self.sample_data_class``
        """
        return self.template_sample.from_vector(self._mean)

    @property
    def _mean(self):
        """
        The mean vector of the samples.

        :type: (N,) ndarray
        """
        return self._pca.mean_

    @property
    def components(self):
        """
        The principal components.

        :type: (``n_components``, ``n_features``) ndarray
        """
        return self._pca.components_

    @property
    def jacobian(self):
        jac = self.components.reshape((self.n_components,
                                       -1,
                                       self.template_sample.n_dims))
        return jac.swapaxes(0, 1)

    def _instance(self, weightings):
        if weightings.shape[0] > self.n_components:
            raise Exception(
                "Number of weightings cannot be greater than {}".format(
                    self.n_components))
        elif weightings.shape[0] < self.n_components:
            full_weightings = np.zeros(self.n_components)
            full_weightings[:weightings.shape[0]] = weightings
            weightings = full_weightings
        return self._pca.inverse_transform(
            weightings.reshape((1, -1))).flatten()

    def _project(self, novel_vectorized_instance):
        return self._pca.transform(
            novel_vectorized_instance.reshape((1, -1))).flatten()

    def _project_out(self, novel_vectorized_instance, n_components):
        #TODO Implement project_out on PCAModel
        pass
