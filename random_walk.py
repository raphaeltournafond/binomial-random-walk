import random

import numpy as np


class RandomWalk:
    """
    A RandomWalk object in one dimension
    """

    def __init__(self, inner=10, outer=1000, q=0.5, z=0):
        """
        Initialise the random walk class
        :param inner: number of moves during a repetition
        :param outer: number of repetitions
        :param q: probability trigger (probability the attacker finds the next block)
        :param z: start offset (number of attacker's block behind)
        """
        self._inner = inner
        self._outer = outer
        self._q = q
        self._z = z
        self._dict = None
        self._values = None
        self._heights = None

    def get_dict(self):
        return self._dict

    def get_values(self):
        return self._values

    def get_heights(self):
        return self._heights

    def get_zero_or_above_value_index(self):
        """
        :return: the index when the value go above 0, None if don't go above
        """
        for i in range(len(self._values)):
            if self._values[i] >= 0:
                return i
        return None

    def get_success(self):
        i = self.get_zero_or_above_value_index()
        if i:
            return 1-((self._outer - sum(self._heights[i:])) / self._outer)
        return 0

    def compute(self):
        """
        Compute the list of values and heights, and the complete dictionary
        """
        dict = self._compute_values(self._compute_stopping_points())
        self._values = list(dict.keys())
        self._heights = list(dict.values())
        self._dict = dict

    def _compute_values(self, stopping_points: list):
        """
        Generate x-axis values dictionnary with their reached times number
        :param stopping_points: unsorted stopping points result for each outer run
        :return: dictionnary of stop point -> number time reached
        """
        values = {}
        stopping_points.sort()
        for point in stopping_points:
            if point in values:
                values[point] += 1
            else:
                values[point] = 1
        return values

    def _compute_stopping_points(self):
        """
        Compute all the random walks values
        :return: array of every repetition end position
        """
        stopping_points = []
        for _ in range(self._outer):
            stopping_points.append(self._compute_k())
        return stopping_points

    def _compute_outer(self):
        """
        Compute all the random walks values
        :return: array of every repetition end position
        """
        fn = []
        for i in range(self._outer):
            fn.append(self._compute_k())
        return fn

    def _compute_k(self):
        """
        Compute a single 1D random walk
        :return: the random walk x coordinate
        """
        k = -self._z
        highest = k
        for _ in range(self._inner):
            if random.uniform(0, 1) <= self._q:
                k += 1
                if highest < k:
                    highest = k
            else:
                k -= 1
        return highest


class RandomWalk2D(RandomWalk):
    """
    RandomWalk 2D extension
    """

    def __init__(self, inner=10, outer=1000, q=0.5, z=0):
        """
        Initialise the random walk class
        :param inner: number of moves during a repetition
        :param outer: number of repetitions
        :param q: probability trigger (probability the attacker finds the next block)
        :param z: start offset (number of attacker's block behind)
        """
        super().__init__(inner, outer, q, z)

    def get_x_values(self):
        """
        :return: the list of all the x coordinates
        """
        return [x for x, y in self._values]

    def get_y_values(self):
        """
        :return: the list of all the y coordinates
        """
        return [y for x, y in self._values]

    def get_zero_or_above_value_index(self):
        """
        :return: the index when the value go above (0, 0), None if don't go above
        """
        for i in range(len(self._values)):
            if self._values[i][0] >= 0 and self._values[i][1] >= 0:
                return i
        return None

    def get_matrix(self):
        """
        Compute the x, y, z matrices
        :return: ordered and sorted x, y and z matrices (see examples)
        """
        # clean lists
        # example : x = [1, -2, 3]; y = [-6, 4]
        x = sorted(list(set(self.get_x_values())))
        y = sorted(list(set(self.get_y_values())))

        # create x matrix
        # [[1, -2, 3], [1, -2, 3]]
        mx = []
        for i in range(len(y)):
            mx.append(x)
        mx = np.matrix(mx)

        # create y matrix
        # [[-6, -6, -6], [4, 4, 4]]
        my = []
        for i in range(len(y)):
            my.append([y[i]] * len(x))
        my = np.matrix(my)

        # create z matrix
        # get matrix size
        ys = mx.shape[0]
        xs = mx.shape[1]
        # fill a matrix with zeros (not reached)
        mz = np.zeros((ys, xs))
        for i in range(ys):
            for j in range(xs):
                mxi = mx.item((i, j))
                myi = my.item((i, j))
                # if coordinate has been reached
                if (mxi, myi) in self._dict:
                    # add it to the matrix
                    mz.itemset((i, j), self._dict.get((mxi, myi)))
        return mx, my, mz

    def get_below_zero_matrix(self):
        """
        :return: get the matrix values on corrdinates below (0, 0), example: (-4, 0), (4, -1), (-2, -8)
        """
        x, y, z = self.get_matrix()
        # create new z matrix
        # get matrix size
        ys = x.shape[0]
        xs = y.shape[1]
        # fill a matrix with zeros (not reached)
        new_z = np.empty((ys, xs))
        new_z[:] = np.nan
        for i in range(ys):
            for j in range(xs):
                xi = x.item((i, j))
                yi = y.item((i, j))
                # if below 0
                if xi < 0 or yi < 0:
                    # add it to the matrix
                    new_z.itemset((i, j), self._dict.get((xi, yi)))
        return new_z

    def get_above_zero_matrix(self):
        """
        :return: get the matrix values on corrdinates above (0, 0), example: (0, 0), (4, 1), (2, 0)
        """
        x, y, z = self.get_matrix()
        # create new z matrix
        # get matrix size
        ys = x.shape[0]
        xs = y.shape[1]
        # fill a matrix with zeros (not reached)
        new_z = np.empty((ys, xs))
        new_z[:] = np.nan
        for i in range(ys):
            for j in range(xs):
                xi = x.item((i, j))
                yi = y.item((i, j))
                # if below 0
                if xi >= 0 and yi >= 0:
                    # add it to the matrix
                    new_z.itemset((i, j), self._dict.get((xi, yi)))
        return new_z

    def compute(self):
        """
        Compute the list of values and heights, and the complete dictionary
        """
        first   = super()._compute_stopping_points()
        second  = super()._compute_stopping_points()
        dict = self._compute_values_2d(first, second)
        self._values = list(dict.keys())
        self._heights = list(dict.values())
        self._dict = dict

    def _compute_values_2d(self, first: list, second: list):
        """
        Generate x-axis values dictionnary with their reached times number
        :param first: unsorted stopping points result for each outer run on x axis
        :param second: unsorted stopping points result for each outer run on y axis
        :return: dictionnary of stop point (x, y) -> number time reached
        """
        values = {}
        for i in range(len(first)):
            key = (first[i], second[i])
            if key in values:
                values[key] += 1
            else:
                values[key] = 1
        values = dict(sorted(values.items()))
        return values