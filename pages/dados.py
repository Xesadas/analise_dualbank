import dash
from dash import html, dcc, Input, Output, dash_table, callback, State
import pandas as pd
import dash_bootstrap_components as dbc

dash.register_page(
    __name__,
    path='/dados',
    title='Dados Clientes',
    name='Dados dos clientes'
)

# Carregar dados
df = pd.read_excel('stores.xlsx', engine='openpyxl')

if 'REPRESENTANTE NOME1' in df.columns:
    # Filtrar valores nulos e vazios
    reps_clean = df['REPRESENTANTE NOME1'].dropna().replace('', pd.NA).dropna().unique()
    # Criar opções válidas
    representantes = [{'label': rep, 'value': rep} for rep in reps_clean if pd.notna(rep) and rep != '']
else:
    representantes = []

# Adicione uma opção padrão se necessário
if representantes:
    representantes.insert(0, {'label': 'Todos', 'value': 'ALL'})

# Layout da página
layout = html.Div([
    html.Div([
        html.Div([
            html.H1("📋 Dados Clientes", className="titulo-dados"),
            
            dbc.Row([
                dbc.Col(
                    dcc.Input(
                        id='search-input',
                        placeholder='🔍 Digite o nome do cliente...',
                        type='text',
                        className='campo-pesquisa',
                        style={'width': '100%'}
                    ),
                    md=6
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id='representante-filter',
                        options=representantes,
                        placeholder='👤 Filtrar por representante...',
                        multi=True,
                        className='dropdown-representantes',
                        clearable=True
                    ),
                    md=6
                )
            ], className='mb-4'),
            
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
                    'overflowX': 'scroll',
                    'borderRadius': '10px',
                    'margin': '20px auto',
                    'width': '100%',
                    'maxWidth': '98vw',  # Limite máximo
                    'minWidth': '100%',  # Força adaptação
},
                style_cell={
                    'textAlign': 'left',
                    'padding': '15px',
                    'fontFamily': 'Open Sans, sans-serif',
                    'backgroundColor': '#262626',
                    'color': 'white',
                    'border': '1px solid #333333',
                    'minWidth': '180px',
                    'whiteSpace': 'normal',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis'
                },
                style_header={
                    'backgroundColor': '#320c8a',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textTransform': 'uppercase',
                    'border': '1px solid #444444',
                    'fontSize': '14px',
                    'minWidth': '180px',
                    'position': 'sticky',
                    'top': 0
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
                    'rule': 'width: 100% !important; min-width: 100% !important;'
                }]
            )
        ], className='table-container animate__animated animate__fadeInUp')
    ], className='container-dados')
], className='main-container')

# Callback para filtros combinados
@callback(
    Output('full-data-table', 'data'),
    Input('search-input', 'value'),
    Input('representante-filter', 'value')
)
def update_table(search_text, selected_representantes):
    filtered_df = df.copy()
    
    # Aplicar filtro de texto
    if search_text:
        filtered_df = filtered_df[filtered_df['ESTABELECIMENTO NOME1'].str.contains(search_text, case=False, na=False)]
    
    # Aplicar filtro de representantes
    if selected_representantes and 'REPRESENTANTE NOME1' in filtered_df.columns:
        if 'ALL' not in selected_representantes:
            filtered_df = filtered_df[filtered_df['REPRESENTANTE NOME1'].isin(selected_representantes)]
    
    return filtered_df.to_dict('records')