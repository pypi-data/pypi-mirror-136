import importlib
import numpy as np
import scipy.stats
import sys


def sample_from(samples, dist_name, dist_kwargs):
    """
    Sample from a distribution by evaluating the quantile function.

    :param samples: The values for which to evaluate the quantile function.
    :param dist_name: The name of the distribution to sample.
    :param dist_kwargs: The (distribution-specific) shape parameters.
    :returns: The sample values as a ``numpy.ndarray`` that has the same shape
        as ``samples``.
    :raises ValueError: if the distribution ``dist_name`` is not defined.

    :Examples:

    >>> import lhs.dist
    >>> import numpy as np
    >>> samples = np.array([0.1, 0.5, 0.9])
    >>> kwargs = {'loc': 10, 'scale': 5}
    >>> values = lhs.dist.sample_from(samples, 'uniform', kwargs)
    >>> print(values)
    [10.5 12.5 14.5]
    """
    try:
        final_period = dist_name.rfind('.')
        if final_period < 0:
            # No period, look for a function in this module.
            fn = getattr(sys.modules[__name__], dist_name)
        else:
            # Also support fully-qualified function names.
            module_name = dist_name[:final_period]
            value_name = dist_name[final_period + 1:]
            module = importlib.import_module(module_name)
            fn = getattr(module, value_name)
    except (AttributeError, ModuleNotFoundError):
        return scipy_stats_dist(samples, dist_name, dist_kwargs)

    if not callable(fn):
        name = __name__ + '.' + dist_name
        raise ValueError('The value "{}" is not callable'.format(name))

    return fn(samples, **dist_kwargs)


def constant(samples, value):
    """
    The constant distribution, which always returns ``value``.

    :Examples:

    .. code-block:: python

       dist_R0 = {'name': 'constant', 'args': {'value': 2.53}}
    """
    return value * np.ones(samples.shape)


def scipy_stats_dist(samples, dist_name, dist_kwargs):
    """
    Sample from a distribution defined in the ``scipy.stats`` module.

    :param samples: The values for which to evaluate the quantile function.
    :param dist_name: The name of the distribution to sample.
    :param dist_kwargs: The (distribution-specific) shape parameters.
    :returns: The sample values as a ``numpy.ndarray`` that has the same shape
        as ``samples``.
    :raises ValueError: if the distribution ``dist_name`` is not defined.
    """
    try:
        dist_class = getattr(scipy.stats, dist_name)
    except AttributeError:
        raise ValueError('Unknown distribution "{}"'.format(dist_name))
    dist_obj = dist_class(**dist_kwargs)
    return dist_obj.ppf(samples)
