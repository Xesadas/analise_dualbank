import dash
from dash import html, dcc, Input, Output, dash_table, callback
import pandas as pd


dash.register_page(
    __name__,
    path='/dados',
    title='Dados Clientes',
    name='Dados dos clientes'
)

# Carregar dados
df = pd.read_excel('stores.xlsx', engine='openpyxl')

# Layout da página
layout = html.Div([
    html.Div([
        html.H1("📋 Dados Clientes", style={'color': '#a991f7', 'textAlign': 'center', 'padding': '20px'}),
        dcc.Input(
            id='search-input',
            placeholder='🔍 Digite o nome do cliente...',
            type='text',
            style={
                'width': '80%',
                'margin': '20px auto',
                'padding': '15px',
                'borderRadius': '25px',
                'border': '2px solid #a991f7',
                'backgroundColor': '#1a1a1a',
                'color': 'white'
            }
        ),
    ], style={'backgroundColor': '#000000'}),
    
    dash_table.DataTable(
        id='full-data-table',
        columns=[{"name": col, "id": col} for col in df.columns],
        data=df.to_dict('records'),
        page_size=20,
        style_table={
            'overflowX': 'auto',
            'width': '95%',
            'margin': '0 auto',
            'backgroundColor': '#1a1a1a'
        },
        style_cell={
            'textAlign': 'left',
            'padding': '12px',
            'fontFamily': 'Open Sans, sans-serif',
            'backgroundColor': '#262626',
            'color': 'white',
            'border': '1px solid #333333'
        },
        style_header={
            'backgroundColor': '#320c8a',
            'color': 'white',
            'fontWeight': 'bold',
            'textTransform': 'uppercase',
            'border': '1px solid #444444'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#333333'
            },
            {
                'if': {'state': 'active'},
                'backgroundColor': '#a991f7 !important',
                'border': '1px solid #ffffff'
            }
        ],
        filter_action='native',
        sort_action='native',
        page_current=0
    )
], style={'backgroundColor': '#000000', 'minHeight': '100vh'})

# Callback para filtro
@callback(
    Output('full-data-table', 'data'),
    Input('search-input', 'value')
)
def update_table(search_text):
    if search_text:
        filtered_df = df[df['ESTABELECIMENTO NOME1'].str.contains(search_text, case=False, na=False)]
        return filtered_df.to_dict('records')
    return df.to_dict('records')