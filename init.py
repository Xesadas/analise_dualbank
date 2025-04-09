import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Carregar os dados
df = pd.read_excel("stores.xlsx")

# Limpeza e preparação dos dados
meses = {
    'Faturamento Dezembro': 'Dezembro',
    'Faturamento Janeiro': 'Janeiro',
    'Faturamento Fevereiro': 'Fevereiro'
}

# Criar formato longo para os dados
df_long = df.melt(
    id_vars=['ESTABELECIMENTO NOME1', 'STATUS'],
    value_vars=meses.keys(),
    var_name='Mês',
    value_name='Faturamento'
)
df_long['Mês'] = df_long['Mês'].map(meses)

# Criar aplicação Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H1("Análise de Faturamento por Cliente", 
               style={'textAlign': 'center', 'color': '#2c3e50'}),
        
        html.Div([
            dcc.Dropdown(
                id='cliente-dropdown',
                options=[{'label': nome, 'value': nome} 
                        for nome in df['ESTABELECIMENTO NOME1'].unique()],
                multi=True,
                placeholder="Selecione até 5 clientes para comparar",
                style={'width': '100%', 'margin': '10px 0'}
            )
        ], style={'width': '80%', 'margin': '0 auto'}),
        
        dcc.Graph(
            id='faturamento-grafico',
            style={'height': '70vh', 'margin': '20px'}
        )
    ], style={'padding': '20px', 'maxWidth': '1200px', 'margin': '0 auto'})
])

@app.callback(
    Output('faturamento-grafico', 'figure'),
    Input('cliente-dropdown', 'value')
)
def update_graph(clientes_selecionados):
    if not clientes_selecionados:
        return px.scatter(title="Selecione clientes no dropdown acima")
    
    # Filtrar dados
    filtered_df = df_long[df_long['ESTABELECIMENTO NOME1'].isin(clientes_selecionados)]
    
    # Criar gráfico
    fig = px.line(
        filtered_df,
        x='Mês',
        y='Faturamento',
        color='ESTABELECIMENTO NOME1',
        markers=True,
        title='Comparativo de Faturamento Mensal',
        labels={'Faturamento': 'Faturamento (R$)', 'Mês': 'Mês'},
        template='plotly_white'
    )
    
    # Personalizar layout
    fig.update_layout(
        hovermode='x unified',
        legend=dict(
            title='Clientes',
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        yaxis_tickprefix='R$ ',
        yaxis_tickformat=',.2f',
        xaxis={'categoryorder': 'array', 'categoryarray': list(meses.values())}
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)