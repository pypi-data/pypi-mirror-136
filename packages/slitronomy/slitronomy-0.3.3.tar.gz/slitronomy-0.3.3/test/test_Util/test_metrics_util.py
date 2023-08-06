__author__ = 'aymgal'

from slitronomy.Util import metrics_util

import numpy as np
import numpy.testing as npt
import pytest
import unittest

np.random.seed(18)


def test_SDR():
    n = 10
    sdr = metrics_util.SDR(np.ones((n, n)), np.ones((n, n)))
    assert np.isinf(sdr)
    sdr = metrics_util.SDR(np.ones((n, n)), 2*np.ones((n, n)))
    assert sdr == 0.


def test_SSIM():
    n = 20
    ssim = metrics_util.SSIM(np.zeros((n, n)), np.zeros((n, n)))
    assert np.isnan(ssim)
    ssim = metrics_util.SSIM(np.ones((n, n)), np.ones((n, n)))
    assert ssim == 1.


def test_QOR():
    n = 20
    qor = metrics_util.QOR(np.ones((n, n)), np.ones((n, n)), np.ones((n, n)))
    assert qor == 0.

def test_chi2_nu():
    n = 20
    chi2_nu = metrics_util.chi2_nu(np.ones((n, n)), n**2)
    assert chi2_nu == 1.

def test_chi2_threshold():
    n = 20
    np.random.seed(18)
    chi2_nu = metrics_util.chi2_threshold(4*np.random.rand(n, n), sigma_threshold=3)
    npt.assert_almost_equal(chi2_nu, 12.469249, decimal=6)

def test_total_mag():
    n = 20
    total_mag = metrics_util.total_mag(np.ones((n, n)), 20)
    npt.assert_almost_equal(total_mag, 13.49485, decimal=4)


if __name__ == '__main__':
    pytest.main()
