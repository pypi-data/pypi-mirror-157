import inspect
from warnings import warn

from matplotlib.widgets import Slider, Button
import matplotlib.pyplot as plt
import numpy as np

try:
    import lmfit
except ImportError:
    warn('lmfit import failed; do you have lmfit installed?', Warning)


def _check_args(fcn, args, kws):
    req_args = len(inspect.signature(fcn).parameters)
    prov_args = len(args) + len(kws)
    if prov_args + 1 != req_args:
        raise TypeError(
            f'{req_args-1} extra arguments are required'
            f' but {prov_args} were provided.'
        )


def _get_model_x(fcn, args, kws):
    name = list(inspect.signature(fcn).parameters)[1]
    if name in kws:
        return kws[name]
    return args[0]


def slider(
    fcn,
    params,
    data_x=None,
    args=None,
    kws=None,
    data=None,
    model_kwargs=None,
    data_kwargs=None,
    x=None,
):
    """Parameters
    ----------
    fcn : callable ``f(params, x, *args, **kws)``
    params : lmfit.Parameters
    data_x : numpy.ndarray
        X data to plot
    args : tuple
        Passed to ``fcn`` for evaluation
    kws : dict
        Passed to ``fcn`` for evaluation
    data : numpy.ndarray
        Y data to plot
    model_kwargs : dict
        ``matplotlib`` arguments for plotting model
    data_kwargs : dict
        ``matplotlib`` arguments for plotting data
    x : numpy.ndarray
        Deprecated, use data_x instead

    Returns
    -------
    new_params : lmfit.Parameters
        The final settings of all the sliders
    """
    # The parametrized function to be plotted
    if args is None:
        args = {}
    if kws is None:
        kws = {}
    if model_kwargs is None:
        model_kwargs = {}
    if data_kwargs is None:
        data_kwargs = {}
    if x is not None:
        warn('x keyword is deprecated, use data_x', FutureWarning)
        data_x = x
    params = params.copy()
    for name in params:
        if np.isinf(params[name].min) or np.isinf(params[name].max):
            raise ValueError('Params must have finite bounds.')
    _check_args(fcn, args, kws)

    # Create the figure and the line that we will manipulate
    fig, ax = plt.subplots()
    model_x = _get_model_x(fcn, args, kws)
    model = fcn(params, *args, **kws)
    line, = ax.plot(model_x, model, **model_kwargs)
    if data is not None:
        line2, = ax.plot(data_x, data, **data_kwargs)

    num_vary_params = 0
    for param in params.values():
        if param.vary:
            num_vary_params += 1
    # adjust the main plot to make room for the sliders
    plt.subplots_adjust(left=0.25, bottom=0.1+0.04*num_vary_params)

    # Make a horizontal slider to control the params.
    param_sliders = {}
    c = 0
    for k, param in params.items():
        if param.vary:
            axfreq = plt.axes([0.25, 0.1+c*0.04, 0.65, 0.03])
            param_sliders[param.name] = Slider(
                ax=axfreq,
                label=k,
                valmin=param.min,
                valmax=param.max,
                valinit=param.value,
            )
            c += 1

    # The function to be called anytime a slider's value changes
    init_min = min(model)
    init_max = max(model)

    def update(val):
        for param_name in param_sliders.keys():
            if params[param_name].vary:
                params[param_name].set(value=param_sliders[param_name].val)
        model = fcn(params, *args, **kws)
        old_bottom, old_top = ax.get_ylim()
        line.set_ydata(
            model,
        )
        ax.set_ylim(
            bottom=min(old_bottom, min(model)),
            top=max(old_top, max(model)),
        )
        if data is not None:
            line2.set_ydata(
                data,
            )
        fig.canvas.draw_idle()

    # register the update function with each slider
    for slider in param_sliders.values():
        slider.on_changed(update)

    resetax = plt.axes([0.8, 0.025, 0.1, 0.04])
    axresetax = plt.axes([0.6, 0.025, 0.1, 0.04])
    button = Button(resetax, 'Reset', hovercolor='0.975')
    button2 = Button(axresetax, 'Reset Axes', hovercolor='0.975')

    def reset(event):
        for slider in param_sliders.values():
            slider.reset()
        ax.set_ylim(bottom=init_min, top=init_max)

    def reset_axes(event):
        model = fcn(params, *args, **kws)
        if data is not None:
            ax.set_ylim(
                bottom=min(min(model), min(data)),
                top=max(max(model), max(data)),
            )
        else:
            ax.set_ylim(bottom=min(model), top=max(model))
    button.on_clicked(reset)
    button2.on_clicked(reset_axes)

    plt.show()
    return params
