# lmfit-slider

### Requirements
- `matplotlib`
- `numpy`

### Usage

```
import lmfit
import numpy as np

from lmfit_slider import slider


def fcn(params, x, A):
    return A*np.sin(params['k']*x)


params = lmfit.Parameters()
params.add('k', value=1, min=-10, max=10)

data_x = np.linspace(0, 2*np.pi, 6)
data = 1.5*np.sin(4*data_x)

model_x = np.linspace(min(data_x), max(data_x), 5000)

new_params = slider(
    fcn,
    params,
    data_x=data_x,
    data=data,
    args=(model_x, 1.5),
)

new_params.pretty_print()
```
