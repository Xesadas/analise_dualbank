import dash
from dash import html, dcc, Input, Output, dash_table, callback, State, register_page
import pandas as pd
import dash_bootstrap_components as dbc
import uuid
from pathlib import Path

register_page(
    __name__,
    path='/dados',
    title='Dados Clientes',
    name='Dados dos clientes'
)
excel_path = Path('stores.xlsx')

excel_file = 'stores.xlsx'
sheet_names = pd.ExcelFile(excel_file, engine='openpyxl').sheet_names

if excel_path.exists():
    dfs = pd.read_excel(excel_path, sheet_name=None, engine='openpyxl')
    
    for sheet in dfs:
        df = dfs[sheet]
        if 'temp_id' not in df.columns:
            df['temp_id'] = [str(uuid.uuid4()) for _ in range(len(df))]
    
    with pd.ExcelWriter(excel_path, engine='openpyxl', mode='w') as writer:
        for sheet_name, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)

def initialize_excel():
    if Path(excel_file).exists():
        dfs = pd.read_excel(excel_file, sheet_name=None, engine='openpyxl')
        for sheet in dfs:
            df = dfs[sheet]
            if 'temp_id' not in df.columns:
                df['temp_id'] = [str(uuid.uuid4()) for _ in range(len(df))]
            df['temp_id'] = df['temp_id'].astype(str)
        
        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
            for sheet_name, df in dfs.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

# Executa a inicialização uma vez
initialize_excel()

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
            
            html.Div([
                dbc.Button(
                    "🗑️ Apagar Linha Selecionada",
                    id='apagar-btn',
                    color="danger",
                    className="me-1",
                    style={'margin': '10px'}
                )
            ], style={'textAlign': 'right'})
            
        ], className='container-header animate__animated animate__fadeInDown'),
        
        html.Div([
            dash_table.DataTable(
                id='full-data-table',
                page_size=20,
                filter_action='native',
                sort_action='native',
                sort_mode='multi',
                row_selectable='single',
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
        html.Div(id='dados-output-mensagem', style={'color': 'white', 'padding': '10px'})  # Changed ID
    ], className='container-dados')
], className='main-container')

def load_excel():
    dfs = pd.read_excel(excel_file, sheet_name=None, engine='openpyxl')
    for sheet in dfs:
        df = dfs[sheet]
        df['temp_id'] = df['temp_id'].astype(str)  # Garante tipo string
    return dfs

def save_excel(modified_data):
    try:
        with pd.ExcelWriter(
            excel_file,
            engine='openpyxl',
            mode='w'  # Modo de sobrescrita completo
        ) as writer:
            for sheet_name in sheet_names:  # Usa a lista original de sheets
                df = modified_data.get(sheet_name, pd.DataFrame())
                if not df.empty:
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
        print("Arquivo salvo com sucesso!")
    except PermissionError:
        print("ERRO: Feche o Excel antes de salvar!")
        raise
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        raise

@callback(
    Output('data-store', 'data'),
    Input('sheet-selector', 'value')
)
def update_data_store(selected_sheet):
    dfs = load_excel()
    df = dfs[selected_sheet].reset_index(drop=True)
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
    
    if search_text:
        df = df[df['ESTABELECIMENTO NOME1'].str.contains(search_text, case=False, na=False)]
    
    if selected_representantes and 'REPRESENTANTE NOME1' in df.columns:
        df = df[df['REPRESENTANTE NOME1'].isin(selected_representantes)]
    
    columns = [{"name": col, "id": col} for col in df.columns if col != 'id']
    
    rep_options = []
    if 'REPRESENTANTE NOME1' in df.columns:
        reps = df['REPRESENTANTE NOME1'].dropna().unique()
        rep_options = [{'label': rep, 'value': rep} for rep in reps]
    
    return columns, df.to_dict('records'), rep_options

@callback(
    Output('dados-output-mensagem', 'children'),
    Output('data-store', 'data', allow_duplicate=True),
    Input('apagar-btn', 'n_clicks'),
    State('full-data-table', 'selected_rows'),
    State('data-store', 'data'),
    State('sheet-selector', 'value'),
    prevent_initial_call=True
)
def delete_row(n_clicks, selected_rows, data, current_sheet):
    if not selected_rows:
        return "🔴 Selecione uma linha antes de apagar!", dash.no_update
    
    try:
        # 1. Carrega dados completos do Excel
        dfs = load_excel()
        original_df = dfs[current_sheet].copy()
        
        # 2. Obtém os UUIDs selecionados DA VISÃO ATUAL (data-store)
        current_df = pd.DataFrame(data)
        selected_uuids = current_df.iloc[selected_rows]['temp_id'].tolist()
        
        # 3. Remove linhas do DataFrame ORIGINAL usando os UUIDs
        updated_df = original_df[~original_df['temp_id'].isin(selected_uuids)]
        
        # 4. Atualiza dados mantendo todas as abas
        new_data = {sheet: dfs[sheet] for sheet in sheet_names}
        new_data[current_sheet] = updated_df
        
        # 5. Salva o Excel com todas as abas
        save_excel(new_data)
        
        # 6. Atualiza o data-store com os dados atualizados
        return "✅ Linha(s) apagada(s) permanentemente!", updated_df.to_dict('records')
    
    except PermissionError:
        return "❌ Erro: Feche o Excel antes de salvar!", dash.no_update
    except Exception as e:
        return f"❌ Erro inesperado: {str(e)}", dash.no_update