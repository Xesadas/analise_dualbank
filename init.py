import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Carregar os dados (ajuste o caminho do arquivo)
df = pd.read_excel("stores.xlsx")

# Limpeza básica dos dados
meses = ['Faturamento Dezembro', 'Faturamento Janeiro', 'Faturamento Fevereiro']
for mes in meses:
    df[mes] = pd.to_numeric(df[mes], errors='coerce').fillna(0)

# Criar aplicação Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Análise de Faturamento - Dashboard Interativo", style={'textAlign': 'center'}),
    
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='estabelecimento-dropdown',
                options=[{'label': nome, 'value': nome} for nome in df['ESTABELECIMENTO NOME1'].unique()],
                multi=True,
                placeholder="Selecione os estabelecimentos"
            )
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Dropdown(
                id='status-dropdown',
                options=[{'label': status, 'value': status} for status in df['STATUS'].unique()],
                multi=True,
                placeholder="Filtrar por status"
            )
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),
    
    dcc.Graph(id='faturamento-grafico'),
    
    dcc.Graph(id='media-grafico'),
    
    html.Div([
        html.H3("Dados Detalhados"),
        html.Div(id='tabela-dados')
    ])
])

@app.callback(
    [Output('faturamento-grafico', 'figure'),
     Output('media-grafico', 'figure'),
     Output('tabela-dados', 'children')],
    [Input('estabelecimento-dropdown', 'value'),
     Input('status-dropdown', 'value')]
)
def update_graph(selected_estabelecimentos, selected_status):
    filtered_df = df.copy()
    
    # Aplicar filtros
    if selected_status:
        filtered_df = filtered_df[filtered_df['STATUS'].isin(selected_status)]
    if selected_estabelecimentos:
        filtered_df = filtered_df[filtered_df['ESTABELECIMENTO NOME1'].isin(selected_estabelecimentos)]
    
    # Gráfico de faturamento por mês
    fig1 = px.line(
        filtered_df,
        x='ESTABELECIMENTO NOME1',
        y=meses,
        title='Faturamento Mensal por Estabelecimento',
        labels={'value': 'Faturamento (R$)', 'variable': 'Mês'}
    )
    
    # Gráfico de média de faturamento
    fig2 = px.bar(
        filtered_df,
        x='ESTABELECIMENTO NOME1',
        y='Média de Faturamento',
        title='Média de Faturamento por Estabelecimento',
        color='STATUS'
    )
    
    # Tabela interativa
    tabela = dash.dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in filtered_df.columns],
        data=filtered_df.to_dict('records'),
        style_table={'overflowX': 'auto'},
        page_size=10
    )
    
    return fig1, fig2, tabela

if __name__ == '__main__':
    app.run_server(debug=True)          