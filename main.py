import yaml
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from modules import download_link

with open(f'modules/params.yml', 'r') as params_file:
    params = yaml.safe_load(params_file)

# aqui, atribuir novos nomes às series
cards_df = pd.read_json(
        requests.request("GET", 
        f"https://api.trello.com/1/boards/{params['board_id']}/cards",
        params = params['con_params']).text)\
        [['id', 'desc', 'name', 'idList']]

lists_df = pd.read_json(
        requests.request("GET",
        f"https://api.trello.com/1/boards/{params['board_id']}/lists",
        params = params['con_params']).text)\
        [['id', 'name']]

# para poder ordenar linhas de acordo com estes, não alfabeticamente
lists_df['cat'] = [n for n in range(0, len(lists_df))]

df = lists_df.merge(cards_df,
    left_on = 'id',
    right_on = 'idList',
    how = 'left')\
    [['name_x', 'name_y', 'cat']]

df['count'] = df['name_y'].apply(lambda x: 1 if type(x) != float else 0)

df = df.groupby(['name_x', 'cat'])['count']\
    .sum()\
    .to_frame()\
    .sort_values('cat')\
    .reset_index()\
    .drop('cat', axis=1)

# nomes de colunas hard coded (se é que isso é válido)
# slice_df = df.loc[df['name_x'].isin(['Funil 1 | Entrevista RH',
#                                      'Funil 1.1 | Desafio técnico',
#                                      'Funil 2 | Etapa Técnica',
#                                      'Funil 3 | Entrevista Final'])]
slice_df = df.copy()
chart_kwargs = params['chart_kwargs']
color_palette = [color for colors in zip(
                chart_kwargs['palette']['silver'],
                chart_kwargs['palette']['gold'],
                chart_kwargs['palette']['cyan']) 
            for color in colors]
colors = color_palette[:len(df.columns)]

fig = px.bar(df,
             x=slice_df['name_x'], y=slice_df['count'],
             color_discrete_sequence=colors, title=None,
             width=900, height=500)

fig.update_yaxes(chart_kwargs['y_axes'])
fig.update_xaxes(chart_kwargs['y_axes'])
fig.update_layout(chart_kwargs['layout'])

st.plotly_chart(fig,
            use_container_width=False, config={'displayModeBar':False}, layout=fig.layout)

st.dataframe(slice_df)
st.markdown(download_link.download_link(df), unsafe_allow_html=True)