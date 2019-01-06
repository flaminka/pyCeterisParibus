import unittest

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import euclidean_distances

from ceteris_paribus.gower import _normalize_mixed_data_columns, gower_distances, _calc_range_mixed_data_columns, \
    _gower_dist
from ceteris_paribus.select_data import select_sample, select_neighbours


class TestSelect(unittest.TestCase):

    def setUp(self):
        self.x = np.array([[1, 0, 1], [2, 0, 2], [10, 2, 10], [1, 0, 2]])
        self.y = np.array([11, 12.1, 13.2, 10.5])

    def test_select_sample(self):
        (_, m) = self.x.shape
        size = 2
        sample = select_sample(self.x, n=size)
        self.assertEqual(sample.shape, (size, m))

    def test_select_sample_2(self):
        sample = select_sample(self.x, n=1)
        self.assertIn(sample[0], self.x)

    def test_select_sample_3(self):
        sample_x, sample_y = select_sample(self.x, self.y, n=1)
        pos = list(self.y).index(sample_y[0])
        self.assertSequenceEqual(list(sample_x[0]), list(self.x[pos]))

    def test_select_sample_4(self):
        sample_x = select_sample(self.x, n=300)
        self.assertEqual(len(sample_x), len(self.x))

    def test_select_neighbours(self):
        neighbours = select_neighbours(self.x, self.x[0], dist_fun=euclidean_distances, n=1)
        neighbours2 = select_neighbours(self.x, self.x[0], dist_fun='gower', n=1)
        self.assertSequenceEqual(list(neighbours[0]), list(self.x[0]))
        self.assertSequenceEqual(list(neighbours2[0]), list(self.x[0]))

    def test_select_neighbours_2(self):
        (_, m) = self.x.shape
        size = 3
        neighbours = select_neighbours(self.x, np.array([4, 3, 2]), dist_fun=euclidean_distances, n=size)
        self.assertEqual(neighbours.shape, (size, m))
        neighbours2 = select_neighbours(self.x, np.array([4, 3, 2]), dist_fun='gower', n=size)
        self.assertEqual(neighbours2.shape, (size, m))

    def test_select_neighbours_3(self):
        sample_x, sample_y = select_neighbours(self.x, np.array([4, 3, 2]), y=self.y, n=3)
        pos = list(self.y).index(sample_y[1])
        self.assertSequenceEqual(list(sample_x[1]), list(self.x[pos]))

    def test_select_neighbours_4(self):
        # it logs warning
        sample_x = select_neighbours(self.x, np.array([4, 3, 2]), n=300)
        self.assertEqual(len(sample_x), len(self.x))


class TestGower(unittest.TestCase):

    def setUp(self):
        self.X = pd.DataFrame(
            {
                'age': [21, 21, 19, 30, 21, 21, 19, 30],
                'gender': ['M', 'M', 'N', 'M', 'F', 'F', 'F', 'F'],
                'civil_status': ['MARRIED', 'SINGLE', 'SINGLE', 'SINGLE', 'MARRIED', 'SINGLE', 'WIDOW', 'DIVORCED'],
                'salary': [3000.0, 1200.0, 32000.0, 1800.0, 2900.0, 1100.0, 10000.0, 1500.0],
                'children': [True, False, True, True, True, False, False, True],
                'available_credit': [2200, 100, 22000, 1100, 2000, 100, 6000, 2200]
            })
        self.arr = _normalize_mixed_data_columns(self.X)
        self.observation = [22, 'F', 'DIVORCED', 2000, False, 1000]
        self.observation = _normalize_mixed_data_columns(self.observation)
        self.first = _normalize_mixed_data_columns(self.X.iloc[0])
        self.ranges = _calc_range_mixed_data_columns(self.arr, self.observation, self.X.dtypes)
        self.X_numeric = np.array([
            [21, 21, 19, 30, 21, 21, 19, 30],
            [3000.0, 1200.0, 32000.0, 1800.0, 2900.0, 1100.0, 10000.0, 1500.0],
            [2200, 100, 22000, 1100, 2000, 100, 6000, 2200]
        ]).T

    def test_normalize_1(self):
        self.assertEqual(self.X.shape, self.arr.shape)

    def test_ranges_1(self):
        np.testing.assert_array_almost_equal(self.ranges, np.array([11, 0, 0, 30900, 0, 21900]), decimal=2)

    def test_gower_distances_1(self):
        distances = gower_distances(self.X, self.X.iloc[0])
        np.testing.assert_array_almost_equal(distances,
                                             np.array([0, 0.3590, 0.6707, 0.3178, 0.1687, 0.5262, 0.5969, 0.4777]),
                                             decimal=3)

    def test_gower_distances_2(self):
        distances = gower_distances(self.X_numeric, self.X_numeric[0])
        np.testing.assert_array_almost_equal(distances,
                                             np.array([0, 0.0513, 0.6748, 0.3024, 0.0041, 0.05245, 0.1939, 0.2889]),
                                             decimal=3)

    def test_gower_distances_3(self):
        observation_out_of_range = [21, 40000, -100]
        distances = gower_distances(self.X_numeric, observation_out_of_range)
        self.assertEqual(distances.shape, (8,))
        np.testing.assert_array_almost_equal(distances[:2],
                                             np.array([0.3517, 0.3356]), decimal=4)

    def test_gower_dist_1(self):
        # test dist(a, a) == 0
        distance = _gower_dist(self.observation, self.observation, self.ranges, self.X.dtypes)
        self.assertEqual(distance, 0.0)

    def test_gower_dist_2(self):
        # test symmetry
        distance1 = _gower_dist(self.observation, self.first, self.ranges, self.X.dtypes)
        distance2 = _gower_dist(self.first, self.observation, self.ranges, self.X.dtypes)
        self.assertAlmostEqual(distance1, distance2, delta=0.0001)

    def test_gower_dist_3(self):
        distance = _gower_dist(self.observation, self.first, self.ranges, self.X.dtypes)
        self.assertAlmostEqual(distance, 0.52967, delta=0.0001)
