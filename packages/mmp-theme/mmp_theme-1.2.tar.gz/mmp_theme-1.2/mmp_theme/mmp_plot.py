#########################
## IMPORT DEPENDENCIES ##
#########################
import plotly.express as px
import plotly.io as pio
from collections import defaultdict
import base64
from mmp_theme import *

##############################
## LIST OF INPUT PARAMETERS ##
##############################
input_params = {'data': 'DataFrame with data to be plot',
                'kind': 'Type of plot. Implemented type are: \'line\', \'scatter\', \'bar\', \'imshow\', \'scatter3d\', \'box\', \'hist\'',
                'x': 'Name of the dataframe column to be used on the x-axis (if None, data.index is used)',
                'y': 'Name of the dataframe column to be used on the y-axis (if None, data.columns is used)',
                'z': 'Name of the dataframe column to be used on the z-axis (only for 3D plots of imshow)',
                'show': 'bool, if True, the plot is shown',
                'main_logo_source': 'str, url or path for main logo',
                'proj_logo_source': 'str, url or path for additional project logo',
                '**plot_fun_keywords': 'The function accepts all the allowed plotly parameters for the plot chosen in \'kind\'',
                '**additional_parameters': 'Hardcoded layout and traces parameters. See dict \'additional_params\''
                }

#################################
## LIST OF ACCEPTED PARAMETERS ##
#################################
additional_params = {'title': 'Plot title (str, optional)',
                     'xlabel': 'Label of x-axis (str, optional)',
                     'ylabel': 'Label of y-axis (str, optional)',
                     'zlabel': 'Label of z-axis (str, optional, only for 3D plots)',
                     'xlim': 'Limits on x-axis (list: [xmin, xmax], optional)',
                     'ylim': 'Limits on y-axis (list: [ymin, ymax], optional)',
                     'legend_title': 'Legend title (str, optional)',
                     'width': 'Figure width (int, optional, default=1500 px)',
                     'height': 'Figure height (int, optional, default=900 px)',
                     'colorbar_title': 'Colorbar title (str, optional, if applicable)',
                     'mode': 'Sets mode for line plots (str, \'lines\', \'lines+markers\', \'markers\', default=\'lines\', only for kind=\'line\'',
                     'line_style': 'Sets style of line traces (str, \'solid\', \'dash\', \'dot\', or any accepted by line_dash property of plotly scatter traces, default=\'solid\', only for kind=\'line\'',
                     'line_color': 'Sets color of line traces (str, named CSS color, or any accepted by line_color property of plotly scatter traces, only for kind=\'line\')',
                     'line_width': 'Sets width of line traces (int, default=2 px, only for kind=\'line\')',
                     'marker_color': 'Sets color of markers (str, named CSS color, or any accepted by line_color property of plotly scatter traces, only for kind=\'line\', \'scatter\')',
                     'marker_size': 'Sets size of markers (int, only for kind=\'line\', \'scatter\')',
                     'marker_alpha': 'Sets opacity of markers (int between or equal to 0 and 1, only for kind=\'line\', \'scatter\')',
                     'quartilemethod': 'Method to compute quartiles (str, \'exclusive\', \'inclusive\', \'linear\', only for kind=\'box\')',
                     'barmode': 'Sets how bars at the same location are displayed (str, \'stack\', \'relative\', \'group\', default=\'overlay\')'
                     }


###########################
## FNC: PARAM PREPROCESS ##
###########################
def process_params(param, kind):
    param = param.copy()  # Creates a copy

    traces, layouts = defaultdict(dict), defaultdict(dict)  # Default properties dictionaries

    # Traces definition
    if kind == 'line':
        traces['mode'] = param.pop('mode', None)
        traces['line'].update(dash=param.pop('line_style', 'solid'))
        traces['line'].update(color=param.pop('line_color', None))
        traces['line'].update(width=param.pop('line_width', None))
    if kind == 'line' or kind == 'scatter':
        traces['marker'].update(size=param.pop('marker_color', None))
        traces['marker'].update(size=param.pop('marker_size', None))
        traces['marker'].update(opacity=param.pop('marker_alpha', None))
    if kind == 'box':
        traces['quartilemethod'] = param.pop('quartilemethod', 'linear')

    # Layout definition
    if kind != 'scatter3d':
        layouts['xaxis'].update(title=param.pop('xlabel', None))
        layouts['yaxis'].update(title=param.pop('ylabel', None))
    layouts['xaxis'].update(range=param.pop('xlim', None))
    layouts['yaxis'].update(range=param.pop('ylim', None))
    layouts['legend'].update(title=param.pop('legend_title', None))
    layouts['width'] = param.pop('width', None)
    layouts['height'] = param.pop('height', None)
    layouts['coloraxis'].update(colorbar=dict(title=param.pop('colorbar_title', None)))
    layouts['barmode'] = param.pop('barmode', 'overlay')
    if kind == 'scatter3d':
        layouts['scene'].update(xaxis=dict(title=param.pop('xlabel', None)),
                                yaxis=dict(title=param.pop('ylabel', None)),
                                zaxis=dict(title=param.pop('zlabel', None)))

    return param, traces, layouts


#####################
## FNC: INNER PLOT ##
#####################
def mmp_inner_plot(plot_fun, data, x, y, z, main_logo_source, proj_logo_source, fun_params, traces_params, layout_params):
    #pio.templates['mmp_theme'].layout.images[0]['visible'] = mmp_logo

    if z is not None:  # 3D
        if plot_fun == px.imshow:
            inner_data = data.set_index([x, y])[z].unstack()
            fig = plot_fun(inner_data, **fun_params)
        elif (plot_fun == px.scatter_3d) or (plot_fun == px.line_3d):
            fig = plot_fun(data, x=x, y=y, z=z, **fun_params).update_traces(**traces_params)
        else:
            raise ValueError('Function not yet implemented')
    else:  # 2D
        fig = plot_fun(data, x=x, y=y, **fun_params).update_traces(**traces_params)

    fig.update_layout(**layout_params)

    # Set logos
    img_list = []
    if main_logo_source is not None:
        if 'https' in main_logo_source:
            main_logo = main_logo_source
        else:
            main_file_logo = base64.b64encode(open(main_logo_source, 'rb').read())
            main_logo = 'data:image/png;base64,{}'.format(main_file_logo.decode())
        main_img_dict = dict(name="mainlogo",
                             source=main_logo,
                             xref="paper", yref="paper",
                             x=1, y=1.01, sizex=1, sizey=0.12,
                             xanchor="right", yanchor="bottom",
                             opacity=1, visible=True)
        img_list.append(main_img_dict)
    if proj_logo_source is not None:
        if 'https' in proj_logo_source:
            proj_logo = proj_logo_source
        else:
            file_logo = base64.b64encode(open(proj_logo_source, 'rb').read())
            proj_logo = 'data:image/png;base64,{}'.format(file_logo.decode())
        proj_img_dict = dict(name="projlogo",
                             source=proj_logo,
                             xref="paper", yref="paper",
                             x=0.75, y=1.01, sizex=1, sizey=0.12,
                             xanchor="right", yanchor="bottom",
                             opacity=1, visible=True)
        img_list.append(proj_img_dict)
    fig.update_layout(images=img_list)

    return fig


#######################
## FNC: FUN SELECTOR ##
#######################
def fun_selector(kind):
    if kind == 'line':
        plot_fun = px.line
    elif kind == 'scatter':
        plot_fun = px.scatter
    elif kind == 'bar':
        plot_fun = px.bar
    # elif kind =='density_heatmap':
    #    plot_fun = px.density_heatmap
    elif kind == 'imshow':
        plot_fun = px.imshow
    elif kind == 'scatter3d':
        plot_fun = px.scatter_3d
    elif kind == 'box':
        plot_fun = px.box
    elif kind == 'hist':
        plot_fun = px.histogram
    else:
        raise ValueError('Function not yet implemented')

    return plot_fun


#############################
## MAIN FUNCTION: mmp_plot ##
#############################
def mmp_plot(data=None, kind='lines', x=None, y=None, z=None, show=True, main_logo_source=None, proj_logo_source=None, **param):
    # Assess input data
    if data is not None:
        if (x is None) and (kind != 'hist'):
            x = data.index
        if (y is None) and (kind != 'hist'):
            y = data.columns
    else:
        NoneType = type(None)
        if isinstance(x, NoneType) or isinstance(y, NoneType):
            raise TypeError('Both x and y must be specified if data is None')

    plot_fun = fun_selector(kind)  # Select type of plot

    fun_params, traces_params, layout_params = process_params(param, kind)  # Param preprocess

    fig = mmp_inner_plot(plot_fun, data, x, y, z, main_logo_source, proj_logo_source, fun_params, traces_params,
                         layout_params)  # Plot function

    if show:
        fig.show()

    return fig