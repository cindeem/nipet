from unittest import TestCase, skipIf, skipUnless
from numpy.testing import (assert_raises, assert_equal, assert_almost_equal)
from os.path import exists
import ..frametime

def file_exists(filename):
    return exists(filename) 

class TestFrametime(TestCase):

    def test_class(self):
        ft = frametime.FrameTime()
        assert_equal(ft.isempty(), True)
        
    def test_check_frame(self): 
        ft = frametime.FrameTime()
        frame = ft._entry_to_frame(np.random.random(ft.col_num))
        badframe = ft._entry_to_frame(np.random.random(ft.col_num + 1))
        assert_equal(ft._check_frame(frame), True)
        assert_equal(ft._check_frame(badframe), False)

    def test_validate_frames(self):
        frames = np.random.random((5, 3))
        ft = frametime.FrameTime()
        ft.data = frames
        assert_raises(ft._validate_frames(), Error)
        frames = np.random.random((5, 4))
        ft.data = frames
        assert_raises(ft._validate_frames(), Error)

    def test_delete_frame(self):
        ft = frametime.FrameTime()
        frames = np.array([[1, 2, 3, 4],
                           [2, 3, 4, 5],
                           [3, 4, 5, 6]])
        ft.data = frames
        ft.delete_frame(1)
        assert_equal(ft.data, np.array([[1, 2, 3, 4],
                                        [3, 4, 5, 6]])

    @skipUnless(file_exists(some_file))
    def test_from_csv(self):
        try:
            ft = frametime.FrameTime()
            filename = '' 
            from_csv(filename)
            assert_equal(ft.data, something)
            assert_equal(ft.get_units(), 'sec')
            from_csv(filename, units = 'min')
            assert_equal(ft.data, something_else)
            assert_equal(ft.get_units(), 'min')
        except:
            print "Welp."


        
