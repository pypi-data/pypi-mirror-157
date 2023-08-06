from typing import Iterable
import plotly.graph_objects as go
import plotly.express as px

from chemeye.tsne import sim_matrix
from chemeye.__asset_loader import default_simmat_options as default_options


class SimMat:
    def __init__(self, row_prints:Iterable, col_prints:Iterable, options:dict=default_options, 
                 key_type:str='ecfp') -> None:
        self.options = options
        sim_arr = sim_matrix(row_prints=row_prints, col_prints=col_prints, key_type=key_type)
        self.fig = px.imshow(sim_arr, color_continuous_scale=options['color_scale'])
        self.update()
        
    def __title(self) -> None:
        self.fig.update_layout(title_text=self.options['title']['text'])
        
        title_pos = self.options['title']['position']
        self.fig.update_layout(title_xanchor=title_pos['x'], title_yanchor=title_pos['y'])
        
    def __axes(self) -> None:
        x = self.options['axes']['x']
        y = self.options['axes']['y']
        
        self.fig.update_xaxes(visible=x['show'])
        self.fig.update_yaxes(visible=y['show'])
        
        self.fig.update_layout(xaxis_side=x['position'], yaxis_side=y['position'])
        
    def update(self) -> go.Figure:
        self.__title()
        self.__axes()
        return self.fig
