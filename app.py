import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import openpyxl

df = pd.read_excel('stores.xlsx', engine='openpyxl')

meses = {
    'Faturamento Dezembro': 'Dezembro',
    'Faturamento Janeiro': 'Janeiro',
    'Faturamento Fevereiro': 'Fevereiro'
}

df_long = df.melt(
    id_vars=['ESTABELECIMENTO NOME1', 'STATUS'],
    value_vars=meses.keys(),
    var_name='Mês',
    value_name='Faturamento'
)


df_long['Mês'] = df_long['Mês'].map(meses)




# =====================================
# PALETA DE CORES & ESTILOS
# =====================================
COLORS = {
    'background': '#f8f9fa',
    'text': '#2c3e50',
    'primary': '#3498db',
    'secondary': '#95a5a6',
    'success': '#2ecc71',
    'danger': '#e74c3c',
    'highlight': '#f1c40f',
    'card': '#ffffff',
    'plot_bg': '#ffffff'
}

FONT_STYLE = {
    'family': 'Open Sans, sans-serif',
    'size': 14,
    'color': COLORS['text']
}

# =====================================
# CONFIGURAÇÃO DA APLICAÇÃO
# =====================================
app = dash.Dash(__name__)
server = app.server

# =====================================
# LAYOUT PRINCIPAL
# =====================================
app.layout = html.Div(style={'backgroundColor': COLORS['background'], 'minHeight': '100vh'}, children=[
    html.Div(className='container', style={'padding': '30px', 'maxWidth': '1200px', 'margin': '0 auto'}, children=[
        
        # Título
        html.Div(className='header', style={'textAlign': 'center', 'marginBottom': '40px'}, children=[
            html.H1("📈 Dashboard de Faturamento", 
                   style={'color': COLORS['primary'], 
                          'fontSize': '2.5em',
                          'textShadow': '2px 2px 4px rgba(0,0,0,0.1)'}),
            html.P("Análise comparativa mensal de desempenho comercial", 
                  style={'color': COLORS['secondary'], 'fontSize': '1.1em'})
        ]),
        
        # Controles
        html.Div(className='control-card', style={
            'backgroundColor': COLORS['card'],
            'padding': '25px',
            'borderRadius': '15px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
            'marginBottom': '30px'
        }, children=[
            dcc.Dropdown(
                id='cliente-dropdown',
                options=[{'label': nome, 'value': nome} 
                        for nome in df['ESTABELECIMENTO NOME1'].unique()],
                multi=True,
                placeholder="🔍 Selecione até 5 clientes...",
                style={
                    'width': '100%',
                    'borderRadius': '8px',
                    'border': f'1px solid {COLORS["secondary"]}'
                },
                className='custom-dropdown',
                maxHeight=300
            )
        ]),
        
        # Gráfico
        html.Div(className='graph-card', style={
            'backgroundColor': COLORS['card'],
            'padding': '20px',
            'borderRadius': '15px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
        }, children=[
            dcc.Graph(
                id='faturamento-grafico',
                style={'height': '65vh'},
                config={'displayModeBar': True, 'scrollZoom': False}
            )
        ]),
        
        # Tabela
        html.Div(className='table-card', style={
            'marginTop': '30px',
            'backgroundColor': COLORS['card'],
            'borderRadius': '15px',
            'overflow': 'hidden',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
        }, children=[
            dash_table.DataTable(
                id='tabela-variacao',
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'center',
                    'padding': '12px',
                    'fontFamily': FONT_STYLE['family'],
                    'border': f'1px solid {COLORS["background"]}'
                },
                style_header={
                    'backgroundColor': COLORS['primary'],
                    'color': 'white',
                    'fontWeight': 'bold',
                    'borderRadius': '0',
                    'textTransform': 'uppercase'
                },
                style_data_conditional=[
                    {
                        'if': {'column_id': 'Variação %', 'filter_query': '{Variação %} > 0'},
                        'color': COLORS['success'],
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {'column_id': 'Variação %', 'filter_query': '{Variação %} < 0'},
                        'color': COLORS['danger'],
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f8f9fa'
                    }
                ]
            )
        ])
    ])
])

@app.callback(
    Output('faturamento-grafico', 'figure'),
    Output('tabela-variacao', 'data'),
    Output('tabela-variacao', 'columns'),
    Input('cliente-dropdown', 'value')
)
def update_graph(clientes_selecionados):
    if not clientes_selecionados:
        return px.scatter(title="Selecione clientes no dropdown acima"), [], []

    # Filtrar e ordenar dados
    filtered_df = df_long[df_long['ESTABELECIMENTO NOME1'].isin(clientes_selecionados)].copy()
    filtered_df.sort_values(['ESTABELECIMENTO NOME1', 'Mês'], inplace=True)

    # Calcular variações
    filtered_df['Faturamento Anterior'] = filtered_df.groupby('ESTABELECIMENTO NOME1')['Faturamento'].shift(1)
    filtered_df['Variação R$'] = filtered_df['Faturamento'] - filtered_df['Faturamento Anterior']
    filtered_df['Variação %'] = np.where(
        filtered_df['Faturamento Anterior'] != 0,
        (filtered_df['Variação R$'] / filtered_df['Faturamento Anterior']) * 100,
        np.nan
    )
    table_df = filtered_df[filtered_df['Mês'] != 'Dezembro'].copy()
    table_df = table_df[['ESTABELECIMENTO NOME1', 'Mês', 'Variação R$', 'Variação %']]
    table_df['Variação R$'] = table_df['Variação R$'].apply(lambda x: f'R$ {x:,.2f}' if pd.notna(x) else 'N/A')
    table_df['Variação %'] = table_df['Variação %'].apply(lambda x: f'{x:.2f}%' if pd.notna(x) else 'N/A')

    columns = [
        {'name': 'Cliente', 'id': 'ESTABELECIMENTO NOME1'},
        {'name': 'Mês', 'id': 'Mês'},
        {'name': 'Variação R$', 'id': 'Variação R$'},
        {'name': 'Variação %', 'id': 'Variação %'}
    ]

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

    # Adicionar setas de variação
    for trace in fig.data:
        client_name = trace.name
        client_data = filtered_df[filtered_df['ESTABELECIMENTO NOME1'] == client_name]
        for i, row in client_data.iterrows():
            if pd.notna(row['Variação R$']):
                symbol = '▲' if row['Variação R$'] > 0 else '▼'
                color = 'green' if row['Variação R$'] > 0 else 'red'
                fig.add_annotation(
                    x=row['Mês'],
                    y=row['Faturamento'],
                    text=symbol,
                    showarrow=False,
                    font=dict(color=color, size=12),
                    xshift=10
                )

    # Personalizar layout
    fig.update_layout(
        plot_bgcolor=COLORS['plot_bg'],
        paper_bgcolor=COLORS['card'],
        font=FONT_STYLE,
        hoverlabel=dict(
            bgcolor=COLORS['primary'],
            font_size=14,
            font_family=FONT_STYLE['family']
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor=COLORS['background'],
            linecolor=COLORS['secondary']
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS['background'],
            linecolor=COLORS['secondary']
        ),
        margin=dict(l=40, r=40, t=80, b=40),
        title_font=dict(size=20, color=COLORS['primary']),
        transition={'duration': 300}
    )
    
    # Personalização das linhas
    for trace in fig.data:
        trace.line.width = 3
        trace.line.shape = 'spline'
        trace.marker.size = 10
        trace.marker.line.width = 2
    
    return fig, table_df.to_dict('records'), columns

if __name__ == '__main__':
    app.run_server(debug=True)