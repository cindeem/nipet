from unittest import TestCase, skipIf, skipUnless
import numpy as np
from numpy.testing import (assert_raises, assert_equal, assert_almost_equal)
from os.path import exists, join, split, abspath
import os
from .. import frametime
from ..frametime import DataError, FrameError

def file_exists(filename):
    return exists(filename) 

class TestFrametime(TestCase):

    def test_class(self):
        ft = frametime.FrameTime()
        assert_equal(ft.isempty(), True)
        assert_equal(ft.units, None)
        ft.set_units('sec')
        assert_equal(ft.units, 'sec')

    def test_guess_units(self):
        sec = np.array([[1, 0, 3600, 3600],
                        [2, 3600, 3600, 7200]])
        assert_equal(frametime.guess_units(sec), 'sec')
        min = np.array([[1, 0, 36, 36],
                        [2, 36, 36, 72]])
        assert_equal(frametime.guess_units(min), 'min')
        
    def test_correct_data_order(self):
        ft = frametime.FrameTime()
        ft.set_units('sec')
        good = np.array([[1, 0, 15, 15],
                         [2, 15, 15, 30]])
        bad = np.array([[1, 0, 15, 15],
                        [2, 15, 30, 15]])
        assert_equal(good, ft.correct_data_order(good)) 
        assert_equal(good, ft.correct_data_order(bad)) 

    def test_check_frame(self): 
        ft = frametime.FrameTime()
        ft.set_units('sec')

        badframe = np.array([2., 6., 27., 33., 1.])
        assert_raises(FrameError, ft._check_frame, badframe)

        badframe = np.random.random((4, 2))
        assert_raises(FrameError, ft._check_frame, badframe)

        badframe = np.array([2., 6., 27., 34.])
        assert_raises(FrameError, ft._check_frame, badframe)

        frame = np.array([1., 6., 33., 27.])
        assert_equal(ft._check_frame(frame), True)

    def test_generate_protocol(self):
        ft = frametime.FrameTime()
        ft.set_units('sec')
        rows = 4
        protocol = ft.generate_empty_protocol(rows)
        assert_equal(protocol.shape, (rows, 4))
        line2 = np.array([2.0, np.nan, np.nan, np.nan])
        line4 = np.array([4.0, np.nan, np.nan, np.nan])
        assert_equal(protocol[2 - 1], line2)
        assert_equal(protocol[4 - 1], line4)
        ft.from_array(protocol, 'sec')

    def test_validate_frames(self):
        frames = np.random.random((5, 3))
        ft = frametime.FrameTime()
        ft.set_units('sec')
        ft.data = frames
        #this works in manual testing
        assert_raises(FrameError, ft._validate_frames)
        frames = np.array([[1, 4, 5, 1], 
                           [2, 5, 8, 3],
                           [4, 9, 14, 6]])
        ft.data = frames
        assert_raises(FrameError, ft._validate_frames)
        frames = np.array([[1, 0, 5, 5], 
                           [2, 5, 8, 3],
                           [3, 9, 14, 5]])
        ft.data = frames
        assert_equal(ft._validate_frames(), True)

    def test_delete_frame(self):
        ft = frametime.FrameTime()
        ft.set_units('sec')
        frames = np.array([[1, 2, 3, 4],
                           [2, 3, 4, 5],
                           [3, 4, 5, 6]])
        ft.data = frames
        ft.delete_frame(1)
        assert_equal(ft.data, np.array([[1, 2, 3, 4],
                                        [3, 4, 5, 6]]))

    def test_from_ecat(self):
        infile = join(split(abspath(__file__))[0], 'data',
                      'frametime','fdg_2frames.v')
        infile2 = join(split(abspath(__file__))[0], 'data', 'fdg_4frames.v')
        sample_data = np.array([[   1.,    0.,  300.,  300.],
                                [   2.,  300.,  600.,  300.]])

        ft = frametime.FrameTime()
        ft.from_ecats(infile, 'sec')
        print ft.data
        assert_equal(ft.data, sample_data)
        assert_equal(ft.get_units(), 'sec')
        
        # test multi-ecats
        ft = frametime.FrameTime()
        ft.from_ecats([infile2, infile])
        sampledata = np.array([[   1,    0,  300,  300],
                               [   2,  300,  600,  300],
                               [   3,  600,  900,  300],
                               [   4,  900,  1200, 300],
                               [   5, 1200,  1500, 300],
                               [   6, 1500,  1800, 299]])
        assert_equal(ft.data, sampledata)



    def test_from_csv(self):
        infile = join(split(abspath(__file__))[0], 'data',
                      'frametime', 'sample_frames.csv')
        sample_data = np.array([[1., 0., 15., 15.],
                                [2., 15., 30., 15.],
                                [3., 45., 60., 15.],
                                [4., 60., 90., 30.]])
        ft = frametime.FrameTime()
        ft.from_csv(infile, 'sec')
        assert_equal(ft.data, sample_data)
        assert_equal(ft.get_units(), 'sec')

    def test_from_excel(self):
        infile = join(split(abspath(__file__))[0], 'data',
                      'frametime', 'sample_frames.xls')
        sample_data = np.array([[1., 0., 15., 15.],
                                [2., 15., 30., 15.],
                                [3., 45., 60., 15.],
                                [4., 60., 90., 30.]])
        ft = frametime.FrameTime()
        ft.from_excel(infile, 'sec')
        assert_equal(ft.data, sample_data)
        assert_equal(ft.get_units(), 'sec')

    def test_to_csv(self):
        outfile = join(split(abspath(__file__))[0], 'data',
                       'frametime', 'sample_out.csv')
        sample_data = np.array([[1., 0., 15., 15.],
                                [2., 15., 30., 15.],
                                [3., 45., 60., 15.],
                                [4., 60., 90., 30.]])
        ft = frametime.FrameTime()
        assert_raises(DataError, ft.to_csv, outfile)
        ft.set_units('sec')
        ft.data = sample_data
        ft2 = frametime.FrameTime() 
        ft2.set_units('sec')
        f1 = ft.to_csv(outfile, 'sec')
        ft2.from_csv(f1, 'sec')
        assert_equal(ft2.data, sample_data)
        if exists(f1):
            os.remove(f1)

    def test_to_excel(self):
        outfile = join(split(abspath(__file__))[0], 'data',
                       'frametime', 'sample_out.xls')
        sample_data = np.array([[1., 0., 15., 15.],
                                [2., 15., 30., 15.],
                                [3., 45., 60., 15.],
                                [4., 60., 90., 30.]])
        
        ft = frametime.FrameTime()
        assert_raises(DataError, ft.to_excel, outfile)
        ft.set_units('sec')
        ft.data = sample_data
        ft2 = frametime.FrameTime() 
        ft2.set_units('sec')
        f1 = ft.to_excel(outfile, 'sec')
        ft2.from_excel(f1, 'sec')
        assert_equal(ft2.data, sample_data)
        if exists(f1):
            os.remove(f1)

    def test_get_data(self):
        """Test get_data, to_min, and to_sec"""
        ft = frametime.FrameTime()
        frames = np.array([[1, 2, 3, 4],
                           [2, 3, 4, 5],
                           [3, 4, 5, 6]])
        min_frames = frames * 1/60.0
        empty = np.array(None, dtype=object)
        ft.data = frames

        assert_equal(ft.get_data('sec'), empty)
        assert_equal(ft.to_sec(), empty)
        assert_equal(ft.to_min(), empty)

        ft.set_units('sec')
        assert_equal(ft.get_data('sec'), frames)
        assert_almost_equal(ft.get_data('min'), min_frames)
        assert_almost_equal(ft.to_sec(), frames)
        assert_almost_equal(ft.to_min(), min_frames)

        ft.data = min_frames
        ft.set_units('min')
        assert_equal(ft.get_data('sec'), frames)
        assert_equal(ft.get_data('min'), min_frames)
        assert_almost_equal(ft.to_sec(), frames)
        assert_almost_equal(ft.to_min(), min_frames)

    def test_get_start_times(self):  
        sample_data = np.array([[1., 0., 15., 15.],
                                [2., 15., 30., 15.],
                                [3., 30., 45., 15.],
                                [4., 45., 60., 15.],
                                [5., 60., 90., 30.]])

        ft = frametime.FrameTime()
        ft.data = sample_data
        start_times = ft.get_start_times()
        expected = np.array([[1, 0.],
                             [2, 15.],
                             [3, 30.], 
                             [4, 45.],
                             [5, 60.]])
        assert_equal(start_times, expected)

    def test_get_stop_times(self):  
        sample_data = np.array([[1., 0., 15., 15.],
                                [2., 15., 30., 15.],
                                [3., 30., 45., 15.],
                                [4., 45., 60., 15.],
                                [5., 60., 90., 30.]])

        ft = frametime.FrameTime()
        ft.data = sample_data
        stop_times = ft.get_stop_times()
        expected = np.array([[1, 15.],
                             [2, 30.],
                             [3, 45.], 
                             [4, 60.],
                             [5, 90.]])
        assert_equal(stop_times, expected)

    def test_get_midtimes(self):  
        sample_data = np.array([[1., 0., 15., 15.],
                                [2., 15., 30., 15.],
                                [3., 30., 45., 15.],
                                [4., 45., 60., 15.],
                                [5., 60., 90., 30.]])

        ft = frametime.FrameTime()
        ft.data = sample_data
        midtimes = ft.get_midtimes()
        expected = np.array([[1, 7.5],
                             [2, 22.5],
                             [3, 37.5], 
                             [4, 52.5],
                             [5, 75]])
        assert_equal(midtimes, expected)
