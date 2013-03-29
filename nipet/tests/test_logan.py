from unittest import TestCase, skipIf, skipUnless
import numpy as np
from numpy.testing import (assert_raises, assert_equal, assert_almost_equal)
from os.path import (exists, join, split, abspath)
import os
from .. import ga

class TestLogan(TestCase):

    def setUp(self):
        """ create small example data """
        self.ref = np.random.random((34))
        self.steps =  np.linspace(0, 90, num=34)# regulalry spaced steps
    def test_init(self):
        # expects same shaped initial input
        assert_raises(TypeError, ga.Logan)
        assert_raises(IOError, ga.Logan, 
                      self.steps, np.random.random((10)))
        good_logan = ga.Logan(self.steps, self.ref)
        assert_equal(good_logan.timesteps, self.steps)
        assert_equal(good_logan.ref_counts, self.ref)

if __name__ == '__main__':
    unittest.main()
