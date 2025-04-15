import dash
from dash import html, dcc, Input, Output, State, register_page, callback
import dash_bootstrap_components as dbc
import pandas as pd
import json
from datetime import datetime, timedelta
from pathlib import Path

register_page(
    __name__,
    path='/novos_clientes',
    title='Análise 30 Dias',
    name='Análise de Novos Clientes'
)

COLORS = {
    'background': '#000000',
    'text': '#ffffff',
    'primary': '#a991f7',
    'secondary': '#333333',  
    'success': '#2ecc71',
    'danger': '#e74c3c',
    'highlight': '#f1c40f',
    'card': '#1a1a1a',  
    'plot_bg': '#1a1a1a',
    'header': '#1a064d'
}

excel_path = Path('stores.xlsx')

def load_analysis_data():
    try:
        # Tenta carregar a aba
        df = pd.read_excel(excel_path, sheet_name='30_days_analysis', engine='openpyxl')
        
        # Verifica se as colunas necessárias existem
        required_columns = ['temp_id', 'data_cadastro', 'transacoes', 'frequencia', 'media_valores', 'dias_restantes']
        if not all(col in df.columns for col in required_columns):
            raise ValueError("Estrutura da planilha inválida")
            
        df['data_cadastro'] = pd.to_datetime(df['data_cadastro'])
        return df
        
    except (FileNotFoundError, ValueError, KeyError):
        # Cria um DataFrame vazio com a estrutura correta
        df = pd.DataFrame(columns=[
            'temp_id',
            'data_cadastro',
            'transacoes',
            'frequencia',
            'media_valores',
            'dias_restantes'
        ])
        
        # Salva a nova aba
        with pd.ExcelWriter(
            excel_path,
            engine='openpyxl',
            mode='a',
            if_sheet_exists='replace'
        ) as writer:
            df.to_excel(writer, sheet_name='30_days_analysis', index=False)
            
        return df

def save_analysis_data(df):
    # Carrega todas as abas existentes
    try:
        existing_sheets = pd.ExcelFile(excel_path).sheet_names
    except FileNotFoundError:
        existing_sheets = []

    # Mantém as outras abas intactas
    with pd.ExcelWriter(
        excel_path,
        engine='openpyxl',
        mode='a' if '30_days_analysis' in existing_sheets else 'w',
        if_sheet_exists='replace'
    ) as writer:
        df.to_excel(writer, sheet_name='30_days_analysis', index=False)

layout = html.Div([
    html.Div([
        html.Div([
            html.H1("📈 Análise de Novos Clientes (30 Dias)", className="titulo-analise"),
            
            dbc.Row([
                dbc.Col(
                    dcc.Dropdown(
                        id='cliente-select',
                        placeholder='👤 Selecione o Cliente...',
                        className='dropdown-clientes'
                    ),
                    md=6
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id='frequencia-select',
                        options=[
                            {'label': 'Diariamente', 'value': 'diaria'},
                            {'label': 'Às Vezes', 'value': 'as_vezes'},
                            {'label': 'Raramente', 'value': 'raramente'}
                        ],
                        placeholder='⏱️ Frequência de Transações...',
                        className='dropdown-frequencia'
                    ),
                    md=6
                )
            ], className='mb-4'),
            
            dbc.Row([
                dbc.Col(
                    dbc.Input(
                        id='valor-transacao',
                        type='number',
                        placeholder='💵 Valor da Transação...',
                        className='campo-transacao'
                    ),
                    md=4
                ),
                dbc.Col(
                    dbc.Button(
                        "➕ Registrar Transação",
                        id='registrar-btn',
                        color="primary",
                        className="me-1"
                    ),
                    md=4
                )
            ], className='mb-4'),
            
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Média de Valores", className='card-header'),
                        dbc.CardBody(
                            html.H4(id='media-valores', className='card-text')
                        )
                    ], color=COLORS['card'], inverse=True),
                    md=3
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Dias Restantes", className='card-header'),
                        dbc.CardBody(
                            html.H4(id='dias-restantes', className='card-text')
                        )
                    ], color=COLORS['card'], inverse=True),
                    md=3
                )
            ]),
            
            html.Div(id='analise-output-mensagem', style={'color': COLORS['text'], 'padding': '10px'})

        ], className='container-novos-clientes animate__animated animate__fadeIn')
    ], className='main-container')
], style={'backgroundColor': COLORS['background'], 'color': COLORS['text']})

@callback(
    Output('cliente-select', 'options'),
    Input('cliente-select', 'search_value')
)
def update_cliente_options(search_value):
    df = load_analysis_data()
    clientes = df.merge(
        pd.read_excel(excel_path, sheet_name='Sheet1'),
        on='temp_id'
    )[['temp_id', 'ESTABELECIMENTO NOME1']].dropna()
    
    return [
        {'label': row['ESTABELECIMENTO NOME1'], 'value': row['temp_id']}
        for _, row in clientes.iterrows()
    ]

@callback(
    Output('analise-output-mensagem', 'children'),
    Output('media-valores', 'children'),
    Output('dias-restantes', 'children'),
    Input('registrar-btn', 'n_clicks'),
    State('cliente-select', 'value'),
    State('valor-transacao', 'value'),
    State('frequencia-select', 'value'),
    prevent_initial_call=True
)
def registrar_transacao(n_clicks, temp_id, valor, frequencia):
    if not all([temp_id, valor, frequencia]):
        return "🔴 Preencha todos os campos!", dash.no_update, dash.no_update
    
    try:
        df = load_analysis_data()
        today = datetime.now().date()
        
        if temp_id not in df['temp_id'].values:
            novo_cliente = {
                'temp_id': temp_id,
                'data_cadastro': today,
                'transacoes': json.dumps({str(today): valor}),
                'frequencia': frequencia,
                'dias_restantes': 30
            }
            df = pd.concat([df, pd.DataFrame([novo_cliente])])
        else:
            row = df[df['temp_id'] == temp_id].iloc[0]
            transacoes = json.loads(row['transacoes'])
            transacoes[str(today)] = valor
            
            dias_passados = (today - row['data_cadastro'].date()).days
            dias_restantes = 30 - dias_passados
            
            df.loc[df['temp_id'] == temp_id, 'transacoes'] = json.dumps(transacoes)
            df.loc[df['temp_id'] == temp_id, 'frequencia'] = frequencia
            df.loc[df['temp_id'] == temp_id, 'dias_restantes'] = max(0, dias_restantes)
        
        # Calcular média
        transacoes = json.loads(df[df['temp_id'] == temp_id]['transacoes'].values[0])
        media = sum(transacoes.values()) / len(transacoes)
        
        save_analysis_data(df)
        
        return f"✅ Transação registrada para {temp_id}", f"R$ {media:.2f}", f"{dias_restantes} dias"

    except Exception as e:
        return f"❌ Erro: {str(e)}", dash.no_update, dash.no_update