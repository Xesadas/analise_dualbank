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
        html.Div([
            html.H1("📋 Dados Clientes", className="titulo-dados"),
            dcc.Input(
                id='search-input',
                placeholder='🔍 Digite o nome do cliente...',
                type='text',
                className='campo-pesquisa'
            ),
        ], className='container-header animate__animated animate__fadeInDown'),
        
        html.Div([
            dash_table.DataTable(
                id='full-data-table',
                columns=[{"name": col, "id": col} for col in df.columns],
                data=df.to_dict('records'),
                page_size=20,
                filter_action='native',
                sort_action='native',
                sort_mode='multi',
                page_current=0,
                style_table={
                    'overflowX': 'auto',
                    'borderRadius': '10px',
                    'boxShadow': '0 4px 15px rgba(169,145,247,0.1)',
                    'margin': '20px auto',
                    'maxWidth': '100%',
                    'minWidth': '100%',
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '15px',
                    'fontFamily': 'Open Sans, sans-serif',
                    'backgroundColor': '#262626',
                    'color': 'white',
                    'border': '1px solid #333333',
                    'minWidth': '180px',  # Aumentado de 120px
                    'maxWidth': '500px',  # Novo parâmetro adicionado
                    'whiteSpace': 'normal',  # Permite quebra de linha
                    'overflow': 'visible'  # Mostra conteúdo completo
                },
                style_header={
                    'backgroundColor': '#320c8a',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textTransform': 'uppercase',
                    'border': '1px solid #444444',
                    'fontSize': '14px',
                    'minWidth': '180px'
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
                    },
                    {
                        'if': {'column_id': 'STATUS'},
                        'color': '#a991f7',
                        'fontWeight': 'bold'
                    }
                ],
                style_filter={
                    'backgroundColor': '#1a1a1a',
                    'color': 'white',
                    'border': '1px solid #333333'
                },
                css=[{
                    'selector': '.dash-spreadsheet-container .dash-spreadsheet-inner',
                    'rule': 'width: 100% !important; max-width: none !important;'
                }]
            )
        ], className='table-container animate__animated animate__fadeInUp')
    ], className='container-dados')
], className='main-container')

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