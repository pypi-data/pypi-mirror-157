
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import Normalize
from matplotlib.cbook import boxplot_stats
import matplotlib as mpl

import  beautifulplots.beautifulplots as bp  


def barplot(df, bar_columns, bar_values, barcurrency=None, barorientation="v", bardataformat="1.2f",
            y2=None, ax=None, bardatalabels=False, test_mode=False, bardatafontsize=14,
            **kwargs):
    """Bar plot function designed for ease of use and aesthetics. 
    The underlying barplot is ased on the Seaborn with additions, such as secondary axis, data labels,
    and improved default parameters. Refer to beautifulplots plot_defaults for a complete list of options.
    
    Args:
        df (DataFrame): The input DataFrame containing colums corresponding to bar_plot values ("bar_values") and column names (see examples in documentation)
            
        bar_columns: Datafrae columns corresponding to bar column names
            
        bar_values: Dataframe column corresponding to bar column values
            
        ax (axis): matplotlib axis (optional), default = None. If axis is None, then create a matplolib figure, axis to host the barplot
            
        color: Matplotlib compatabile color name as text or RGB values, for example,  color = [51/235,125/235,183/235].
            
        palette: Matplotlib compatible color palette name, for example, "tab20"
            
        hue: Name of hue dimension variable (i.e., DataFrame column name)
            
        ci: Seaborn confidence interval parameter: float, sd, or None, default = None
            
        barorientation: default = v (vertical), or h (horizontal)
            
        barcurrency: default = False (bar values do not represent currency). True (bar values represent currency, append $ to the value)
            
        bardatalabels (Boolean): default = False (data labels not included)
        
        additional options:  see kale.plot_defaults for additional input variables.
            

    Returns:
        returns True if processing completes succesfully (without errors).
    """
        
    plot_options = bp.get_kwargs(**kwargs)
    
    estimator = plot_options['estimator'] 
    estimator2 = plot_options['estimator'] 
    ci = plot_options['ci']
    ci2 = plot_options['ci2']
    alpha = plot_options['alpha']
    alpha2 = plot_options['alpha2']
    hue = plot_options['hue']
    palette = plot_options['palette']
    palette2 = plot_options['palette2']
    marker2 = plot_options['marker2']
    color = plot_options['color']
    color2 = plot_options['color2']


    # if no hue then only one color
    # if hue == None and color==None : color = [51/235,125/235,183/235] if plot_options['color'] == None else plot_options['color']

    if barorientation == 'v': x,y = bar_columns, bar_values
    else: x,y = bar_values, bar_columns
    

    if ax == None: 
        mpl.rcParams.update(mpl.rcParamsDefault) # reset plot/figure parameters
        plt.style.use(plot_options['pltstyle'])
        fig,_ax = plt.subplots(nrows=1, ncols=1, figsize=plot_options['figsize']) 
    else: _ax = ax
        
    g=sns.barplot(x=x, y=y, hue=hue, color = color, palette=palette, data=df, ax = _ax,
                  orient=barorientation, ci=ci, estimator=estimator, alpha=alpha)
    
    # Bar labels ... iterate with hue
    # Matplotlib
      # https://matplotlib.org/stable/gallery/lines_bars_and_markers/bar_label_demo.html#sphx-glr-gallery-lines-bars-and-markers-bar-label-demo-py
    # Geeks for Geeks
      # https://www.geeksforgeeks.org/how-to-show-values-on-seaborn-barplot/
    if bardatalabels== True and hue == None:
        f = "%"+bardataformat+""
        if barcurrency == True: f = "$"+f # dollar
        g.bar_label(g.containers[0],  fontsize=bardatafontsize, fmt=f)

    # Geeks for Geeks bar data labels
      # https://www.geeksforgeeks.org/how-to-show-values-on-seaborn-barplot/
    if  bardatalabels == True and hue !=None:
        f = "%"+bardataformat+""
        if barcurrency == True: f = "$"+f # dollar
        for i in g.containers:
            g.bar_label(i,fontsize=bardatafontsize, fmt=f )
   
    # yaxis tick label format
    # https://matplotlib.org/stable/gallery/pyplots/dollar_ticks.html
    # x or y format same as bars ... since this could be v or h graph
    if barcurrency == True:
        #y_ticks = _ax.get_yticks()
        f='{x:'+ bardataformat  +'}'
        if barcurrency== True: f='${x:'+ bardataformat  +'}'
        if barorientation=='v':
            _ax.yaxis.set_major_formatter(f)
        if barorientation=='h':
            _ax.xaxis.set_major_formatter(f)
 
   
   # secondary y-axis
    if y2 != None:
       
        if isinstance(y2,list):
            y2_list = y2
        else:
            y2_list = [y2]

        _ax2 = _ax.twinx()
        
        
        for _y2 in y2_list:
            if plot_options['palette2'] !=None:
                g = sns.lineplot(data=df,x=x, y =_y2, hue=hue, palette=palette2,  ax=_ax2, label=_y2, 
                                 alpha = alpha2,ci = ci2, marker=marker2, estimator=estimator2)
            elif plot_options['color2'] !=None:
                g = sns.lineplot(data=df,x=x, y=_y2, hue=hue, color=color2,  ax=_ax2,label=_y2, 
                                 alpha=alpha2, ci=ci2, marker=marker2, estimator=estimator2)
            else:
                g = sns.lineplot(data=df,x=x, y=_y2, hue=hue, ax=_ax2, label=_y2, 
                                 alpha=alpha2, ci=ci2, marker=marker2, estimator=estimator2) 
                
        _ax2.grid(b=None)  
    
    # set axis params
    bp.set_axisparams(plot_options,_ax,g)  # axis parameters from the plot_options dictionary
    
    # y2 axis params
    if y2 != None:
        bp.set_axisparams(plot_options,_ax2,g)  # axis parameters
    
        # set ylims 2 after general axis parameters 
        if plot_options['ylims2'] != None:
            _ax2.set_ylim(plot_options['ylims2'])
        
        # axis 2 legend
        if y2 != None and plot_options['legend']==True:
            _ax2.legend( loc=plot_options['legend_loc2'], prop={'size': plot_options['legendsize']})
    

    if ax==None and test_mode==False: plt.show() # if barplot created the figure then plt.show()
    
    return None