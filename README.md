# mplformatting

Utilities to make Matplotlib plots pretty and consistent across projects:

- Custom log tick logic (decades + adaptive minor ticks)
- Mixed tick directions:
  - Left & bottom ticks **out**
  - Right & top ticks **in**
  - No labels on top/right
- Scientific notation formatter for the y-axis
- A custom `paper.mpltstyle` style sheet
- `apply()`, `autoformat` decorator and `autoformatting` context manager

## Installation

Clone this repo somewhere on your machine, e.g.

```bash
git clone <YOUR-REPO-URL> ~/code/mplformatting
cd ~/code/mplformatting
```

You can tweak the wording of course, but that’s the general structure.

---

In **any** project on your PC:

1. Make sure you’re in that project’s environment (or system Python).
2. Install your package once:

   ```bash
   cd ~/code/mplformatting
   pip install -e .

```python
import matplotlib.pyplot as plt
import numpy as np
from mplformatting import apply

x = np.linspace(0, 1000, 100)
y = np.sin(x) * 1e6

fig, ax = plt.subplots()
ax.plot(x, y, label="Sine")
ax.set_yscale("log")
ax.set_ylim(1, 1e7)

apply(ax)  # applies style, log tick formatting, mixed tick directions

ax.legend()
plt.show()
```

Decorator usage:
```python

from mplformatting import autoformat
import matplotlib.pyplot as plt
import numpy as np

@autoformat(max_xticks=6, max_yticks=6)
def make_plot():
    x = np.linspace(0, 1000, 100)
    y = np.cos(x) * 1e6

    fig, ax = plt.subplots()
    ax.plot(x, y, label="Cosine")
    ax.set_yscale("log")
    ax.set_ylim(1, 1e7)
    ax.legend()
    return fig, ax

fig, ax = make_plot()
plt.show()
```

```python
from mplformatting import autoformatting
import matplotlib.pyplot as plt
import numpy as np

with autoformatting(max_xticks=6, max_yticks=6):
    fig, axes = plt.subplots(2, 2, sharex=True, sharey=True)
    x = np.linspace(0, 1000, 100)

    for ax in axes.flat:
        ax.plot(x, np.sin(x) * 1e6)
        ax.set_yscale("log")
        ax.set_ylim(1, 1e7)
    # Shared axis labels
    fig.supxlabel("X-label")
    fig.supylabel("Y-label")


plt.show()
```