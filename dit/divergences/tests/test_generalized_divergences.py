"""
Tests for dit.divergences.kullback_leiber_divergence.
"""

from __future__ import division

from nose.tools import assert_almost_equal, assert_not_equal, assert_raises, assert_greater

import numpy as np

from dit import Distribution
from dit.exceptions import ditException
from dit.divergences import kullback_leibler_divergence, alpha_divergence, renyi_divergence, tsallis_divergence, hellinger_divergence, hellinger_sum

def get_dists_1():
    """
    Construct several example distributions.
    """
    d1 = Distribution(['0', '1'], [1/2, 1/2])
    d2 = Distribution(['0', '2'], [1/2, 1/2])
    d3 = Distribution(['0', '1', '2'], [1/3, 1/3, 1/3])
    d4 = Distribution(['00', '11'], [2/5, 3/5])
    d5 = Distribution(['00', '11'], [1/2, 1/2])
    return d1, d2, d3, d4, d5

def get_dists_2():
    """
    Construct several example distributions.
    """
    d1 = Distribution(['0', '1'], [1/2, 1/2])
    d2 = Distribution(['0', '1'], [1/3, 2/3])
    d3 = Distribution(['0', '1'], [2/5, 3/5])
    return d1, d2, d3

def get_dists_3():
    """
    Construct several example distributions.
    """
    d1 = Distribution(['0', '1', '2'], [1/5, 2/5, 2/5])
    d2 = Distribution(['0', '1', '2'], [1/4, 1/2, 1/4])
    d3 = Distribution(['0', '1', '2'], [1/3, 1/3, 1/3])
    d4 = Distribution(['0', '1', '2'], [1/6, 2/6, 3/6])
    return d1, d2, d3, d4

def test_positive_definite():
    """
    Tests that divergences are zero when the input distributions are the same, and that the Hellinger sum is equal to 1.
    """
    alphas = [0, 1, 2, 0.5]
    divergences = [alpha_divergence, renyi_divergence, tsallis_divergence, hellinger_divergence]
    for dist in get_dists_1():
        for alpha in alphas:
            for divergence in divergences:
                assert_almost_equal(divergence(dist, dist, alpha), 0)
            assert_almost_equal(hellinger_sum(dist, dist, alpha), 1)

def test_positivity():
    """
    Tests that the divergence functions return positive values for non-equal arguments.
    """
    alphas = [0.1, 0.5, 1, 1.5]
    divergences = [alpha_divergence, renyi_divergence, tsallis_divergence, hellinger_divergence]
    test_dists = [get_dists_2(), get_dists_3()]
    for alpha in alphas:
        for dists in test_dists:
            for dist1 in dists:
                for dist2 in dists:
                    if dist1 == dist2:
                        continue
                    for divergence in divergences:
                        assert_greater(divergence(dist1, dist2, alpha), 0)

def test_alpha_symmetry():
    """
    Tests the alpha -> -alpha symmetry for the alpha divergence, and a similar symmetry for the Hellinger divergence.
    """
    alphas = [-1, 0, 0.5, 1, 2]
    test_dists = [get_dists_2(), get_dists_3()]
    for alpha in alphas:
        for dists in test_dists:
            for dist1 in dists:
                for dist2 in dists:
                    assert_almost_equal(alpha_divergence(dist1, dist2, alpha), alpha_divergence(dist2, dist1, -alpha))
                    assert_almost_equal((1.-alpha)*hellinger_divergence(dist1, dist2, alpha), alpha*hellinger_divergence(dist2, dist1, 1.-alpha))

def test_divergences_to_kl():
    """
    Tests that the generalized divergences properly fall back to KL for the appropriate values of alpha, and not otherwise.
    """
    test_dists = [get_dists_2(), get_dists_3()]
    for dists in test_dists:
        for dist1 in dists:
            for dist2 in dists:
                assert_almost_equal(alpha_divergence(dist1, dist2, alpha=-1), kullback_leibler_divergence(dist2, dist1))
                if dist1 != dist2:
                    assert_not_equal(alpha_divergence(dist1, dist2, alpha=0), kullback_leibler_divergence(dist2, dist1))
                for divergence in [renyi_divergence, tsallis_divergence, alpha_divergence, hellinger_divergence]:
                    assert_almost_equal(divergence(dist1, dist2, alpha=1), kullback_leibler_divergence(dist1, dist2))
                    if dist1 != dist2:
                        assert_not_equal(alpha_divergence(dist1, dist2, alpha=0), kullback_leibler_divergence(dist2, dist1))
                        assert_not_equal(alpha_divergence(dist1, dist2, alpha=2), kullback_leibler_divergence(dist2, dist1))

def test_exceptions():
    """
    Test that when p has outcomes that q doesn't have, that we raise an exception.
    """
    d1, d2, d3, d4, d5 = get_dists_1()
    tests = [[d4, d1, None, None],
             [d4, d2, None, None],
             [d4, d3, None, None],
             [d1, d2, [0, 1], None],
             [d3, d4, [1], None],
             [d5, d1, [0], [1]],
             [d4, d3, [1], [0]]]
    divergences = [alpha_divergence, renyi_divergence, tsallis_divergence, hellinger_divergence]
    alphas = [0, 1, 2, 0.5]
    for first, second, rvs, crvs in tests:
        for divergence in divergences:
            for alpha in alphas:
                yield assert_raises, ditException, divergence, first, second, alpha, rvs, crvs
