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
        self.expected_data = np.array([[[[ 0.92961609, 0, 0.18391881],
                                    [ 0, 0.56772503, 0.5955447]],

                                   [[ 0, 0, 0],
                                    [ 0.65356987, 0.74771481, 0]]],

                                  [[[ 0.0083883, 0, 0.29870371],
                                    [ 0, 0.80981255, 0.87217591]],

                                   [[ 0,  0,  0],
                                    [ 0.71745362, 0.46759901, 0]]]])


        self.affine = np.eye(4)
        self.affine[:, 3] = 1

        self.frame1 = np.random.random((2, 2, 3))
        self.frame2 = np.random.random((2, 2, 3))

        self.file1 = 'test_frame_0001.nii'
        self.file2 = 'test_frame_0002.nii'
        self.file_4d = 'test_4d.nii'
        self.mask_file = 'mask_test.nii'

        new_img = ni.Nifti1Image(self.frame1, self.affine)
        ni.save(new_img, self.file1) 
        new_img = ni.Nifti1Image(self.frame2, self.affine)
        ni.save(new_img, self.file2) 
        new_img = ni.Nifti1Image(self.mask, self.affine)
        ni.save(new_img, self.mask_file) 
        new_img = ni.Nifti1Image(np.array((self.frame1, self.frame2)), self.affine)
        ni.save(new_img, self.file_4d) 

    def tearDown(self):
        os.remove(self.file1)
        os.remove(self.file2)
        os.remove(self.mask_file)
        os.remove(self.file_4d)

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

    def test_pick_function(self):
        assert_equal(roi._pick_function(['test'], 'frames', None), roi.frame_data)
        assert_equal(roi._pick_function(['test'], '4d', None), roi.frame_data)
        assert_equal(roi._pick_function(['test'], 'frames_files', 'file.nii'), roi.frame_data)
        assert_equal(roi._pick_function(['test'], '4d_file', 'file.nii'), roi.frame_data)
        assert_raises(Exception, roi._pick_function, ['test'], 'frames_files', None)
        assert_raises(Exception, roi._pick_function, 'test', '4d_file', None)
        assert_equal(roi._pick_function(['test'], 'values', None), roi.frame_values)
        assert_equal(roi._pick_function(['test'], 'stats', None), roi.frame_stats)

        assert_equal(roi._pick_function('test', 'values', None), roi.extract_values)
        assert_equal(roi._pick_function('test', 'frames', None), roi.apply_mask)
        assert_equal(roi._pick_function('test', 'stats', None), roi.get_stats)

    def test_process_files(self):
        data = roi.process_files(roi.frame_data, [self.file1, self.file2], self.mask_file, 0)
        data_4d = roi.process_files(roi.apply_mask, self.file_4d, self.mask_file, 0)
        values = roi.process_files(roi.frame_values, [self.file1], self.mask_file, 0)
        stats = roi.process_files(roi.frame_stats, [self.file1], self.mask_file, 0)
        expected_data = np.array([[[[ 0.92961609, 0, 0.18391881],
                                    [ 0, 0.56772503, 0.5955447]],

                                   [[ 0, 0, 0],
                                    [ 0.65356987, 0.74771481, 0]]],

                                  [[[ 0.0083883, 0, 0.29870371],
                                    [ 0, 0.80981255, 0.87217591]],

                                   [[ 0,  0,  0],
                                    [ 0.71745362, 0.46759901, 0]]]])
        print data
        known_values = np.array([0.92961609, 0.18391881, 0.56772503, 0.5955447, 0.65356987, 0.74771481])
        known_stats = (0.3065074430565158, 0.34567164953488178)
        assert_almost_equal(data[0], self.expected_data)
        assert_almost_equal(data_4d[0], self.expected_data)
        assert_almost_equal(values[0][0], known_values)
        assert_almost_equal(stats[0][0], known_stats)

    def test_process_input(self):

        known_values = np.array([0.92961609, 0.18391881, 0.56772503, 0.5955447, 0.65356987, 0.74771481])
        known_stats = (0.3065074430565158, 0.34567164953488178)

        data = roi.process_input(self.file_4d, self.mask_file, 'data')
        assert_almost_equal(data[0], self.expected_data)
        values = roi.process_input(self.file_4d, self.mask_file, 'values')
        assert_almost_equal(values, known_values)

        outfile = roi.process_input(self.file_4d, self.mask_file, '4d_file', 'test_output.nii')
        out_data = ni.load(outfile).get_data()
        assert_equal(out_data, self.expected_data)

        outfiles = roi.process_input(self.file_4d, self.mask_file, 'frames_files', 'test_output.nii')
        assert_equal(self.expected_data[1], ni.load(outfiles[1]).get_data())

        files = [self.file1, self.file2]
        outfile = roi.process_input(files, self.mask_file, '4d_file', 'test_output.nii')
        out_data = ni.load(outfile).get_data()
        assert_equal(out_data, self.expected_data)

        outfiles = roi.process_input(files, self.mask_file, 'frames_files', 'test_output.nii')
        assert_equal(self.expected_data[1], ni.load(outfiles[1]).get_data())

        out_data = roi.process_input(files, self.mask_file, 'frames', None)
        assert_equal(self.expected_data, out_data[0])
        assert_equal(self.affine, out_data[1])
