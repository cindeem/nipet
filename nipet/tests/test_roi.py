from unittest import TestCase, skipIf, skipUnless
import numpy as np
from numpy.testing import (assert_raises, assert_equal, assert_almost_equal)
from os.path import exists, join, split, abspath
import os
from .. import roi

class TestROI(TestCase):
    
    def setUp(self):
        self.data = np.array([[[np.nan, 2, 3], [4, 5, np.nan]],
                         [[1, 3, 5], [2, 4, 7]]])

        self.mask = np.array([[[1, 0, 1], [0, 1, 1]],
                         [[0, 0, 0], [1, 1, 0]]])
        

    def test_mask_array(self):
        data, mask = self.data, self.mask

        m_data = roi.mask_array(data, mask)

        expected_mask = np.array([[[True, True, False], [True, False, True]],
                                  [[True, True, True], [False, False, True]]])

        assert_equal(m_data.data, data)
        assert_equal(m_data.mask, expected_mask)
        assert_equal(m_data.fill_value, 0)

        data = np.random.random((3, 3, 3))
        mask = np.random.random_integers(0, 1, (3, 3, 3))

        masked_data = np.ma.MaskedArray(data, mask=mask, fill_value = -1)
        inverted_mask = mask < 1
        m_data = roi.mask_array(data, inverted_mask, -1)
        assert_equal(masked_data, m_data)

    def test_apply_mask(self):
        data, mask = self.data, self.mask

        expected_output = np.array([[[0, 0, 3], [0, 5, 0]],
                                    [[0, 0, 0], [2, 4, 0]]])
        output = roi.apply_mask(data, mask, 0)
        print expected_output
        print output
        assert_equal(expected_output, roi.apply_mask(data, mask, 0))

    def extract_values(self):
        data, mask = self.data, self.mask

        expected_output = np.array([2, 3, 4, 5, 1, 3, 5, 2, 4, 7])
        assert_equal(extract_values(data, mask, 0), expected_output)

    def test_reslice_mask(self):
        raise Exception('test not written')

    def test_frame_data(self):
        raise Exception('test not written')
    
    def test_frame_values(self):
        raise Exception('test not written')

    def test_frame_stats(self):
        raise Exception('test not written')

    def test_process_input(self):
        raise Exception('test not written')
