import dash
from dash import dcc, html, Input, Output, State, callback, register_page
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
import openpyxl
from openpyxl import Workbook
import os
import traceback
import logging
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
import json
from pathlib import Path


logging.basicConfig(level=logging.DEBUG)
excel_path = Path('stores.xlsx')

#REFERENTE A ANÁLISE DE DADOS!!!
dash.register_page(
    __name__,
    path='/cadastro',
    title='Cadastro de Clientes',
    name='Cadastro'
)

# Estilos
transaction_style = {
    'border': '1px solid #e0e0e0',
    'borderRadius': '10px',
    'padding': '20px',
    'marginTop': '30px'
}
    
layout = dbc.Container([
    html.Div([
        html.Div([
            html.H2("Cadastro de Clientes", className="titulo-dados mb-4"),
            html.Span("Campos obrigatórios*", className="text-muted mb-4 d-block"),
        ], className="container-header text-center mb-5"),
        
        dbc.Card([
            dbc.CardBody([
                # Seção de Cadastro (original)
                html.Div([
                    html.H5("Datas", className="form-section-title"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Data de Cadastro", className="mb-2"),
                            dcc.DatePickerSingle(
                                id='data-cadastro',
                                date=datetime.today(),
                                first_day_of_week=0,
                                display_format='DD/MM/YYYY',
                                className='w-100'
                            )
                        ], md=6, className="mb-4"),
                        
                        dbc.Col([
                            dbc.Label("Data de Aprovação", className="mb-2"),
                            dcc.DatePickerSingle(
                                id='data-aprovacao',
                                first_day_of_week=0,
                                display_format='DD/MM/YYYY',
                                className='w-100'
                            )
                        ], md=6, className="mb-4")
                    ]),
                ]),
                
                html.Div([
                    html.H5("Informações do Estabelecimento", className="form-section-title"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Input(
                                id='nome-estabelecimento',
                                placeholder="Nome do Estabelecimento*",
                                className='mb-4'
                            )
                        ], md=12),
                        
                        dbc.Col([
                            dbc.Input(
                                id='cpf-cnpj',
                                placeholder="CPF/CNPJ*",
                                className='mb-4'
                            )
                        ], md=12)
                    ]),
                ]),
                
                html.Div([
                    html.H5("Responsável", className="form-section-title"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Input(
                                id='responsavel',
                                placeholder="Responsável do Estabelecimento*",
                                className='mb-4'
                            )
                        ], md=6),
                        
                        dbc.Col([
                            dbc.Input(
                                id='telefone',
                                placeholder="Telefone*",
                                type="tel",
                                className='mb-4'
                            )
                        ], md=6)
                    ]),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Input(
                                id='cpf-responsavel',
                                placeholder="CPF do Responsável*",
                                className='mb-4'
                            )
                        ], md=12)
                    ]),
                ]),
                
                html.Div([
                    html.H5("Representante", className="form-section-title"),
                    dbc.Input(
                        id='representante',
                        placeholder="Nome do Representante*",
                        type="text",
                        className='mb-4'
                    )
                ]),
                
                html.Div([
                    html.H5("Configurações", className="form-section-title"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Portal"),
                            dcc.Dropdown(
                                id='portal',
                                options=[
                                    {'label': 'Ativo', 'value': 'ATIVO'},
                                    {'label': 'Inativo', 'value': 'INATIVO'}
                                ],
                                className='mb-4'
                            )
                        ], md=4),
                        
                        dbc.Col([
                            dbc.Label("PagSeguro"),
                            dcc.Dropdown(
                                id='pagseguro',
                                options=[
                                    {'label': 'Habilitado', 'value': 'HABILITADO'},
                                    {'label': 'Desabilitado', 'value': 'DESABILITADO'}
                                ],
                                className='mb-4'
                            )
                        ], md=4),
                        
                        dbc.Col([
                            dbc.Label("Sub"),
                            dcc.Dropdown(
                                id='sub',
                                options=[
                                    {'label': 'Habilitado', 'value': 'HABILITADO'},
                                    {'label': 'Não Habilitado', 'value': 'NÃO HABILITADO'}
                                ],
                                className='mb-4'
                            )
                        ], md=4)
                    ]),
                    
                    dbc.Row([
                        dbc.Col([
                            dbc.Input(
                                id='pagseguro-email',
                                placeholder="Email PagSeguro",
                                type="email",
                                className='mb-4'
                            )
                        ], md=8),
                        
                        dbc.Col([
                            dbc.Label("Plano PagSeguro"),
                            dcc.Dropdown(
                                id='plano-pagseguro',
                                options=[
                                    {'label': 'NNB', 'value': 'NNB'},
                                    {'label': 'NNA', 'value': 'NNA'},
                                    {'label': 'NNC', 'value': 'NNC'},
                                    {'label': 'NND', 'value': 'NND'}
                                ],
                                className='mb-4'
                            )
                        ], md=4)
                    ]),
                ]),
                      
                dbc.Button(
                    "Salvar Cadastro", 
                    id='salvar-button', 
                    className='mt-4',
                    size="lg"
                )
            ])
        ], className="cadastro-container shadow-lg mb-5"),
        
        # Nova Seção de Transações
        dbc.Card([
            dbc.CardBody([
                html.H5("Registro de Transações Diárias", className="form-section-title"),
                
                dbc.Row([
                    dbc.Col([
                        dbc.Label("Selecionar Cliente"),
                        dcc.Dropdown(
                            id='cliente-transacao',
                            options=[],
                            placeholder="CPF/CNPJ do Cliente*",
                            className='mb-3'
                        )
                    ], md=6),
                    
                    dbc.Col([
                        dbc.Label("Data da Transação"),
                        dcc.DatePickerSingle(
                            id='data-transacao',
                            date=datetime.today(),
                            display_format='DD/MM/YYYY',
                            className='w-100 mb-3'
                        )
                    ], md=3),
                    
                    dbc.Col([
                        dbc.Label("Valor (R$)"),
                        dbc.Input(
                            id='valor-transacao',
                            type='number',
                            step=0.01,
                            placeholder="0.00",
                            className='mb-3'
                        )
                    ], md=3)
                ]),
                
                dbc.Button(
                    "Registrar Transação",
                    id='salvar-transacao',
                    color="secondary",
                    className='mt-2'
                )
            ])
        ], style=transaction_style, className="shadow-sm")
        
    ], className="py-5"),
    
    dcc.Store(id='clientes-store', storage_type='memory'),
    
    dbc.Alert(
        id='alert', 
        is_open=False, 
        duration=4000, 
        className="animate__animated animate__fadeInRight"
    ),
    
    dbc.Alert(
        id='alert-transacao', 
        is_open=False, 
        duration=4000,
        className="animate__animated animate__fadeInRight"
    )
], fluid=True)

# =============================================
# CALLBACKS
# =============================================

@callback(
    Output('cliente-transacao', 'options'),
    Input('clientes-store', 'data')
)
def carregar_clientes(_):
    file_path = 'stores.xlsx'
    try:
        if os.path.exists(file_path):
            df = pd.read_excel(
                file_path, 
                sheet_name='Sheet1', 
                usecols=['ESTABELECIMENTO CPF/CNPJ'], 
                dtype={'ESTABELECIMENTO CPF/CNPJ': str}
            )
            
            # Filtro aprimorado
            options = [
                {'label': cnpj, 'value': cnpj} 
                for cnpj in df['ESTABELECIMENTO CPF/CNPJ'].dropna().unique()
                if isinstance(cnpj, str) and cnpj.strip() != ''
            ]
            
            return options
        return []
    except Exception as e:
        logging.error(f"Erro ao carregar clientes: {str(e)}")
        return []

@callback(
    Output('alert-transacao', 'is_open'),
    Output('alert-transacao', 'children'),
    Output('alert-transacao', 'color'),
    Input('salvar-transacao', 'n_clicks'),
    [
        State('cliente-transacao', 'value'),
        State('data-transacao', 'date'),
        State('valor-transacao', 'value'),
    ],
    prevent_initial_call=True
)
def salvar_transacao(n_clicks, cliente, data_transacao, valor):
    file_path = 'stores.xlsx'
    
    if not all([cliente, data_transacao, valor]):
        return True, "Preencha todos os campos obrigatórios! ⚠️", "warning"
    
    try:
        from openpyxl import load_workbook

        # Processar dados
        data_transacao = datetime.strptime(data_transacao.split('T')[0], '%Y-%m-%d').strftime('%d/%m/%Y')
        valor = float(valor)

        # Carregar ou criar arquivo
        if os.path.exists(file_path):
            wb = load_workbook(file_path)
            if 'Transacoes' in wb.sheetnames:
                ws = wb['Transacoes']
            else:
                ws = wb.create_sheet('Transacoes')
                ws.append(['CPF/CNPJ', 'DATA', 'VALOR (R$)', 'STATUS'])
        else:
            wb = Workbook()
            ws = wb.active
            ws.title = 'Transacoes'
            ws.append(['CPF/CNPJ', 'DATA', 'VALOR (R$)', 'STATUS'])

        # Adicionar nova transação
        ws.append([cliente, data_transacao, valor, 'PROCESSADO'])

        # Garantir que a planilha principal existe
        if 'Sheet1' not in wb.sheetnames:
            wb.create_sheet('Sheet1')

        # Salvar alterações
        wb.save(file_path)

        return True, f"Transação de R${valor:.2f} registrada com sucesso! ✅", "success"
    
    except Exception as e:
        logging.error(f"Erro: {str(e)}\n{traceback.format_exc()}")
        return True, f"Erro: {str(e)} ❌", "danger"

@callback(
    Output('alert', 'is_open'),
    Output('alert', 'children'),
    Output('alert', 'color'),
    Input('salvar-button', 'n_clicks'),
    [
        State('data-cadastro', 'date'),
        State('data-aprovacao', 'date'),
        State('nome-estabelecimento', 'value'),
        State('cpf-cnpj', 'value'),
        State('responsavel', 'value'),
        State('telefone', 'value'),
        State('cpf-responsavel', 'value'),
        State('representante', 'value'),
        State('portal', 'value'),
        State('pagseguro', 'value'),
        State('sub', 'value'),
        State('pagseguro-email', 'value'),
        State('plano-pagseguro', 'value')
    ],
    prevent_initial_call=True
)
def salvar_cadastro(n_clicks, data_cadastro, data_aprovacao, nome_estabelecimento, 
                   cpf_cnpj, responsavel, telefone, cpf_responsavel, representante, 
                   portal, pagseguro, sub, pagseguro_email, plano_pagseguro):
    
    file_path = 'stores.xlsx'
    
    try:
        from openpyxl import load_workbook

        # Processar datas
        def processar_data(date_str):
            if not date_str:
                return None
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').strftime('%d/%m/%Y')
            except:
                return None

        data_cadastro = processar_data(data_cadastro)
        data_aprovacao = processar_data(data_aprovacao)

        # Criar dicionário com os dados
        novo_registro = {
            'DATA DE CADASTRO': data_cadastro,
            'DATA DE APROVAÇÃO': data_aprovacao,
            'ESTABELECIMENTO NOME1': nome_estabelecimento or '',
            'ESTABELECIMENTO CPF/CNPJ': str(cpf_cnpj).strip() if cpf_cnpj else '',
            'RESPONSÁVEL DO ESTABELECIMENTO': responsavel or '',
            'RESPONSÁVEL TELEFONE': telefone or '',
            'RESPONSÁVEL CPF/CNPJ': cpf_responsavel or '',
            'REPRESENTANTE NOME1': representante or '',
            'PORTAL': portal or 'INATIVO',
            'PAGSEGURO': pagseguro or 'DESABILITADO',
            'SUB': sub or 'NÃO HABILITADO',
            'PAGSEGURO EMAIL': pagseguro_email or '',
            'PLANO PAG': plano_pagseguro or '',
            'STATUS': 'PENDENTE',
            'BANKING': 'NÃO HABILITADO',
            'Média de Faturamento': 0.0,
            'Faturamento Dezembro': 0,
            'Faturamento Janeiro': 0,
            'Faturamento Fevereiro': 0
        }

        # Carregar ou criar arquivo
        if os.path.exists(file_path):
            wb = load_workbook(file_path)
            if 'Sheet1' in wb.sheetnames:
                ws = wb['Sheet1']
            else:
                ws = wb.create_sheet('Sheet1')
                # Adicionar cabeçalhos se nova planilha
                ws.append(list(novo_registro.keys()))
        else:
            wb = Workbook()
            ws = wb.active
            ws.title = 'Sheet1'
            ws.append(list(novo_registro.keys()))

        # Adicionar nova linha
        ws.append(list(novo_registro.values()))

        # Salvar alterações
        wb.save(file_path)

        return True, "Cadastro salvo com sucesso! ✔️", "success"
    
    except Exception as e:
        logging.error(f"Erro: {str(e)}\n{traceback.format_exc()}")
        return True, f"Erro ao salvar: {str(e)} ❌", "danger"