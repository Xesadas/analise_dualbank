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

logging.basicConfig(level=logging.DEBUG)

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

@callback(
    Output('cliente-transacao', 'options'),
    Input('clientes-store', 'data')
)
def carregar_clientes(_):
    file_path = 'stores.xlsx'
    try:
        if os.path.exists(file_path):
            df = pd.read_excel(file_path, 
                             sheet_name='Cadastros', 
                             usecols=['ESTABELECIMENTO CPF/CNPJ'])
            return [{'label': cnpj, 'value': cnpj} for cnpj in df['ESTABELECIMENTO CPF/CNPJ'].unique()]
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
        data_transacao = datetime.strptime(data_transacao, '%Y-%m-%d').strftime('%d/%m/%Y')
        valor = float(valor)
        
        nova_transacao = {
            'CPF/CNPJ': cliente,
            'DATA': data_transacao,
            'VALOR (R$)': valor,
            'STATUS': 'PROCESSADO'
        }
        
        sheets = []
        if os.path.exists(file_path):
            with pd.ExcelFile(file_path) as excel:
                sheets = excel.sheet_names
                
            if 'Transacoes' in sheets:
                df_transacoes = pd.read_excel(file_path, sheet_name='Transacoes')
            else:
                df_transacoes = pd.DataFrame()
        else:
            df_transacoes = pd.DataFrame()
        
        df_nova = pd.DataFrame([nova_transacao])
        df_final = pd.concat([df_transacoes, df_nova], ignore_index=True)
        
        with pd.ExcelWriter(
            file_path,
            engine='openpyxl',
            mode='a' if 'Cadastros' in sheets else 'w',
            if_sheet_exists='replace'
        ) as writer:
            if 'Cadastros' in sheets:
                df_cadastros = pd.read_excel(file_path, sheet_name='Cadastros')
                df_cadastros.to_excel(writer, index=False, sheet_name='Cadastros')
            
            df_final.to_excel(writer, index=False, sheet_name='Transacoes')
            
            workbook = writer.book
            if 'Transacoes' in workbook.sheetnames:
                ws = workbook['Transacoes']
                
                header_fill = PatternFill(start_color='2d5f8a', end_color='2d5f8a', fill_type='solid')
                header_font = Font(color='FFFFFF', bold=True)
                
                for cell in ws[1]:
                    cell.fill = header_fill
                    cell.font = header_font
                    cell.alignment = Alignment(horizontal='center')
                
                column_widths = {'A': 20, 'B': 15, 'C': 15, 'D': 15}
                for col, width in column_widths.items():
                    ws.column_dimensions[col].width = width
        
        return True, f"Transação de R${valor:.2f} registrada com sucesso! ✅", "success"
    
    except Exception as e:
        logging.error(f"Erro ao salvar transação: {str(e)}")
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
        def processar_data(date_str):
            if not date_str:
                return None
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except Exception as e:
                logging.error(f"Erro na conversão da data: {str(e)}")
                return None

        data_cadastro_dt = processar_data(data_cadastro)
        data_aprovacao_dt = processar_data(data_aprovacao)

        novo_registro = {
            'DATA DE CADASTRO': data_cadastro_dt,
            'DATA DE APROVAÇÃO': data_aprovacao_dt,
            'ESTABELECIMENTO NOME1': nome_estabelecimento or '',
            'ESTABELECIMENTO CPF/CNPJ': cpf_cnpj or '',
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

        sheets = []
        if os.path.exists(file_path):
            with pd.ExcelFile(file_path) as excel:
                sheets = excel.sheet_names
                
            if 'Cadastros' in sheets:
                df_existente = pd.read_excel(file_path, sheet_name='Cadastros')
            else:
                df_existente = pd.DataFrame()
        else:
            df_existente = pd.DataFrame()

        df_novo = pd.DataFrame([novo_registro])
        df_final = pd.concat([df_existente, df_novo], ignore_index=True)

        with pd.ExcelWriter(
            file_path,
            engine='openpyxl',
            mode='a' if sheets else 'w',
            if_sheet_exists='replace'
        ) as writer:
            if 'Transacoes' in sheets:
                df_transacoes = pd.read_excel(file_path, sheet_name='Transacoes')
                df_transacoes.to_excel(writer, index=False, sheet_name='Transacoes')
            
            df_final.to_excel(writer, index=False, sheet_name='Cadastros')
            
            workbook = writer.book
            worksheet = writer.sheets['Cadastros']
            
            header_fill = PatternFill(start_color='1a064d', end_color='1a064d', fill_type='solid')
            header_font = Font(color='FFFFFF', bold=True)
            header_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.border = header_border
                cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            
            date_format = 'DD/MM/YYYY'
            for col in ['A', 'B']:
                for cell in worksheet[col][1:]:
                    cell.number_format = date_format
            
            column_widths = {
                'A': 15, 'B': 15, 'C': 25, 'D': 20, 'E': 25,
                'F': 15, 'G': 20, 'H': 20, 'I': 12, 'J': 12,
                'K': 15, 'L': 20, 'M': 15, 'N': 15, 'O': 18,
                'P': 15, 'Q': 12, 'R': 20, 'S': 20, 'T': 20,
                'U': 20
            }
            
            for col, width in column_widths.items():
                worksheet.column_dimensions[col].width = width

        return True, "Cadastro salvo com sucesso! ✔️", "success"
    
    except Exception as e:
        logging.error(f"Erro crítico: {str(e)}\n{traceback.format_exc()}")
        return True, f"Erro ao salvar: {str(e)} ❌", "danger"