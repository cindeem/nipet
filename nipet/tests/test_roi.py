from unittest import TestCase, skipIf, skipUnless
import numpy as np
from numpy.testing import (assert_raises, assert_equal, assert_almost_equal)
from os.path import exists, join, split, abspath
import nibabel as ni
import os
from .. import roi

class TestROI(TestCase):
    
    def setUp(self):
        self.data = np.array([[[0, 2, 3], [4, 5, np.nan]],
                         [[1, 3, 5], [2, 4, 7]]])

        self.mask = np.array([[[1, 0, 1], [0, 1, 1]],
                         [[0, 0, 0], [1, 1, 0]]])
        
        np.random.seed(12345)

        self.affine = np.eye(4)
        self.affine[:, 3] = 1

        self.frame1 = np.random.random((2, 2, 3))
        self.frame2 = np.random.random((2, 2, 3))

        self.file1 = 'test_frame_0001.nii'
        self.file2 = 'test_frame_0002.nii'
        self.mask_file = 'mask_test.nii'

        new_img = ni.Nifti1Image(self.frame1, self.affine)
        ni.save(new_img, self.file1) 
        new_img = ni.Nifti1Image(self.frame2, self.affine)
        ni.save(new_img, self.file2) 
        new_img = ni.Nifti1Image(self.mask, self.affine)
        ni.save(new_img, self.mask_file) 

    def tearDown(self):
        os.remove(self.file1)
        os.remove(self.file2)

    def test_mask_array(self):
        data, mask = self.data, self.mask

        m_data = roi.mask_array(data, mask)

        expected_mask = np.array([[[True, True, False], [True, False, True]],
                                  [[True, True, True], [False, False, True]]])

        assert_equal(m_data.data, data)
        assert_equal(m_data.mask, expected_mask)
        assert_equal(m_data.fill_value, 0)

        np.random.seed(12345)
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
        data = roi.frame_data(self.file1, self.mask_file, 0)
        expected_data = np.array([[[ 0.92961609, 0, 0.18391881],
                                   [ 0, 0.56772503, 0.5955447]],

                                  [[ 0, 0, 0],
                                   [ 0.65356987, 0.74771481, 0]]])
        assert_almost_equal(data, expected_data)

    
    def test_frame_values(self):
        values = roi.frame_values(self.file1, self.mask_file, 0)
        print values
        known_values = np.array([0.92961609, 0.18391881, 0.56772503, 0.5955447, 0.65356987, 0.74771481])
        assert_almost_equal(values, known_values)

    def test_frame_stats(self):
        stats = roi.frame_stats(self.file1, self.mask_file, 0)
        known_stats = (0.3065074430565158, 0.34567164953488178)
        assert_equal(stats, known_stats)

    def test_process_input(self):
        raise Exception('test not written')

    def test_return_output(self):
        raise Exception('test not written')
