#########################
## IMPORT DEPENDENCIES ##
#########################
import plotly.graph_objects as go
import plotly.io as pio
from collections import defaultdict
import pandas as pd
import plotly.express as px
import base64

######################
## THEME DEFINITION ##
######################
pio.templates['mmp_theme'] = go.layout.Template({
    'data': {'bar': [{'error_x': {'color': '#000000', 'thickness': 2, 'width': 5},
                      'error_y': {'color': '#000000', 'thickness': 2, 'width': 5},
                      'marker': {'line': {'color': 'white', 'width': 0.5},
                                 'pattern': {'fillmode': 'overlay', 'size': 10, 'solidity': 0.2}},
                      'type': 'bar'}],
             'barpolar': [{'marker': {'line': {'color': 'white', 'width': 0.5},
                                      'pattern': {'fillmode': 'overlay', 'size': 10, 'solidity': 0.2}},
                           'type': 'barpolar'}],
             'carpet': [{'aaxis': {'endlinecolor': '#2a3f5f',
                                   'gridcolor': '#C8D4E3',
                                   'linecolor': '#C8D4E3',
                                   'minorgridcolor': '#C8D4E3',
                                   'startlinecolor': '#2a3f5f'},
                         'baxis': {'endlinecolor': '#2a3f5f',
                                   'gridcolor': '#C8D4E3',
                                   'linecolor': '#C8D4E3',
                                   'minorgridcolor': '#C8D4E3',
                                   'startlinecolor': '#2a3f5f'},
                         'type': 'carpet'}],
             'choropleth': [{'colorbar': {'outlinewidth': 0, 'ticks': ''}, 'type': 'choropleth'}],
             'contour': [{'colorbar': {'outlinewidth': 0, 'ticks': ''},
                          'colorscale': [[0.0, '#0d0887'],
                                         [0.1111111111111111, '#46039f'],
                                         [0.2222222222222222, '#7201a8'],
                                         [0.3333333333333333, '#9c179e'],
                                         [0.4444444444444444, '#bd3786'],
                                         [0.5555555555555556, '#d8576b'],
                                         [0.6666666666666666, '#ed7953'],
                                         [0.7777777777777778, '#fb9f3a'],
                                         [0.8888888888888888, '#fdca26'],
                                         [1.0, '#f0f921']],
                          'type': 'contour'}],
             'contourcarpet': [{'colorbar': {'outlinewidth': 0, 'ticks': ''}, 'type': 'contourcarpet'}],
             'heatmap': [{'colorbar': {'outlinewidth': 0, 'ticks': ''},
                          'colorscale': [[0.0, '#0d0887'],
                                         [0.1111111111111111, '#46039f'],
                                         [0.2222222222222222, '#7201a8'],
                                         [0.3333333333333333, '#9c179e'],
                                         [0.4444444444444444, '#bd3786'],
                                         [0.5555555555555556, '#d8576b'],
                                         [0.6666666666666666, '#ed7953'],
                                         [0.7777777777777778, '#fb9f3a'],
                                         [0.8888888888888888, '#fdca26'],
                                         [1.0, '#f0f921']],
                          'type': 'heatmap'}],
             'heatmapgl': [{'colorbar': {'outlinewidth': 0, 'ticks': ''},
                            'colorscale': [[0.0, '#0d0887'],
                                           [0.1111111111111111, '#46039f'],
                                           [0.2222222222222222, '#7201a8'],
                                           [0.3333333333333333, '#9c179e'], 
                                           [0.4444444444444444, '#bd3786'],
                                           [0.5555555555555556, '#d8576b'],
                                           [0.6666666666666666, '#ed7953'],
                                           [0.7777777777777778, '#fb9f3a'],
                                           [0.8888888888888888, '#fdca26'],
                                           [1.0, '#f0f921']],
                            'type': 'heatmapgl'}],
             'histogram': [{'marker': {'pattern': {'fillmode': 'overlay', 'size': 10, 'solidity': 0.2}},
                            'type': 'histogram'}],
             'histogram2d': [{'colorbar': {'outlinewidth': 0, 'ticks': ''},
                              'colorscale': [[0.0, '#0d0887'],
                                             [0.1111111111111111, '#46039f'],
                                             [0.2222222222222222, '#7201a8'],
                                             [0.3333333333333333, '#9c179e'],
                                             [0.4444444444444444, '#bd3786'],
                                             [0.5555555555555556, '#d8576b'],
                                             [0.6666666666666666, '#ed7953'],
                                             [0.7777777777777778, '#fb9f3a'],
                                             [0.8888888888888888, '#fdca26'], 
                                             [1.0, '#f0f921']],
                              'type': 'histogram2d'}],
             'histogram2dcontour': [{'colorbar': {'outlinewidth': 0, 'ticks': ''},
                                     'colorscale': [[0.0, '#0d0887'],
                                                    [0.1111111111111111, '#46039f'],
                                                    [0.2222222222222222, '#7201a8'],
                                                    [0.3333333333333333, '#9c179e'],
                                                    [0.4444444444444444, '#bd3786'],
                                                    [0.5555555555555556, '#d8576b'],
                                                    [0.6666666666666666, '#ed7953'],
                                                    [0.7777777777777778, '#fb9f3a'],
                                                    [0.8888888888888888, '#fdca26'],
                                                    [1.0, '#f0f921']],
                                     'type': 'histogram2dcontour'}],
             'mesh3d': [{'colorbar': {'outlinewidth': 0, 'ticks': ''}, 'type': 'mesh3d'}],
             'parcoords': [{'line': {'colorbar': {'outlinewidth': 0, 'ticks': ''}}, 'type': 'parcoords'}],
             'pie': [{'automargin': True, 'type': 'pie'}],
             'scatter': [{'marker': {'colorbar': {'outlinewidth': 0, 'ticks': ''}}, 'type': 'scatter'}],
             'scatter3d': [{'line': {'colorbar': {'outlinewidth': 0, 'ticks': ''}},
                            'marker': {'colorbar': {'outlinewidth': 0, 'ticks': ''}},
                            'type': 'scatter3d'}],
             'scattercarpet': [{'marker': {'colorbar': {'outlinewidth': 0, 'ticks': ''}}, 'type': 'scattercarpet'}],
             'scattergeo': [{'marker': {'colorbar': {'outlinewidth': 0, 'ticks': ''}}, 'type': 'scattergeo'}],
             'scattergl': [{'marker': {'colorbar': {'outlinewidth': 0, 'ticks': ''}}, 'type': 'scattergl'}],
             'scattermapbox': [{'marker': {'colorbar': {'outlinewidth': 0, 'ticks': ''}}, 'type': 'scattermapbox'}],
             'scatterpolar': [{'marker': {'colorbar': {'outlinewidth': 0, 'ticks': ''}}, 'type': 'scatterpolar'}],
             'scatterpolargl': [{'marker': {'colorbar': {'outlinewidth': 0, 'ticks': ''}}, 'type': 'scatterpolargl'}],
             'scatterternary': [{'marker': {'colorbar': {'outlinewidth': 0, 'ticks': ''}}, 'type': 'scatterternary'}],
             'surface': [{'colorbar': {'outlinewidth': 0, 'ticks': ''},
                          'colorscale': [[0.0, '#0d0887'],
                                         [0.1111111111111111, '#46039f'],
                                         [0.2222222222222222, '#7201a8'],
                                         [0.3333333333333333, '#9c179e'],
                                         [0.4444444444444444, '#bd3786'],
                                         [0.5555555555555556, '#d8576b'],
                                         [0.6666666666666666, '#ed7953'],
                                         [0.7777777777777778, '#fb9f3a'],
                                         [0.8888888888888888, '#fdca26'],
                                         [1.0, '#f0f921']],
                          'type': 'surface'}],
             'table': [{'cells': {'fill': {'color': '#EBF0F8'}, 'line': {'color': 'white'}},
                        'header': {'fill': {'color': '#C8D4E3'}, 'line': {'color': 'white'}},
                        'type': 'table'}],
    },
    'layout': {'annotationdefaults': {'arrowcolor': '#2a3f5f', 'arrowhead': 0, 'arrowwidth': 1},
               'autotypenumbers': 'strict',
               'coloraxis': {'colorbar': {'outlinewidth': 0, 'ticks': ''}},
               'colorscale': {'diverging': [[0, '#8e0152'], [0.1, '#c51b7d'],
                                            [0.2, '#de77ae'], [0.3, '#f1b6da'],
                                            [0.4, '#fde0ef'], [0.5, '#f7f7f7'],
                                            [0.6, '#e6f5d0'], [0.7, '#b8e186'],
                                            [0.8, '#7fbc41'], [0.9, '#4d9221'],
                                            [1, '#276419']],
                              'sequential': [[0.0, '#0d0887'],
                                             [0.1111111111111111, '#46039f'],
                                             [0.2222222222222222, '#7201a8'],
                                             [0.3333333333333333, '#9c179e'],
                                             [0.4444444444444444, '#bd3786'],
                                             [0.5555555555555556, '#d8576b'],
                                             [0.6666666666666666, '#ed7953'],
                                             [0.7777777777777778, '#fb9f3a'],
                                             [0.8888888888888888, '#fdca26'],
                                             [1.0, '#f0f921']],
                              'sequentialminus': [[0.0, '#0d0887'],
                                                  [0.1111111111111111, '#46039f'],
                                                  [0.2222222222222222, '#7201a8'],
                                                  [0.3333333333333333, '#9c179e'],
                                                  [0.4444444444444444, '#bd3786'],
                                                  [0.5555555555555556, '#d8576b'],
                                                  [0.6666666666666666, '#ed7953'],
                                                  [0.7777777777777778, '#fb9f3a'],
                                                  [0.8888888888888888, '#fdca26'],
                                                  [1.0, '#f0f921']]},
               'colorway': ['#1F77B4', '#FF7F0E', '#2CA02C', '#D62728', '#9467BD', '#8C564B',
                            '#E377C2', '#7F7F7F', '#BCBD22', '#17BECF'],
               'font': {'color': '#06476a', 'family': 'Comfortaa', 'size': 18},
               'geo': {'bgcolor': 'white',
                       'lakecolor': 'white',
                       'landcolor': 'white',
                       'showlakes': True,
                       'showland': True,
                       'subunitcolor': '#C8D4E3'},
               'hoverlabel': {'align': 'left'},
               'hovermode': 'closest',
               'images': [{'name': "mmplogo",
                          #  'source': "https://www.milanomultiphysics.it/wp-content/uploads/2019/02/MMP_logo-piccolo.png",
                          # 'source': "https://media.istockphoto.com/photos/longspine-porcupinefish-diodon-holocanthus-picture-id92041422?s=612x612",
                           'source': 'data:image/png;base64,{}'.format(base64.b64encode(open("gdrive/Shareddrives/ufficio-hs-mmp/logo-v4.png", 'rb').read()).decode()),
                           'xref': "paper", 'yref': "paper",
                           'x': 1, 'y': 1.01,
                           'sizex':1, 'sizey': 0.12,
                           'xanchor': "right", 'yanchor': "bottom",
                           'opacity':1, 'visible':True},
              #              {'name': "additionallogo",
              #              'source': "https://images.plot.ly/language-icons/api-home/python-logo.png",
              #              'xref': "paper", 'yref': "paper",
              #              'x': 0.9, 'y': 1,
              #              'sizex':0.1, 'sizey': 0.15,
              #              'xanchor': "right", 'yanchor': "bottom",
              #              'opacity':1, 'visible':True}
                            ],
               'mapbox': {'style': 'light'},
               'paper_bgcolor': 'white',
               'plot_bgcolor': 'white',
               'polar': {'angularaxis': {'gridcolor': '#EBF0F8', 'linecolor': '#EBF0F8', 'ticks': ''},
                         'bgcolor': 'white',
                         'radialaxis': {'gridcolor': '#EBF0F8', 'linecolor': '#EBF0F8', 'ticks': ''}},
               'scene': {'xaxis': {'backgroundcolor': 'white',
                                   'gridcolor': '#DFE8F3',
                                   'gridwidth': 3,
                                   'linecolor': '#EBF0F8',
                                   'showbackground': True,
                                   'ticks': 'outside',
                                   'zerolinecolor': '#EBF0F8'},
                         'yaxis': {'backgroundcolor': 'white',
                                   'gridcolor': '#DFE8F3',
                                   'gridwidth': 3,
                                   'linecolor': '#EBF0F8',
                                   'showbackground': True,
                                   'ticks': '',
                                   'zerolinecolor': '#EBF0F8'},
                         'zaxis': {'backgroundcolor': 'white',
                                   'gridcolor': '#DFE8F3',
                                   'gridwidth': 3,
                                   'linecolor': '#EBF0F8',
                                   'showbackground': True,
                                   'ticks': '',
                                   'zerolinecolor': '#EBF0F8'}},
               'shapedefaults': {'line': {'color': '#2a3f5f'}},
               'ternary': {'aaxis': {'gridcolor': '#DFE8F3', 'linecolor': '#A2B1C6', 'ticks': ''},
                           'baxis': {'gridcolor': '#DFE8F3', 'linecolor': '#A2B1C6', 'ticks': ''},
                           'bgcolor': 'white',
                           'caxis': {'gridcolor': '#DFE8F3', 'linecolor': '#A2B1C6', 'ticks': ''}},
               'title': {'x': 0.05, 'font': {'family': 'Comfortaa', 'size': 25, 'color': '#06476a'}},#, 'text': ''},
               'xaxis': {'automargin': True,
                         'gridcolor': '#9dddf0',
                         'linecolor': '#9dddf0',
                         'ticks': 'outside',
                         'tickfont': {'family': 'Comfortaa', 'size': 18},
                         'title': {'standoff': 15, 'font': {'family': 'Comfortaa', 'size': 20}},
                         'zerolinecolor': '#9dddf0',
                         'zerolinewidth': 1},
               'yaxis': {'automargin': True,
                         'gridcolor': '#9dddf0',
                         'linecolor': '#9dddf0',
                         'ticks': 'outside',
                         'tickfont': {'family': 'Comfortaa', 'size': 18},
                         'title': {'standoff': 15, 'font': {'family': 'Comfortaa', 'size': 20}},
                         'zerolinecolor': '#9dddf0',
                         'zerolinewidth': 1},
               'width': 1500,
               'height': 900},
               
})

##########################
## SET THEME AS DEFAULT ##
##########################
pio.templates.default = 'mmp_theme'


##############################
## LIST OF INPUT PARAMETERS ##
##############################
input_params = {'data': 'DataFrame with data to be plot',
                'kind': 'Type of plot. Implemented type are: \'line\', \'scatter\', \'bar\', \'imshow\', \'scatter3d\', \'box\', \'hist\'',
                'x': 'Name of the dataframe column to be used on the x-axis (if None, data.index is used)',
                'y': 'Name of the dataframe column to be used on the y-axis (if None, data.columns is used)',
                'z': 'Name of the dataframe column to be used on the z-axis (only for 3D plots of imshow)',
                'show': 'bool, if True, the plot is shown',
                'mmp_logo': 'bool, if True, main company logo is displayed',
                'proj_logo_source': 'str, url or path for additional project logo'
                }


#################################
## LIST OF ACCEPTED PARAMETERS ##
#################################
accepted_params = {' GENERAL INFO': 'The following parameters ',
                   'title': 'Plot title (str, optional)',
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
                   'quartilemethod': 'Method to compute quartiles (str, \'exclusive\', \'inclusive\', \'linear\', only for kind=\'box\')'
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
    if kind == 'scatter3d':
        layouts['scene'].update(xaxis=dict(title=param.pop('xlabel', None)),
                                yaxis=dict(title=param.pop('ylabel', None)),
                                zaxis=dict(title=param.pop('zlabel', None)))
    
    return param, traces, layouts

#####################
## FNC: INNER PLOT ##
#####################
def mmp_inner_plot(plot_fun, data, x, y, z, mmp_logo, proj_logo_source, fun_params, traces_params, layout_params):

    pio.templates['mmp_theme'].layout.images[0]['visible'] = mmp_logo   
    
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
    
    img_list = []
    # if mmp_logo: 
    #     img_mmp_dict = {'name': "mmplogo",
    #                     'source': "https://media.istockphoto.com/photos/longspine-porcupinefish-diodon-holocanthus-picture-id92041422?s=612x612",
    #                     #'source': "https://www.milanomultiphysics.it/wp-content/uploads/2019/02/MMP_logo-piccolo.png",
    #                     'xref': "paper", 'yref': "paper",
    #                     'x': 1, 'y': 1.01,
    #                     'sizex':1, 'sizey': 0.12,
    #                     'xanchor': "right", 'yanchor': "bottom",
    #                     'opacity':1, 'visible':True}
    #     img_list.append(img_mmp_dict)

    if proj_logo_source is not None:
      if 'https' in proj_logo_source:
          proj_logo = proj_logo_source
      else:
          file_logo = base64.b64encode(open(proj_logo_source, 'rb').read())
          proj_logo = 'data:image/png;base64,{}'.format(file_logo.decode())
      img_add_dict = {'name': "additionallogo",
                      'source': proj_logo,
                      'xref': "paper", 'yref': "paper",
                      'x': 0.8, 'y': 1.01, 'sizex': 1, 'sizey': 0.12,
                      'xanchor': "right", 'yanchor': "bottom",
                      'opacity': 1, 'visible': True}
      img_list.append(img_add_dict)
      # fig.update_layout(images=[dict(name="additionallogo",
      #                                source=proj_logo,
      #                                xref="paper", yref="paper",
      #                                x=0.8, y=1.01, sizex=1, sizey=0.12,
      #                                xanchor="right", yanchor="bottom",
      #                                opacity=1, visible=True)])
    
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
    #elif kind =='density_heatmap':
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
def mmp_plot(data=None, kind='lines', x=None, y=None, z=None, show=True, mmp_logo=False, proj_logo_source=None, **param):

    # Assess input data
    if data is not None:
        if x is None:
            x = data.index
        if y is None:
            y = data.columns
    else:
        print('qui')
        NoneType = type(None)
        if isinstance(x, NoneType) and isinstance(y, NoneType):
            raise TypeError('Both x and y must be specified if data is None')

    plot_fun = fun_selector(kind)  # Select type of plot

    fun_params, traces_params, layout_params = process_params(param, kind)  # Param preprocess

    fig = mmp_inner_plot(plot_fun, data, x, y, z, mmp_logo, proj_logo_source, fun_params, traces_params, layout_params)  # Plot function

    if show:
      fig.show()
      return fig
    else:
      return fig


