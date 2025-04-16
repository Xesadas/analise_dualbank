import dash
from dash import html, dcc, Input, Output, State, register_page, callback
import dash_bootstrap_components as dbc
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go

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

def register_new_client(cpf_cnpj):
    try:
        pass  # Placeholder for the code to execute
    except Exception as e:
        print(f"Erro: {str(e)}")
        with pd.ExcelFile(excel_path) as excel:
            analysis_df = pd.read_excel(excel, sheet_name='30_days_analysis', dtype={'cpf_cnpj': str})
            clientes_df = pd.read_excel(excel, sheet_name='Sheet1', dtype={'ESTABELECIMENTO CPF/CNPJ': str})

        cpf_cnpj = str(cpf_cnpj).strip()
        client = clientes_df[clientes_df['ESTABELECIMENTO CPF/CNPJ'] == cpf_cnpj].iloc[0]
        data_cadastro = pd.to_datetime(client['DATA DE CADASTRO']).date()
        
        novo_registro = {
            'cpf_cnpj': cpf_cnpj,
            'data_cadastro': data_cadastro,
            'transacoes': json.dumps({}),
            'frequencia': 'diaria',
            'media_valores': 0.0,
            'dias_restantes': 30
        }
        
        analysis_df = pd.concat([analysis_df, pd.DataFrame([novo_registro])])
        
        with pd.ExcelWriter(
            excel_path,
            engine='openpyxl',
            mode='a',
            if_sheet_exists='replace'
        ) as writer:
            analysis_df.to_excel(writer, sheet_name='30_days_analysis', index=False)
            
        return True
    except Exception as e:
        print(f"Erro: {str(e)}")
        return False

def register_transaction(cpf_cnpj, valor, frequencia):
    try:
        with pd.ExcelFile(excel_path) as excel:
            analysis_df = pd.read_excel(excel, sheet_name='30_days_analysis', dtype={'cpf_cnpj': str})
            clientes_df = pd.read_excel(excel, sheet_name='Sheet1', dtype={'ESTABELECIMENTO CPF/CNPJ': str})
            transacoes_df = pd.read_excel(excel, sheet_name='Transacoes') if 'Transacoes' in excel.sheet_names else pd.DataFrame()

        cpf_cnpj = str(cpf_cnpj).strip()
        clientes_df['ESTABELECIMENTO CPF/CNPJ'] = clientes_df['ESTABELECIMENTO CPF/CNPJ'].str.replace(r'\.0$', '', regex=True)
        
        cliente = clientes_df[clientes_df['ESTABELECIMENTO CPF/CNPJ'] == cpf_cnpj].iloc[0]
        today = datetime.now().date()
        data_cadastro = pd.to_datetime(cliente['DATA DE CADASTRO']).date()
        dias_restantes = 30 - (today - data_cadastro).days

        if cpf_cnpj not in analysis_df['cpf_cnpj'].values:
            novo_registro = {
                'cpf_cnpj': cpf_cnpj,
                'data_cadastro': data_cadastro,
                'transacoes': json.dumps({str(today): float(valor)}),
                'frequencia': frequencia,
                'media_valores': float(valor),
                'dias_restantes': dias_restantes
            }
            analysis_df = pd.concat([analysis_df, pd.DataFrame([novo_registro])])
        else:
            row_index = analysis_df[analysis_df['cpf_cnpj'] == cpf_cnpj].index[0]
            transacoes = json.loads(analysis_df.at[row_index, 'transacoes'])
            transacoes[str(today)] = float(valor)
            
            media = sum(transacoes.values()) / len(transacoes)
            
            analysis_df.at[row_index, 'transacoes'] = json.dumps(transacoes)
            analysis_df.at[row_index, 'media_valores'] = media
            analysis_df.at[row_index, 'dias_restantes'] = dias_restantes

            nova_transacao = {
            'CPF/CNPJ': str(cpf_cnpj).strip().replace('.0', ''),
            'DATA': today.strftime('%d/%m/%Y'),
            'VALOR (R$)': float(valor),
            'STATUS': 'PROCESSADO'
            }

        transacoes_df = pd.concat([transacoes_df, pd.DataFrame([nova_transacao])])

        with pd.ExcelWriter(
            excel_path,
            engine='openpyxl',
            mode='a',
            if_sheet_exists='replace'
        ) as writer:
            analysis_df.to_excel(writer, sheet_name='30_days_analysis', index=False)
            transacoes_df.to_excel(writer, sheet_name='Transacoes', index=False)
            clientes_df.to_excel(writer, sheet_name='Sheet1', index=False)

        return True, f"✅ Transação registrada para {cliente['ESTABELECIMENTO NOME1']}", media, dias_restantes

    except Exception as e:
        print(f"Erro detalhado: {str(e)}")
        return False, f"❌ Erro: {str(e)}", None, None

def load_analysis_data():
    required_columns = ['cpf_cnpj', 'data_cadastro', 'transacoes', 'frequencia', 'media_valores', 'dias_restantes']
    try:
        df = pd.read_excel(excel_path, sheet_name='30_days_analysis', engine='openpyxl')
        df['cpf_cnpj'] = df['cpf_cnpj'].astype(str).str.replace(r'\.0$', '', regex=True)
        if not all(col in df.columns for col in required_columns):
            raise ValueError("Invalid structure")
        return df
    except (FileNotFoundError, ValueError, KeyError):
        df = pd.DataFrame(columns=required_columns)
        with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name='30_days_analysis', index=False)
        return df
    except Exception as e:
        print(f"Unexpected error: {e}")
        df = pd.DataFrame(columns=required_columns)
        with pd.ExcelWriter(excel_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name='30_days_analysis', index=False)
        return df

def save_analysis_data(df):
    try:
        existing_sheets = pd.ExcelFile(excel_path).sheet_names
    except FileNotFoundError:
        existing_sheets = []

    with pd.ExcelWriter(
        excel_path,
        engine='openpyxl',
        mode='a' if '30_days_analysis' in existing_sheets else 'w',
        if_sheet_exists='replace'
    ) as writer:
        df.to_excel(writer, sheet_name='30_days_analysis', index=False)

# =====================================
# LAYOUT
# =====================================

layout = html.Div(
    [
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
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        [
                                            dbc.CardHeader("Dias Restantes", className='card-header'),
                                            dbc.CardBody(
                                                html.H4(id='dias-restantes', className='card-text')
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
# CALLBACKS
# =====================================

@callback(
    Output('cliente-select', 'options'),
    Input('cliente-select', 'search_value')
)
def update_dropdown(search_value):
    try:
        # Carregar dados da planilha
        clientes_df = pd.read_excel(
            excel_path,
            sheet_name='Sheet1',
            usecols=['ESTABELECIMENTO NOME1', 'ESTABELECIMENTO CPF/CNPJ'],
            dtype={'ESTABELECIMENTO CPF/CNPJ': str}
        ).dropna(subset=['ESTABELECIMENTO CPF/CNPJ'])
        
        # Limpar e formatar CPF/CNPJ
        clientes_df['ESTABELECIMENTO CPF/CNPJ'] = (
            clientes_df['ESTABELECIMENTO CPF/CNPJ']
            .str.strip()
            .str.replace(r'\D', '', regex=True))
        
        # Carregar análise existente
        analysis_df = load_analysis_data()
        analysis_df['cpf_cnpj'] = analysis_df['cpf_cnpj'].astype(str).str.replace(r'\.0$', '', regex=True)
        
        # Criar opções para dropdown
        options = []
        for _, row in clientes_df.iterrows():
            cpf_cnpj = str(row['ESTABELECIMENTO CPF/CNPJ'])
            exists = cpf_cnpj in analysis_df['cpf_cnpj'].values
            
            options.append({
                'label': f"{row['ESTABELECIMENTO NOME1']} {'✅' if exists else '🆕'} - {cpf_cnpj}",
                'value': cpf_cnpj
            })
            
        return options
        
    except Exception as e:
        print(f"Erro: {str(e)}")
        return []

@callback(
    Output('media-valores', 'children'),
    Output('dias-restantes', 'children'),
    Output('frequencia-select', 'value'),
    Input('cliente-select', 'value'),
    prevent_initial_call=True
)
def update_metrics(selected_client):
    try:
        if not selected_client:
            raise PreventUpdate
            
        analysis_df = load_analysis_data()
        client_data = analysis_df[analysis_df['cpf_cnpj'] == str(selected_client)].iloc[0]
        
        media = client_data['media_valores']
        dias = client_data['dias_restantes']
        frequencia = client_data['frequencia']
        
        return (
            f"R$ {media:.2f}",
            f"{dias} dias",
            frequencia
        )
    except:
        return dash.no_update, dash.no_update, dash.no_update
    
@callback(
    Output('grafico-transacoes', 'figure'),
    Input('cliente-select', 'value'),
    prevent_initial_call=True
)
def update_transaction_chart(selected_client):
    try:
        if not selected_client:
            raise PreventUpdate
            
        # Carregar dados da aba Transacoes
        transacoes_df = pd.read_excel(
            excel_path, 
            sheet_name='Transacoes',
            dtype={'CPF/CNPJ': str}
        ).copy()  # Evitar SettingWithCopyWarning
        
        # Filtrar transações do cliente selecionado
        filtered_df = transacoes_df[transacoes_df['CPF/CNPJ'] == str(selected_client)].copy()
        
        # Converter datas para datetime
        filtered_df['DATA'] = pd.to_datetime(filtered_df['DATA'], dayfirst=True)
        
        # Agrupar e somar valores por data
        grouped_df = (
            filtered_df.groupby('DATA', as_index=False)
            ['VALOR (R$)'].sum()
            .sort_values('DATA')
        )
        
        # Criar gráfico de barras
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=grouped_df['DATA'],
            y=grouped_df['VALOR (R$)'],
            marker_color=COLORS['primary'],
            name='Transações'
        ))
        
        # Configurações do layout
        fig.update_layout(
            title='Transações por Dia',
            xaxis_title='Data',
            yaxis_title='Valor (R$)',
            plot_bgcolor=COLORS['plot_bg'],
            paper_bgcolor=COLORS['card'],
            font=dict(color=COLORS['text']),
            margin=dict(l=40, r=40, t=60, b=40),
            xaxis=dict(type='category'),  # Forçar todas as datas no eixo X
            hovermode='x unified'
        )
        
        return fig
        
    except Exception as e:
        print(f"Erro no gráfico: {str(e)}")
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
        exists = selected_client in analysis_df['cpf_cnpj'].values
        return exists
    except:
        return True

@callback(
    Output('analise-output-mensagem', 'children', allow_duplicate=True),
    Input('registrar-cliente-btn', 'n_clicks'),
    State('cliente-select', 'value'),
    prevent_initial_call=True
)
def handle_new_client_registration(n_clicks, cpf_cnpj):
    if n_clicks and cpf_cnpj:
        success = register_new_client(cpf_cnpj)
        if success:
            return html.Div([
                html.Span("✅ Cliente registrado para análise de 30 dias!", style={'color': COLORS['success']}),
                html.Br(),
                html.Small("Agora você pode registrar transações", style={'color': COLORS['highlight']})
            ])
    return html.Span("❌ Erro ao registrar cliente", style={'color': COLORS['danger']})