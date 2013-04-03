from unittest import TestCase, skipIf, skipUnless
import numpy as np
from numpy.random import RandomState
from numpy.testing import (assert_raises, assert_equal, assert_almost_equal)
from os.path import (exists, join, split, abspath)
import os
from .. import ga

class TestLogan(TestCase):

    def setUp(self):
        """ create small example data """
        nprand = RandomState(42)
        self.ref = nprand.random_sample(34)# generate fixed random sample
        self.steps =  np.linspace(0, 90, num=34)# regulalry spaced steps
    def test_init(self):
        # expects same shaped initial input
        assert_raises(TypeError, ga.Logan)
        assert_raises(IOError, ga.Logan, 
                      self.steps, np.random.random((10)))
        good_logan = ga.Logan(self.steps, self.ref)
        assert_equal(good_logan.timesteps, self.steps)
        assert_equal(good_logan.ref_counts, self.ref)

    def test_integrate_reference(self):
        lga = ga.Logan(self.steps, self.ref)
        assert_equal(hasattr(lga, 'int_ref'), False)
        lga._integrate_reference()
        integrated = np.zeros(self.ref.shape)
        integrated[1:] = ga.cumtrapz(self.ref, self.steps)
        assert_equal(lga.int_ref, integrated)
        assert_equal(lga.int_ref[0], 0)


if __name__ == '__main__':
    unittest.main()
