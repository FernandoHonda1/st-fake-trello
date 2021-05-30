import yaml
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from modules import download_link
import datetime
import base64
import numpy as np

with open(f'modules/params.yml', 'r') as params_file:
    params = yaml.safe_load(params_file)

color_palette = [color for colors in zip(
                params['chart_kwargs']['palette']['silver'],
                params['chart_kwargs']['palette']['gold'],
                params['chart_kwargs']['palette']['cyan']) 
            for color in colors]

card_response = requests.get('https://o8rvfaouii.execute-api.sa-east-1.amazonaws.com/default/card-data-trello')
list_response = requests.get('https://n1vj1w01xi.execute-api.sa-east-1.amazonaws.com/default/list-data-trello')

cards_df = pd.DataFrame(card_response.json())[['id', 'desc', 'name', 'idList', 'labels']]
lists_df = pd.DataFrame(list_response.json())[['id', 'name']]

lists_df.columns = ['idList', 'list_name']
lists_df['cat'] = [n for n in range(0, len(lists_df))]

table_data = []
for n in range(0, len(cards_df)):
    for dici in cards_df.iloc[n]['labels']:
        if 'color' in dici.keys():
            if dici['color'] == 'lime':
                table_data.append([dici['name'], cards_df.iloc[n]['idList']])
                
table_data = pd.DataFrame(table_data)

table_data.columns = ['codigo_vaga', 'idList']
table_data['count'] = 1

table_data = table_data.merge(lists_df, on = 'idList')

sum_by_code = table_data.copy() 

table_data = table_data.pivot_table(index = 'codigo_vaga', columns = 'list_name', aggfunc = np.sum)\
                                    .fillna(0)\
                                    .reset_index()\
                                    .set_index('codigo_vaga')['count']\
                                    .reset_index()

expected_steps = ['Mapeamento', 'Screening', 'Entrevista RH', 'Desafio técnico', 'Etapa técnica', 'Entrevista final', 'Oferta']

for i in [step for step in expected_steps if step not in table_data.columns.tolist()]: # 'imputando' nomes de etapas com zero participantes
    exec(f"table_data['{i}'] = 0")
    
table_data = table_data[['codigo_vaga', 'Mapeamento', 'Screening', 'Entrevista RH', 'Desafio técnico', 'Etapa técnica', 'Entrevista final', 'Oferta']].set_index('codigo_vaga')
table_data = table_data.astype(int)
st.dataframe(table_data)

st.markdown(download_link.download_link(table_data), unsafe_allow_html=True)

# plot

grpb_data = lists_df.merge(cards_df, on = 'idList', how = 'left')
grpb_data['count'] = grpb_data['name'].apply(lambda x: 1 if type(x) != float else 0)

grpb_data = grpb_data.groupby(['list_name', 'cat'])['count']\
                                .sum()\
                                .to_frame()\
                                .sort_values('cat')\
                                .reset_index()\
                                .drop('cat', axis=1)

grpb_data = grpb_data.loc[grpb_data['list_name'].isin(['Mapeamento', 'Screening', 'Entrevista RH', 'Desafio técnico',
                                                    'Etapa técnica', 'Entrevista final', 'Oferta'])]

colors = color_palette[:len(grpb_data.columns)]

fig = px.bar(grpb_data,
            x=grpb_data['list_name'], y=grpb_data['count'],
            color_discrete_sequence=colors, title=None,
            width=900, height=500)

fig.update_yaxes(params['chart_kwargs']['y_axes'])
fig.update_xaxes(params['chart_kwargs']['x_axes'])
fig.update_layout(params['chart_kwargs']['layout'])

st.plotly_chart(fig,
    use_container_width=False, config={'displayModeBar':False}, layout=fig.layout)