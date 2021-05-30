import yaml
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from modules import download_link
import datetime
import base64

# with open(f'modules/params.yml', 'r') as params_file:
#     params = yaml.safe_load(params_file)

card_response = requests.get('https://o8rvfaouii.execute-api.sa-east-1.amazonaws.com/default/card-data-trello')
list_response = requests.get('https://n1vj1w01xi.execute-api.sa-east-1.amazonaws.com/default/list-data-trello')

cards_df = pd.DataFrame(card_response.json())[['id', 'desc', 'name', 'idList', 'labels']]
lists_df = pd.DataFrame(list_response.json())[['id', 'name']]

lists_df.columns = ['idList', 'list_name']
lists_df['cat'] = [n for n in range(0, len(lists_df))]

st.dataframe(cards_df)
st.dataframe(lists_df)

st.markdown(download_link.download_link(cards_df), unsafe_allow_html=True)