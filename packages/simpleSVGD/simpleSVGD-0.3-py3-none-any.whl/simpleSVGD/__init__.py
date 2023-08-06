import numpy as _numpy
import tqdm.auto as _tqdm_auto
import matplotlib.pyplot as _plt
import matplotlib.figure as _figure
from typing import Callable as _Callable, List as _List, Tuple as _Tuple

from .kernels import rbf_kernel as _rbf_kernel
from .helpers import TorchWrapper as _TorchWrapper


from . import _version

__version__ = _version.get_versions()["version"]


def update(
    x0: _numpy.array,
    gradient_fn: _Callable,
    # All following parameters are tuning parameters
    n_iter: int = 1000,
    stepsize: float = 1e-3,
    bandwidth: float = -1,
    # All following parameter only concern animation
    animate: bool = False,
    figure: _figure.Figure = None,
    dimensions_to_plot: _List[float] = [0, 1],
    background: _Tuple[_numpy.array] = None,
):
    """
    Function to update a collection of samples using the SVGD algorithm.

    x0
        The initial samples are given to the function using x0, which has shape
        (n_samples, function_dimensionality).

    gradient_fn
        A callable which computes the gradients of the function to approximate.
        No values of the actual function are needed. Should accept multiple
        points in input space (i.e. the shape of x0) and return a gradient of
        the same shape as its input. In a Bayesian context; the actual
        gradients to pass are those of the negative log likelihood.

    n_iter
        Number of iterations to do on the samples. Default is 1000.

    stepsize
        Stepsize of the SVGD algorithm. Default is 1e-3.

    bandwidth
        Bandwidth of the radial basis functions. Omitting this (or passing -1)
        automatically computes it based on the distribution of samples. This is
        more likely to produce good results, but will slow the algorithm down.
        Default is -1.

    animate
        A boolean to animate the algorithm. Only works for functions of at
        least two dimensions. Default is False.

    figure
        A figure object in which to use the current axis for the animation.
        Passing None will create a new figure. Default is None.

    dimensions_to_plot
        An array of two ints which describe which two dimensions to animate of
        any higher dimensional function. Default is [0, 1].

    background
        A tuple of three arrays, used for the first three arguments of
        matplotlib.pyplot.contour, to make plotting a background easier.
    """
    # Check input
    if x0 is None or gradient_fn is None:
        raise ValueError("x0 or gradient_fn cannot be None!")

    if animate:
        if figure is None:
            figure = _plt.figure(figsize=(8, 8))
        axis = _plt.gca()

    # To make sure we don't accidentally update a variable we're not supposed
    # to (i.e. avoid changing a variable by reference)
    x0_updated = _numpy.copy(x0)

    # adagrad with momentum
    if animate:
        if background is not None:
            x1s, x2s, background_image = background

            axis.contour(
                x1s,
                x2s,
                _numpy.exp(-background_image),
                levels=20,
                alpha=0.5,
                zorder=0,
            )

        scatter = axis.scatter(
            x0_updated[:, dimensions_to_plot[0]],
            x0_updated[:, dimensions_to_plot[1]],
        )

        if background is not None:
            _plt.xlim([x1s.min(), x1s.max()])
            _plt.ylim([x2s.min(), x2s.max()])

        axis.set_aspect(1)

        figure.canvas.draw()
        _plt.pause(1e-5)

    # The Try/Except allows on to interrupt the algorithm using CTRL+C while
    # still getting x0_updated at the point of interruption.
    try:
        for _ in _tqdm_auto.trange(n_iter):

            # Calculate all the gradients of the -log(p)
            grad_neglogp = gradient_fn(x0_updated)

            # calculating the kernel matrix
            kxy, dxkxy = _rbf_kernel(x0_updated, h=bandwidth)
            grad_theta = (_numpy.matmul(kxy, grad_neglogp) - dxkxy) / x0.shape[
                0
            ]

            x0_updated = x0_updated - stepsize * grad_theta

            if animate:
                scatter.set_offsets(
                    _numpy.hstack(
                        (
                            x0_updated[:, dimensions_to_plot[0], None],
                            x0_updated[:, dimensions_to_plot[1], None],
                        )
                    )
                )
                figure.canvas.draw()
                _plt.pause(1e-5)

    except KeyboardInterrupt:
        pass

    return x0_updated


def update_torch(
    x0: _numpy.array,
    gradient_fn: _Callable,
    optimizer_class,
    optimizer_parameters={},
    schedulers=[],
    # All following parameters are tuning parameters
    n_iter: int = 1000,
    # All following parameter only concern animation
    animate: bool = False,
    figure: _figure.Figure = None,
    dimensions_to_plot: _List[float] = [0, 1],
    background: _Tuple[_numpy.array] = None,
    # Torch algorithm
):
    """
    Function to update a collection of samples using the SVGD algorithm.

    x0
        The initial samples are given to the function using x0, which has shape
        (n_samples, function_dimensionality).

    gradient_fn
        A callable which computes the gradients of the function to approximate.
        No values of the actual function are needed. Should accept multiple
        points in input space (i.e. the shape of x0) and return a gradient of
        the same shape as its input. In a Bayesian context; the actual
        gradients to pass are those of the negative log likelihood.

    n_iter
        Number of iterations to do on the samples. Default is 1000.

    stepsize
        Stepsize of the SVGD algorithm. Default is 1e-3.

    bandwidth
        Bandwidth of the radial basis functions. Omitting this (or passing -1)
        automatically computes it based on the distribution of samples. This is
        more likely to produce good results, but will slow the algorithm down.
        Default is -1.

    animate
        A boolean to animate the algorithm. Only works for functions of at
        least two dimensions. Default is False.

    figure
        A figure object in which to use the current axis for the animation.
        Passing None will create a new figure. Default is None.

    dimensions_to_plot
        An array of two ints which describe which two dimensions to animate of
        any higher dimensional function. Default is [0, 1].

    background
        A tuple of three arrays, used for the first three arguments of
        matplotlib.pyplot.contour, to make plotting a background easier.
    """
    import torch as _torch

    # Check input
    if x0 is None or gradient_fn is None:
        raise ValueError("x0 or gradient_fn cannot be None!")

    if animate:
        if figure is None:
            figure = _plt.figure(figsize=(8, 8))
        axis = _plt.gca()

    # To make sure we don't accidentally update a variable we're not supposed
    # to (i.e. avoid changing a variable by reference)
    x0_updated = _numpy.copy(x0)

    # adagrad with momentum
    if animate:
        if background is not None:
            x1s, x2s, background_image = background

            axis.contour(
                x1s,
                x2s,
                _numpy.exp(-background_image),
                levels=20,
                alpha=0.5,
                zorder=0,
            )

        scatter = axis.scatter(
            x0_updated[:, dimensions_to_plot[0]],
            x0_updated[:, dimensions_to_plot[1]],
        )

        if background is not None:
            _plt.xlim([x1s.min(), x1s.max()])
            _plt.ylim([x2s.min(), x2s.max()])

        axis.set_aspect(1)

        figure.canvas.draw()
        _plt.pause(1e-5)

    x0_updated = _torch.tensor(x0_updated, requires_grad=True)
    total = _TorchWrapper(gradient_fn, _rbf_kernel)

    optimizer = optimizer_class([x0_updated], **optimizer_parameters)

    # The Try/Except allows on to interrupt the algorithm using CTRL+C while
    # still getting x0_updated at the point of interruption.
    try:
        for _ in _tqdm_auto.trange(n_iter):

            def closure():
                optimizer.zero_grad()
                loss = total(x0_updated).mean()
                loss.backward()
                return loss

            optimizer.step(closure)

            for scheduler in schedulers:
                scheduler.step()

            if animate:
                scatter.set_offsets(
                    _numpy.hstack(
                        (
                            x0_updated.detach()[
                                :, dimensions_to_plot[0], None
                            ],
                            x0_updated.detach()[
                                :, dimensions_to_plot[1], None
                            ],
                        )
                    )
                )
                figure.canvas.draw()
                _plt.pause(1e-5)

    except KeyboardInterrupt:
        pass

    return x0_updated.detach().numpy()


def gradient_vectorizer(non_vectorized_gradient: _Callable):
    def grd(m: _numpy.array) -> _numpy.array:
        return _numpy.hstack(
            [
                non_vectorized_gradient(m[idm, :, None])
                for idm in range(m.shape[0])
            ]
        ).T

    return grd
