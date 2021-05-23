
import base64
import datetime

def download_link(df):
    now = datetime.datetime.now()
    csv = df.to_csv().encode('latin1')
    b64 = base64.b64encode(csv).decode('utf-8')
    href = f'<a href="data:file/csv;base64,{b64}" download="{now.year}_{now.month}_{now.day}_funil.csv" target="_blank">Download csv</a>'
    return href
