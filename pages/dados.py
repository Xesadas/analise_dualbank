import dash
from dash import html, dcc, Input, Output, dash_table, callback, State, dash, clientside_callback, register_page
import pandas as pd
import dash_bootstrap_components as dbc
from flask import send_file

register_page(
    __name__,
    path='/dados',
    title='Dados Clientes',
    name='Dados dos clientes'
)

# Carregar o arquivo Excel completo
excel_file = 'stores.xlsx'
sheet_names = pd.ExcelFile(excel_file, engine='openpyxl').sheet_names

layout = html.Div([
    html.Div([
        html.Div([
            html.H1("📋 Dados Clientes", className="titulo-dados"),
            
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(
                        id='sheet-selector',
                        options=[{'label': sheet, 'value': sheet} for sheet in sheet_names],
                        value=sheet_names[0],
                        placeholder='📑 Selecione a aba...',
                        className='dropdown-sheets'
                    ),
                    md=4
                ),
                dbc.Col(
                    dcc.Input(
                        id='search-input',
                        placeholder='🔍 Digite o nome do cliente...',
                        type='text',
                        className='campo-pesquisa',
                        style={'width': '100%'}
                    ),
                    md=4
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id='representante-filter',
                        placeholder='👤 Filtrar por representante...',
                        multi=True,
                        className='dropdown-representantes',
                        clearable=True
                    ),
                    md=4
                )
            ], className='mb-4'),
            
            # Botão para salvar alterações
            html.Div([
                dbc.Button("💾 Salvar Alterações", 
                         id='save-button', 
                         color="primary",
                         className="me-1",
                         style={'margin': '10px'}),
                dcc.Download(id="download-excel")
            ], style={'textAlign': 'right'})
            
        ], className='container-header animate__animated animate__fadeInDown'),
        
        html.Div([
            dash_table.DataTable(
                id='full-data-table',
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
                    'maxWidth': '98vw',
                    'minWidth': '100%',
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
                },
                style_header={
                    'backgroundColor': '#320c8a',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'textTransform': 'uppercase',
                    'border': '1px solid #444444',
                    'fontSize': '14px',
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
                    }
                ],
                style_filter={
                    'backgroundColor': '#1a1a1a',
                    'color': 'white',
                    'border': '1px solid #333333'
                },
                editable=False
            )
        ], className='table-container animate__animated animate__fadeInUp'),
        
        dcc.Store(id='data-store'),
        html.Div(id='hidden-div', style={'display': 'none'}),
        dcc.Input(id='deleted-row-id', type='hidden')
    ], className='container-dados')
], className='main-container')

def load_excel():
    return pd.read_excel(excel_file, sheet_name=None, engine='openpyxl')

def save_excel(modified_data):
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        for sheet_name, df in modified_data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

@callback(
    Output('data-store', 'data'),
    Input('sheet-selector', 'value')
)
def update_data_store(selected_sheet):
    dfs = load_excel()
    df = dfs[selected_sheet].copy()
    df['id'] = df.index.astype(str)
    return df.to_dict('records')

@callback(
    Output('full-data-table', 'columns'),
    Output('full-data-table', 'data'),
    Output('representante-filter', 'options'),
    Input('data-store', 'data'),
    Input('search-input', 'value'),
    Input('representante-filter', 'value'),
)
def update_table(data, search_text, selected_representantes):
    df = pd.DataFrame(data)
    
    # Aplicar filtros
    if search_text:
        df = df[df['ESTABELECIMENTO NOME1'].str.contains(search_text, case=False, na=False)]
    
    if selected_representantes and 'REPRESENTANTE NOME1' in df.columns:
        df = df[df['REPRESENTANTE NOME1'].isin(selected_representantes)]
    
    # Gerar colunas
    columns = [{"name": col, "id": col} for col in df.columns if col != 'id']
    
    # Atualizar opções de representantes
    if 'REPRESENTANTE NOME1' in df.columns:
        reps = df['REPRESENTANTE NOME1'].dropna().unique()
        rep_options = [{'label': rep, 'value': rep} for rep in reps] + [{'label': 'Todos', 'value': 'ALL'}]
    else:
        rep_options = []
    
    return columns, df.to_dict('records'), rep_options

@callback(
    Output('download-excel', 'data'),
    Output('data-store', 'data', allow_duplicate=True),
    Input('save-button', 'n_clicks'),
    State('data-store', 'data'),
    State('sheet-selector', 'value'),
    prevent_initial_call=True
)
def save_changes(n_clicks, data, current_sheet):
    if n_clicks:
        # Carregar todas as abas
        all_sheets = load_excel()
        
        # Atualizar a aba atual com dados modificados
        updated_df = pd.DataFrame(data).drop(columns=['id'])
        all_sheets[current_sheet] = updated_df
        
        # Salvar no arquivo Excel
        save_excel(all_sheets)
        
        # Forçar recarregamento dos dados
        return dcc.send_file(excel_file), updated_df.to_dict('records')
    
    return dash.no_update, dash.no_update

@callback(
    Output('data-store', 'data', allow_duplicate=True),
    Input('deleted-row-id', 'value'),
    State('data-store', 'data'),
    State('sheet-selector', 'value'),
    prevent_initial_call=True
)
def delete_row(deleted_row_id, data, current_sheet):
    if deleted_row_id and data:
        df = pd.DataFrame(data)
        df = df[df['id'] != deleted_row_id].reset_index(drop=True)
        return df.to_dict('records')
    return dash.no_update

# Clienteside callback para detectar clicks nos botões
clientside_callback(
    """
    function(n_intervals) {
        setTimeout(function() {
            const deleteButtons = document.querySelectorAll('.delete-row-btn');
            
            deleteButtons.forEach(btn => {
                btn.onclick = function() {
                    const rowId = this.getAttribute('data-rowid');
                    if(confirm('Tem certeza que deseja excluir permanentemente este registro?')) {
                        document.getElementById('deleted-row-id').value = rowId;
                        document.getElementById('deleted-row-id').dispatchEvent(new Event('change'));
                    }
                }
            });
        }, 500);
        return '';
    }
    """,
    Output('hidden-div', 'children'),
    Input('hidden-div', 'n_intervals')
)