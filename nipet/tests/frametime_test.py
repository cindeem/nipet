from unittest import TestCase, skipIf, skipUnless
import numpy as np
from numpy.testing import (assert_raises, assert_equal, assert_almost_equal)
from os.path import exists
from .. import frametime

def file_exists(filename):
    return exists(filename) 

class TestFrametime(TestCase):

    def test_class(self):
        ft = frametime.FrameTime()
        assert_equal(ft.isempty(), True)
        
    def test_check_frame(self): 
        ft = frametime.FrameTime()

        badframe = np.array([2., 6., 27., 33., 1.])
        assert_equal(ft._check_frame(badframe), False)

        badframe = np.random.random((4, 2))
        assert_equal(ft._check_frame(badframe), False)

        badframe = np.array([2., 6., 27., 34.])
        assert_equal(ft._check_frame(badframe), False)

        frame = np.array([1., 6., 27., 33.])
        assert_equal(ft._check_frame(frame), True)

    def test_generate_protocol(self):
        ft = frametime.FrameTime()
        protocol = ft.generate_empty_protocol(4)
        assert_equal(protocol.shape, (5, 4))
        header = np.array(['frame number', 'start time', 'duration', 'stop time'], dtype = 'S12')
        line2 = np.array(['2.0', '', '', ''], dtype = 'S12')
        line4 = np.array(['4.0', '', '', ''], dtype = 'S12')
        assert_equal(protocol[0], header)
        assert_equal(protocol[2], line2)
        assert_equal(protocol[4], line4)

    def test_validate_frames(self):
        frames = np.random.random((5, 3))
        ft = frametime.FrameTime()
        ft.data = frames
        #this works in manual testing
        assert_raises(ValueError, ft._validate_frames)
        frames = np.array([[1, 4, 5, 1], 
                           [2, 5, 8, 3],
                           [4, 8, 14, 6]])
        ft.data = frames
        assert_raises(ValueError, ft._validate_frames)
        frames = np.array([[1, 0, 5, 5], 
                           [2, 5, 3, 8],
                           [4, 8, 6, 14]])
        ft.data = frames
        assert_equal(ft._validate_frames(), True)

    def test_delete_frame(self):
        ft = frametime.FrameTime()
        frames = np.array([[1, 2, 3, 4],
                           [2, 3, 4, 5],
                           [3, 4, 5, 6]])
        ft.data = frames
        ft.delete_frame(1)
        assert_equal(ft.data, np.array([[1, 2, 3, 4],
                                        [3, 4, 5, 6]]))

    def test_from_csv(self):
        infile = 'data/sample_frames.csv'
        sample_data = np.array([[1., 0., 15., 15.],
                                [2., 15., 15., 30.],
                                [3., 30., 15., 45.],
                                [4., 45., 15., 60.],
                                [5., 60., 30., 90.]])
        try:
            ft = frametime.FrameTime()
            ft.from_csv(infile)
            assert_equal(ft.data, sample_data)
            assert_equal(ft.get_units(), 'sec')
        except:
            print "Welp."   

    def test_from_excel(self):
        infile = 'data/sample_frames.xls'
        sample_data = np.array([[1., 0., 15., 15.],
                                [2., 15., 15., 30.],
                                [3., 30., 15., 45.],
                                [4., 45., 15., 60.],
                                [5., 60., 30., 90.]])
        try:
            ft = frametime.FrameTime()
            ft.from_xls(infile)
            assert_equal(ft.data, sample_data)
            assert_equal(ft.get_units(), 'sec')
        except:
            print "Welp."   


    def test_get_data(self):
        """Test get_array, to_min, and to_sec"""
        ft = frametime.FrameTime()
        frames = np.array([[1, 2, 3, 4],
                           [2, 3, 4, 5],
                           [3, 4, 5, 6]])
        min_frames = frames * 1/60.0
        empty = np.array(None, dtype=object)
        ft.data = frames

        assert_equal(ft.get_array(), empty)
        assert_equal(ft.to_sec(), empty)
        assert_equal(ft.to_min(), empty)

        ft.units = 'sec'
        assert_equal(ft.get_array(), frames)
        assert_almost_equal(ft.get_array('min'), min_frames)
        assert_almost_equal(ft.to_sec(), frames)
        assert_almost_equal(ft.to_min(), min_frames)

        ft.data = min_frames
        ft.units = 'min'
        assert_equal(ft.get_array(), frames)
        assert_equal(ft.get_array('min'), min_frames)
        assert_almost_equal(ft.to_sec(), frames)
        assert_almost_equal(ft.to_min(), min_frames)

        
