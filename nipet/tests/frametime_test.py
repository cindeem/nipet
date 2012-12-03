from unittest import TestCase, skipIf, skipUnless
from numpy.testing import (assert_raises, assert_equal, assert_almost_equal)
from os.path import exists
import ..frametime

def file_exists(filename):
    return exists(filename) 

class TestFrametime(TestCase):

    def test_class(self):
        ft = frametime.FrameTime()
        assert_equal(ft.data, np.array([[0], [0], [0], [0]])) 
        assert_equal(ft.isempty(), True)
        
    def test_helpers(self): 
        ft = frametime.FrameTime()
        frame = ft._entry_to_frame(np.random.random(ft.data_size))
        badframe = ft._entry_to_frame(np.random.random(ft.data_size + 1))
        assert_equal(ft._check_frame(frame), True)
        assert_equal(ft._check_frame(badframe), False)
        ft.clear()
        assert_equal(ft.isempty(), True)

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


        
