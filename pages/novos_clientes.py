import dash
from dash import html, dcc, Input, Output, State, register_page, callback
import dash_bootstrap_components as dbc
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from datetime import datetime, timezone
import os
import openpyxl
import logging
from openpyxl import Workbook
import re


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

logging.basicConfig(level=logging.DEBUG)
MOUNT_PATH = '/data' if os.environ.get('RENDER') else os.path.join(os.getcwd(), 'data')
EXCEL_PATH = os.path.join(MOUNT_PATH, 'stores.xlsx')

def setup_persistent_environment():
    try:
        os.makedirs(MOUNT_PATH, exist_ok=True)
        
        if not os.path.exists(EXCEL_PATH):
            wb = Workbook()
            wb.save(EXCEL_PATH)
        
        if not os.access(MOUNT_PATH, os.W_OK):
            logging.error(f"Sem permissão de escrita em: {MOUNT_PATH}")
            raise PermissionError("Erro de permissão no diretório persistente")

    except Exception as e:
        logging.error(f"Falha na configuração inicial: {str(e)}")
        raise

setup_persistent_environment()

# =====================================
# FUNÇÕES DE PROCESSAMENTO DE DADOS
# =====================================
def register_new_client(cpf_cnpj, frequencia):
    try:
        with pd.ExcelFile(EXCEL_PATH) as excel:
            analysis_df = pd.read_excel(excel, sheet_name='30_days_analysis', dtype={'cpf_cnpj': str})
            clientes_df = pd.read_excel(excel, sheet_name='Sheet1', dtype={'ESTABELECIMENTO CPF/CNPJ': str})

        cpf_cnpj = re.sub(r'\D', '', str(cpf_cnpj))
        client = clientes_df[
            clientes_df['ESTABELECIMENTO CPF/CNPJ'].astype(str).str.replace(r'\D', '', regex=True) == cpf_cnpj
        ].iloc[0]
        
        data_cadastro = pd.to_datetime(client['DATA DE CADASTRO']).date()
        
        novo_registro = {
            'cpf_cnpj': cpf_cnpj,
            'data_cadastro': data_cadastro,
            'transacoes': json.dumps({}),
            'frequencia': frequencia,
            'media_valores': 0.0
        }
        
        analysis_df = pd.concat([analysis_df, pd.DataFrame([novo_registro])], ignore_index=True)
        
        with pd.ExcelWriter(
            EXCEL_PATH,
            engine='openpyxl',
            mode='a',
            if_sheet_exists='replace'
        ) as writer:
            analysis_df.to_excel(writer, sheet_name='30_days_analysis', index=False)
            
            # Formatar coluna 'cpf_cnpj' como texto
            workbook = writer.book
            worksheet = workbook['30_days_analysis']
            for cell in worksheet['A']:
                cell.number_format = '@'
        
        return True
    except Exception as e:
        logging.error(f"Erro no registro: {str(e)}")
        return False

def register_transaction(cpf_cnpj, valor, frequencia):
    try:
        with pd.ExcelFile(EXCEL_PATH) as excel:
            analysis_df = pd.read_excel(excel, sheet_name='30_days_analysis', dtype={'cpf_cnpj': str})
            clientes_df = pd.read_excel(excel, sheet_name='Sheet1', dtype={'ESTABELECIMENTO CPF/CNPJ': str})
            transacoes_df = pd.read_excel(excel, sheet_name='Transacoes') if 'Transacoes' in excel.sheet_names else pd.DataFrame()

        cpf_cnpj = re.sub(r'\D', '', str(cpf_cnpj))  # Normalização
        clientes_df['ESTABELECIMENTO CPF/CNPJ'] = clientes_df['ESTABELECIMENTO CPF/CNPJ'].str.replace(r'\D', '', regex=True)
        
        cliente = clientes_df[clientes_df['ESTABELECIMENTO CPF/CNPJ'] == cpf_cnpj].iloc[0]
        today = datetime.now(timezone.utc).date()
        data_cadastro = pd.to_datetime(cliente['DATA DE CADASTRO']).date()

        if cpf_cnpj not in analysis_df['cpf_cnpj'].values:
            novo_registro = pd.DataFrame([{
                'cpf_cnpj': cpf_cnpj,
                'data_cadastro': data_cadastro,
                'transacoes': json.dumps({str(today): float(valor)}),
                'frequencia': frequencia,
                'media_valores': float(valor)
            }])
            analysis_df = pd.concat([analysis_df, novo_registro], ignore_index=True)
        else:
            row_index = analysis_df[analysis_df['cpf_cnpj'] == cpf_cnpj].index[0]
            transacoes = json.loads(analysis_df.at[row_index, 'transacoes'])
            transacoes[str(today)] = float(valor)
            
            media = sum(transacoes.values()) / len(transacoes) if transacoes else 0
            media = round(media, 2)
            
            analysis_df.at[row_index, 'transacoes'] = json.dumps(transacoes)
            analysis_df.at[row_index, 'media_valores'] = media

        nova_transacao = {
            'CPF/CNPJ': cpf_cnpj,
            'DATA': today.strftime('%d/%m/%Y'),
            'VALOR (R$)': float(valor),
            'STATUS': 'PROCESSADO'
        }

        transacoes_df = pd.concat([transacoes_df, pd.DataFrame([nova_transacao])])

        with pd.ExcelWriter(
            EXCEL_PATH,
            engine='openpyxl',
            mode='a',
            if_sheet_exists='replace'
        ) as writer:
            analysis_df.to_excel(writer, sheet_name='30_days_analysis', index=False)
            transacoes_df.to_excel(writer, sheet_name='Transacoes', index=False)
            clientes_df.to_excel(writer, sheet_name='Sheet1', index=False)

        return True, f"✅ Transação registrada para {cliente['ESTABELECIMENTO NOME1']}", media

    except Exception as e:
        logging.error(f"Erro detalhado: {str(e)}")
        return False, f"❌ Erro: {str(e)}", None

def load_analysis_data():
    try:
        df = pd.read_excel(
            EXCEL_PATH,
            sheet_name='30_days_analysis',
            dtype={'cpf_cnpj': str},
            parse_dates=['data_cadastro']
        )
        
        df['data_cadastro'] = pd.to_datetime(df['data_cadastro']).dt.tz_localize(None)
        today = pd.Timestamp.now().normalize()
        df['dias_cadastro'] = (today - df['data_cadastro']).dt.days
        df = df[df['dias_cadastro'] <= 30]
        return df
    except Exception as e:
        logging.error(f"Erro ao carregar dados: {str(e)}")
        return pd.DataFrame()

# =====================================
# LAYOUT (CORRIGIDO)
# =====================================
layout = html.Div(
    [
        dcc.Store(id='clientes-store', storage_type='memory'),
        html.Div(
            [
                html.Div(
                    [
                        html.H1("📈 Análise de Novos Clientes (30 Dias)", className="titulo-analise"),
                        
                        dbc.Row(
                            [
                                dbc.Col(
                                    dcc.Dropdown(
                                        id='cliente-select',
                                        placeholder='👤 Selecione o Cliente...',
                                        className='dropdown-clientes'
                                    ),
                                    md=6
                                ),
                                dbc.Col(
                                    dbc.Button(
                                        "➕ Registrar Novo Cliente",
                                        id='registrar-cliente-btn',
                                        color="success",
                                        className="me-1",
                                        disabled=True
                                    ),
                                    md=3
                                ),
                                dbc.Col(
                                    dbc.Button(
                                        "🗑️ Remover Cliente",
                                        id='remover-cliente-btn',
                                        color="danger",
                                        className="me-1",
                                        disabled=True
                                    ),
                                    md=3
                                )
                            ],
                            className='mb-4'
                        ),
                        
                        dbc.Row(
                            [
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
                            ],
                            className='mb-4'
                        ),
                        
                        dbc.Card(
                            [
                                dbc.CardHeader("Linha do Tempo de Transações", className='card-header'),
                                dbc.CardBody(
                                    dcc.Graph(
                                        id='grafico-transacoes',
                                        config={'displayModeBar': False},
                                        style={'height': '400px'}
                                    )
                                )
                            ],
                            className='mb-4',
                            color=COLORS['card'],
                            inverse=True
                        ),
                        
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Média de Valores", className='card-header'),
                                            dbc.CardBody(
                                                html.H4(id='media-valores', className='card-text')
                                            )
                                        ],
                                        color=COLORS['card'],
                                        inverse=True
                                    ),
                                    md=3
                                )
                            ]
                        ),
                        
                        html.Div(id='analise-output-mensagem', style={'color': COLORS['text'], 'padding': '10px'})
                        
                    ],
                    className='container-novos-clientes animate__animated animate__fadeIn'
                )
            ],
            className='main-container'
        )
    ],
    style={'backgroundColor': COLORS['background'], 'color': COLORS['text']}
)

# =====================================
# CALLBACKS (CORRIGIDOS)
# =====================================

@callback(
    Output('remover-cliente-btn', 'disabled'),
    Input('cliente-select', 'value')
)
def toggle_remove_button(selected_client):
    if not selected_client:
        return True
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name='30_days_analysis', dtype={'cpf_cnpj': str})
        df['cpf_cnpj'] = df['cpf_cnpj'].apply(lambda x: re.sub(r'\D', '', str(x)))
        return re.sub(r'\D', '', str(selected_client)) not in df['cpf_cnpj'].values
    except:
        return True

@callback(
    Output('analise-output-mensagem', 'children', allow_duplicate=True),
    Output('cliente-select', 'options', allow_duplicate=True),
    Input('remover-cliente-btn', 'n_clicks'),
    State('cliente-select', 'value'),
    prevent_initial_call=True
)
def handle_client_removal(n_clicks, cpf_cnpj):
    if n_clicks and cpf_cnpj:
        try:
            cpf_cnpj = re.sub(r'\D', '', str(cpf_cnpj))
            df = pd.read_excel(EXCEL_PATH, sheet_name='30_days_analysis', dtype={'cpf_cnpj': str})
            df['cpf_cnpj'] = df['cpf_cnpj'].apply(lambda x: re.sub(r'\D', '', str(x)))
            df = df[df['cpf_cnpj'] != cpf_cnpj]
            
            with pd.ExcelWriter(EXCEL_PATH, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name='30_days_analysis', index=False)
            
            clientes_df = pd.read_excel(EXCEL_PATH, sheet_name='Sheet1', dtype={'ESTABELECIMENTO CPF/CNPJ': str})
            clientes_df['ESTABELECIMENTO CPF/CNPJ'] = clientes_df['ESTABELECIMENTO CPF/CNPJ'].apply(lambda x: re.sub(r'\D', '', str(x)))
            
            options = []
            for _, row in clientes_df.iterrows():
                current_cpf = re.sub(r'\D', '', str(row['ESTABELECIMENTO CPF/CNPJ']))
                exists = current_cpf in df['cpf_cnpj'].values
                options.append({
                    'label': f"{row['ESTABELECIMENTO NOME1']} {'✅' if exists else '🆕'} - {current_cpf}",
                    'value': current_cpf
                })
            
            return (
                html.Div([
                    html.Span("✅ Cliente removido com sucesso!", style={'color': COLORS['success']}),
                    html.Br(),
                    html.Small("Atualização concluída", style={'color': COLORS['highlight']})
                ]),
                options
            )
        except Exception as e:
            logging.error(f"Erro na remoção: {str(e)}")
            return (
                html.Span(f"❌ Erro: {str(e)}", style={'color': COLORS['danger']}),
                dash.no_update
            )
    return PreventUpdate()

@callback(
    Output('cliente-select', 'options'),
    Input('clientes-store', 'data')
)
def update_dropdown(_):
    try:
        # Carrega e filtra dados
        clientes_df = pd.read_excel(
            EXCEL_PATH,
            sheet_name='Sheet1',
            usecols=['ESTABELECIMENTO NOME1', 'ESTABELECIMENTO CPF/CNPJ'],
            dtype={'ESTABELECIMENTO CPF/CNPJ': str}
        ).dropna(subset=['ESTABELECIMENTO CPF/CNPJ'])  # Remove linhas com CPF/CNPJ faltante

        analysis_df = pd.read_excel(
            EXCEL_PATH,
            sheet_name='30_days_analysis',
            dtype={'cpf_cnpj': str}
        ).dropna(subset=['cpf_cnpj'])  # Remove CPFs inválidos

        # Normalização rigorosa
        clientes_df['ESTABELECIMENTO CPF/CNPJ'] = (
            clientes_df['ESTABELECIMENTO CPF/CNPJ']
            .astype(str)
            .str.replace(r'\D', '', regex=True)
        )
        analysis_df['cpf_cnpj'] = (
            analysis_df['cpf_cnpj']
            .astype(str)
            .str.replace(r'\D', '', regex=True)
        )

        # Remove CPFs vazios ou inválidos
        clientes_df = clientes_df[
            clientes_df['ESTABELECIMENTO CPF/CNPJ'].str.strip().astype(bool)
        ]

        # Gera opções válidas
        options = []
        for _, row in clientes_df.iterrows():
            cpf = row['ESTABELECIMENTO CPF/CNPJ'].strip()
            if not cpf:  # Ignora CPFs vazios
                continue
                
            exists = cpf in analysis_df['cpf_cnpj'].values
            options.append({
                'label': f"{row['ESTABELECIMENTO NOME1']} {'✅' if exists else '🆕'} - {cpf}",
                'value': cpf
            })

        return options

    except Exception as e:
        logging.error(f"Erro no dropdown: {str(e)}")
        return []


@callback(
    Output('media-valores', 'children'),
    Output('frequencia-select', 'value'),
    Input('cliente-select', 'value'),
    prevent_initial_call=True
)
def update_metrics(selected_client):
    try:
        if not selected_client:
            raise PreventUpdate
        
        # Carrega dados da análise para frequência
        analysis_df = load_analysis_data()
        selected_client = re.sub(r'\D', '', str(selected_client))
        client_data = analysis_df[analysis_df['cpf_cnpj'] == selected_client]
        
        if client_data.empty:
            return "N/A", None
        
        # Busca transações reais na aba Transacoes
        transacoes_df = pd.read_excel(
            EXCEL_PATH,
            sheet_name='Transacoes',
            dtype={'CPF/CNPJ': str}
        )
        transacoes_df['CPF/CNPJ'] = transacoes_df['CPF/CNPJ'].str.replace(r'\D', '', regex=True)
        
        # Filtra e calcula média
        transacoes_cliente = transacoes_df[transacoes_df['CPF/CNPJ'] == selected_client]
        media = transacoes_cliente['VALOR (R$)'].mean()
        media = round(media, 2) if not transacoes_cliente.empty else 0.0
        
        return (
            f"R$ {media:.2f}",
            client_data.iloc[0]['frequencia']
        )
        
    except Exception as e:
        logging.error(f"Erro nas métricas: {str(e)}")
        return "Erro", None

@callback(
    Output('grafico-transacoes', 'figure'),
    Input('cliente-select', 'value'),
    prevent_initial_call=True
)
def update_transaction_chart(selected_client):
    try:
        if not selected_client:
            raise PreventUpdate
            
        transacoes_df = pd.read_excel(
            EXCEL_PATH, 
            sheet_name='Transacoes',
            dtype={'CPF/CNPJ': str}
        )
        selected_client = re.sub(r'\D', '', str(selected_client))
        transacoes_df['CPF/CNPJ'] = transacoes_df['CPF/CNPJ'].apply(lambda x: re.sub(r'\D', '', str(x)))
        filtered_df = transacoes_df[transacoes_df['CPF/CNPJ'] == selected_client].copy()
        
        filtered_df['DATA'] = pd.to_datetime(filtered_df['DATA'], dayfirst=True)
        grouped_df = filtered_df.groupby('DATA', as_index=False)['VALOR (R$)'].sum().sort_values('DATA')
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=grouped_df['DATA'],
            y=grouped_df['VALOR (R$)'],
            marker_color=COLORS['primary'],
            name='Transações'
        ))
        
        fig.update_layout(
            title='Histórico de Transações',
            xaxis_title='Data',
            yaxis_title='Valor (R$)',
            plot_bgcolor=COLORS['plot_bg'],
            paper_bgcolor=COLORS['card'],
            font=dict(color=COLORS['text']),
            margin=dict(l=40, r=40, t=60, b=40),
            xaxis=dict(type='category'),
            hovermode='x unified'
        )
        
        return fig
        
    except Exception as e:
        logging.error(f"Erro no gráfico: {str(e)}")
        return go.Figure()

@callback(
    Output('registrar-cliente-btn', 'disabled'),
    Input('cliente-select', 'value')
)
def toggle_register_button(selected_client):
    if not selected_client:
        return True
        
    try:
        analysis_df = load_analysis_data()
        selected_client = re.sub(r'\D', '', str(selected_client))
        return selected_client in analysis_df['cpf_cnpj'].values
    except:
        return True

@callback(
    Output('clientes-store', 'data', allow_duplicate=True),
    Output('analise-output-mensagem', 'children', allow_duplicate=True),
    Input('registrar-cliente-btn', 'n_clicks'),
    State('cliente-select', 'value'),
    State('frequencia-select', 'value'),  # Novo State
    prevent_initial_call=True
)
def handle_new_client_registration(n_clicks, cpf_cnpj, frequencia):
    if n_clicks and cpf_cnpj and frequencia:  # Verifica frequencia
        try:
            cpf_cnpj = re.sub(r'\D', '', str(cpf_cnpj))
            success = register_new_client(cpf_cnpj, frequencia)  # Passa frequencia
            if success:
                return (
                    {'timestamp': datetime.now().isoformat()},
                    html.Div([
                        html.Span("✅ Cliente registrado com sucesso!", style={'color': COLORS['success']}),
                        html.Br(),
                        html.Small("Frequência salva: " + frequencia, style={'color': COLORS['highlight']})
                    ])
                )
            return dash.no_update, html.Span("❌ Falha no registro", style={'color': COLORS['danger']})
        except Exception as e:
            return dash.no_update, html.Span(f"❌ Erro: {str(e)}", style={'color': COLORS['danger']})
    return dash.no_update, html.Span("Preencha todos os campos!", style={'color': COLORS['text']})