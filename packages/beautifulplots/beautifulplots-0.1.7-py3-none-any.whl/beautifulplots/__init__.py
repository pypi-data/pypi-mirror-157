# read version from installed package
from importlib.metadata import version
__version__ = version("beautifulplots")


from .beautifulplots import plot_defaults 
from .beautifulplots import set_axisparams
from .beautifulplots import get_kwargs
from .barplot import barplot
from .lineplot import lineplot