import pandas as pd
from datetime import datetime
import plotly .express as px
import numpy as np
import dash
from dash import dcc, html

app = dash.Dash(__name__)

df = pd.read_excel('stores.xlsx', sheet_name='listagem-de-estabelecimentos')
df['DATA DE CADASTRO'] = pd.to_datetime(df['DATA DE CADASTRO'], format='%d/%m/%Y')
df['CLIENTE NOVO'] = (datetime.now() - df['DATA DE CADASTRO']).dt.days <= 30

planos = {
    'NNA': 5000, 'NNB': 3000, 'SEM PLANO': 1000, 'nnpaytime2escrows d0': 2000
}
df['LUCRO_ESPERADO'] = df['PLANO PAG'].map(planos).fillna(2000)

import plotly.express as px

fig1 = px.pie(
    df, names='CLIENTE NOVO', 
    title='Proporção de Clientes Novos vs. Antigos'
)

fig2 = px.bar(
    df['STATUS'].value_counts(), 
    title='Status dos Clientes (Habilitados, Pendentes, etc)'
)
df['LUCRO_ATUAL'] = np.random.randint(500, 4000, size=len(df))
df['ALERTA'] = df['LUCRO_ATUAL'] < df['LUCRO_ESPERADO']

fig3 = px.scatter(
    df, x='ESTABELECIMENTO NOME1', y='LUCRO_ATUAL', 
    color='ALERTA', title='Clientes com Alerta de Baixo Lucro'
)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Análise de Clientes - Projeto Piloto"),
    dcc.Graph(figure=fig1),
    dcc.Graph(figure=fig2),
    dcc.Graph(figure=fig3)
])

if __name__ == '__main__':
    app.run_server(debug=True)