🧪 pytest_bootstrap
===================

.. image:: https://github.com/tillahoffmann/pytest-bootstrap/actions/workflows/main.yml/badge.svg
  :target: https://github.com/tillahoffmann/pytest-bootstrap/actions/workflows/main.yml
  :alt: Build status.
.. image:: https://readthedocs.org/projects/pytest-bootstrap/badge/?version=latest
  :target: https://pytest-bootstrap.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation status.

Scientific software development often relies on stochasticity, e.g. for `Monte Carlo <https://en.wikipedia.org/wiki/Monte_Carlo_integration>`_ integration or simulating the `Ising model <https://en.wikipedia.org/wiki/Ising_model>`_. Testing non-deterministic code is difficult. This package offers a bootstrap test to validate stochastic algorithms.

For example, suppose we want to implement the expected value of `log-normal distribution <https://en.wikipedia.org/wiki/Log-normal_distribution>`_ with location parameter :math:`\mu` and scale parameter :math:`\sigma`.

.. doctest::

  >>> import numpy as np
  >>>
  >>> def lognormal_expectation(mu, sigma):
  ...   return np.exp(mu + sigma ** 2 / 2)
  >>>
  >>> def lognormal_expectation_wrong(mu, sigma):
  ...   return np.exp(mu + sigma ** 2)

We can validate our implementation by simulating from a lognormal distribution and comparing with the bootstrapped mean.

.. doctest::

  >>> from pytest_bootstrap import bootstrap_test
  >>>
  >>> mu = -1
  >>> sigma = 1
  >>> reference = lognormal_expectation(mu, sigma)
  >>> x = np.exp(np.random.normal(mu, sigma, 1000))
  >>> result = bootstrap_test(x, np.mean, reference)

This returns a summary of the test, such as the bootstrapped statistics.

.. doctest::

  >>> result.keys()
  dict_keys(['alpha', 'reference', 'lower', 'upper', 'z_score', 'median', 'iqr', 'statistics'])

Comparing with our incorrect implementation reveals the bug.

.. doctest::

  >>> reference_wrong = lognormal_expectation_wrong(mu, sigma)
  >>> result = bootstrap_test(x, np.mean, reference_wrong)
  Traceback (most recent call last):
    ...
  pytest_bootstrap.BootstrapTestError: {'alpha': 0.01, reference: 1.0, ...

Visualising the bootstrapped distribution can help identify discrepancies between the bootstrapped statistics and the theoretical reference value.

.. plot:: examples/lognormal.py

Interface
---------

.. automodule:: pytest_bootstrap
  :members:
