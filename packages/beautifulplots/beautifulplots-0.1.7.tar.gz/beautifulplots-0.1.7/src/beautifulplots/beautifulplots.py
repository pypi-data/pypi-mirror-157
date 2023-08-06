
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import Normalize
from matplotlib.cbook import boxplot_stats
import matplotlib as mpl 


def plot_defaults():
    """Dictionary of plot parameters. Each parameter coresponds and corresponding value. 
    See also get_plot_options for extracting plot options from **kwargs. 

    **Axis - x, y, and plot area parameters**
    
    Args:
        df (DataFrame): The input DataFrame containing colums corresponding to bar values and columns.
 
        title (String): corresponds to the axis title. default = ''
            
        titlefontsize: font size of the axis title, default = 18
            
        legend_loc(String): Matplotlib legend location, for example, upper right , default = "best".
        
        legend_loc2 (String): Secondary axis legend location, for example, upper right , default = best.
         
        xlims: (xmin, xmax), minimum and maximum x-values of the axis. default = None, in which case the min and max are set automatically by matplotlib.
        
        ylims: (ymin,ymax), minimum and maximum y-values of the axis. default = None, in which case the min and max are set automatically by matplotlib.
        
        ylims2: (ymin,ymax), minimum and maximum y-values of the secondary axis. default = None, in which case the min and max are set automatically by matplotlib.
        
        xlabelfontsize: default = 16
        
        xticklabelsize: default = 16
        
        xtickfontsize: default = 16
        
        xtickrotation: default = 0
        
        ylabelfontsize: ylabel font size, default = 16
            
        ytickfontsize: xtick label font size, default = 16
        
        ytickrotation:  Rotation of the xtick label, default = 0
        
        legendsize: legend font size, default = 16
        
        legend (Boolean):  Place a legend on the axis, default = False
            
        xlabel (String): xlabel title, default = ''
            
        ylabel (String):  ylable title, default = ''
        
    **Line, Scatter Plots**
    
    Args:
        
        marker: Matplotlib line markers. default = None (Matplotlib default).
            
        marker2: Secondary axis, Matplotlib line marker. default = None (Matplotlib default).
            
        yaxis_currency (Boolean): Boolean default = False.
            
        ytick_format (String): String default = None (Matplotlib default).
            
        alpha (fraction): Trasnparancy (opacity), default = None (not transparent)
            
        alpha2 (fraction): Secondary axis, default = 0.5, 50% opacity
        
        legend_labels (list): Overide default legend labels. default = None (do not override)
        
        estimator: seaborn barplot summary estimator, default = sum
            
        estimator2: secondary axis, seaborn barplot summary estimator, default = sum
            
        color: default = None, indicateing Matplolib default (Matplotlib default)
            
        color2: secondary axis line, bar or color. defualt = None (Matplotlib default)
            
        palette: colormap, default = None
            
        palette2: colormap, default = None, secondary y axis.
            
        hue: dimension value for corresponding Seaborn graphs, default = None.
        
        ci: Seaborn confidence interval parameter: float, sd, or None
            
        ci2: Seaborn confidence interval parameter second y axis: float, sd, or None
     
    **Plots and subplots**
    
    Parameters corresponding to the plot or subplot characteristics. They are used when matplot_helpers
    functions create the plot figure and axis, otherewise, these parameters do not affect the plot.
    
    Args:
    
        plotstyle (String): matplotlib plotstyle
            
        figsize: total size (height, width) in inches of the figure, including total plotting area of all subplots and spacing
        
        wspace: width space (horizontal) between subplots, default wspace = 0.2
        
        hspace: height space (vertical) between subplots, default hspace = 0.2
            
        legendloc: default=best
   
    **Returns**
    
        Dictionary: {parameter1:value1, parameter2:value2, ... }. 
        Pairs of plat parameters and corresponding values.
    """    

    plot_defaults = {
    # plot and subplot
    'pltstyle': 'seaborn',
    'figsize' :  None,
    'legend_loc':'best',
    'legend_loc2':'best',
    'wspace': 0.2,
    'hspace': 0.2,
    'sharex':False,
    
    # Axis ( corx and y plot)
    'title' :None,               #  list ot titles, 1 per axis  #  list of x,y tuples
    'ylims' :None,               # list of two-tuples ylims (lower, upper)
    'xlims' :None,
    'ylims2':None,
    'xlabelfontsize':16,
    'xticklabelsize':16,
    'xtickfontsize': 16,
    'xtickrotation':0,
    'ylabelfontsize':16,
    'ytickfontsize':16,
    'ytickrotation':0,
    'titlefontsize':18,
    'legendsize':16,
    'legend':False,
    'xlabel': '',
    'ylabel': '',
    'color':None,   # color designation for the corresponding graph
    'color2':None,   # color secondary y axis
    'palette':None,  
    'palette2':None,  # palette secondary y axis
    'hue':None,   # dimensional value for corresponding Seaborn graphs
    'ci':None, # confidence parameter for pimary axis
    'ci2': None, # confidence parameter for secondary axis


    # Lines and Scatter
    'marker':None,  # Boolean, list, dictionary
    'marker2':None,  # Boolean, list, or dictionary
    'yaxis_currency':False,
    'ytick_format': None,
    'legend_labels':None,
    'alpha': None,
    'alpha2': 0.5,
    'estimator':sum,
    'estimator2':sum
 

    }

    return plot_defaults

def set_axisparams(options_dict,ax,g): 
    """Receives as input a dictionary of plot options and applies the options to the maxtplotlib axis and graph.

    Args:
        options_dict (dictionary): Dictionary where each key, value pair corresponds to plot parameter
        ax (axis): matplotlib axis to apply the plot options
        g (graph): matplotlib graph to apply the plot options

    Returns:
        None: returns None if the function completes without errors.
    """ 

    title=options_dict['title']
    titlefontsize=options_dict['titlefontsize']
    legendloc=options_dict['legend_loc']
    legendsize=options_dict['legendsize']
    xlabel=options_dict['xlabel']
    xlabelfontsize=options_dict['xlabelfontsize']
    xlims=options_dict['xlims']
    xtickfontsize=options_dict['xtickfontsize']
    xtickrotation=options_dict['xtickrotation']
    ylabel=options_dict['ylabel']
    ylabelfontsize=options_dict['ylabelfontsize']
    ytickfontsize=options_dict['ytickfontsize']
    ytickrotation=options_dict['ytickrotation']
    ylims=options_dict['ylims']
    
    
    ax.set_xlabel(xlabel,fontsize=xlabelfontsize)
    ax.set_ylabel(ylabel,fontsize=ylabelfontsize)

    for x_tick in ax.get_xticklabels():
        x_tick.set_fontsize(xtickfontsize)
        x_tick.set_rotation(xtickrotation)

    for y_tick in ax.get_yticklabels():
        y_tick.set_fontsize(ytickfontsize)
        y_tick.set_rotation(ytickrotation)


    ax.set_title(title, fontsize=titlefontsize)

    if ylims != None:
        ax.set_ylim(ylims[0],ylims[1])

    if xlims != None:
        ax.set_xlim(xlims[0],xlims[1])

    if options_dict['legend'] == True:
        ax.legend( loc=legendloc, prop={'size': legendsize})     
        

    return None

def get_kwargs(**kwargs):   
    """process **kwargs options corresponding to the plot_defaults dictionary (see above)
    If a beautifulplots plot_option dictionary key is 
    contained in the **kwargs then the plot_defautls[key] value is replaced 
    with that found in **kwargs. 

    Returns:
        Dictionary: {parameter1:value1, parameter2:value2, ...} dictionary corresponding to plot options 
    """   
       
    plot_options = plot_defaults() # returns a dictionary of defaut matplotlib parameters

    # interate through the parameters in the plot_options dictionary
    # find the key in the kwargs, otherwise the paremeer = default
    # if the kwargs parameter != default then update plot_options
    for key in plot_options:
        default = plot_options[key]
        kwarg_value = kwargs.get(key, default) # parameter = kwarg  or default
        if kwarg_value != default: plot_options[key] = kwarg_value # update plot_option 
        
    return plot_options