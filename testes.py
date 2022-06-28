import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from random import randrange
import numpy as np

#plt.rcParams["figure.figsize"] = [7.00, 3.50]
plt.rcParams["figure.autolayout"] = True
fig, ax = plt.subplots(figsize=(10, 4))
plt.show()

for i in range(1000):
    x = np.arange(1, 21, 1)
    y = [randrange(0, 10) for _ in range(20)]

    X_Y_Spline = make_interp_spline(x, y)
    
    # Returns evenly spaced numbers
    # over a specified interval.
    x_ = np.linspace(x.min(), x.max(), 500)
    y_ = X_Y_Spline(x_)

    ax.plot(x_, y_, color="C0")
    ax.fill_between(x_, y_, y_.min(), color='C0', alpha=.1)
    plt.xticks(x)
    plt.xlim([x[0], x[-1]])
    fig.canvas.draw()
    plt.pause(0.1)