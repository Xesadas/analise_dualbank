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

# Layout da página
layout = dbc.Container([
    html.Div([  # Adicionar um wrapper para o conteúdo
        html.Div([
            html.H2("Cadastro de Clientes", className="titulo-dados mb-4"),
            html.Span("Campos obrigatórios*", className="text-muted mb-4 d-block"),
        ], className="container-header text-center mb-5"),
        
        dbc.Card([
            dbc.CardBody([
                # Seção de Datas
                html.Div([
                    html.H5("Datas", className="form-section-title"),
                    dbc.Row([
                        dbc.Col([
                            dbc.Label("Data de Cadastro", className="mb-2"),
                            dcc.DatePickerSingle(
                                id='data-cadastro',
                                date=datetime.today(),
                                display_format='DD/MM/YYYY',
                                className='w-100'
                            )
                        ], md=6, className="mb-4"),
                        
                        dbc.Col([
                            dbc.Label("Data de Aprovação", className="mb-2"),
                            dcc.DatePickerSingle(
                                id='data-aprovacao',
                                display_format='DD/MM/YYYY',
                                className='w-100'
                            )
                        ], md=6, className="mb-4")
                    ]),
                ]),
                
                # Seção de Informações do Estabelecimento
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
                
                # Seção de Responsável
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
                
                # Seção de Configurações
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
        ], className="cadastro-container shadow-lg")
    ], className="py-5"),
    
    dbc.Alert(
        id='alert', 
        is_open=False, 
        duration=4000, 
        className="animate__animated animate__fadeInRight"
    )
], fluid=True)

@callback(
    Output('alert', 'is_open'),
    Output('alert', 'children'),
    Output('alert', 'color'),
    Input('salvar-button', 'n_clicks'),
    [State(field, 'value') for field in [
        'data-cadastro', 'data-aprovacao', 'nome-estabelecimento',
        'cpf-cnpj', 'responsavel', 'telefone', 'cpf-responsavel',
        'representante', 'portal', 'pagseguro', 'sub',
        'pagseguro-email', 'plano-pagseguro'
    ]],
    prevent_initial_call=True
)
def salvar_cadastro(n_clicks, *args):
    file_path = 'stores.xlsx'
    
    try:
        # 1. Verificação de dados de entrada
        logging.debug(f"Dados recebidos: {args}")
        
        # 2. Processamento de datas com fallbacks
        def processar_data(date_value):
            if not date_value:
                return None
            try:
                if isinstance(date_value, datetime):
                    return date_value.date()
                return datetime.fromisoformat(date_value).date()
            except Exception as e:
                logging.error(f"Erro conversão data: {str(e)}")
                return None

        data_cadastro = processar_data(args[0])
        data_aprovacao = processar_data(args[1])
        
        logging.debug(f"Datas convertidas - Cadastro: {data_cadastro} | Aprovação: {data_aprovacao}")

        # 3. Criar dicionário com tipos explícitos
        novo_registro = {
            'DATA DE CADASTRO': data_cadastro,
            'DATA DE APROVAÇÃO': data_aprovacao,
            'ESTABELECIMENTO NOME1': str(args[2]) if args[2] else None,
            'ESTABELECIMENTO CPF/CNPJ': str(args[3]) if args[3] else None,
            'RESPONSÁVEL DO ESTABELECIMENTO': str(args[4]) if args[4] else None,
            'RESPONSÁVEL TELEFONE': str(args[5]) if args[5] else None,
            'RESPONSÁVEL CPF/CNPJ': str(args[6]) if args[6] else None,
            'REPRESENTANTE NOME1': str(args[7]) if args[7] else None,
            'PORTAL': args[8],
            'PAGSEGURO': args[9],
            'SUB': args[10],
            'PAGSEGURO EMAIL': str(args[11]) if args[11] else None,
            'PLANO PAG': args[12],
            'STATUS': 'PENDENTE',
            'BANKING': 'NÃO HABILITADO',
            'Média de Faturamento': 0.0
        }

        # 4. Criar DataFrame com tipos explícitos
        dtypes = {
            'DATA DE CADASTRO': 'datetime64[ns]',
            'DATA DE APROVAÇÃO': 'datetime64[ns]',
            'ESTABELECIMENTO NOME1': 'object',
            'ESTABELECIMENTO CPF/CNPJ': 'object',
            'RESPONSÁVEL DO ESTABELECIMENTO': 'object',
            'RESPONSÁVEL TELEFONE': 'object',
            'RESPONSÁVEL CPF/CNPJ': 'object',
            'REPRESENTANTE NOME1': 'object',
            'PORTAL': 'category',
            'PAGSEGURO': 'category',
            'SUB': 'category',
            'PAGSEGURO EMAIL': 'object',
            'PLANO PAG': 'category',
            'STATUS': 'category',
            'BANKING': 'category',
            'Média de Faturamento': 'float64'
        }

        # 5. Carregar ou criar novo arquivo
        if os.path.exists(file_path):
            try:
                df_existente = pd.read_excel(
                    file_path,
                    dtype=dtypes,
                    parse_dates=['DATA DE CADASTRO', 'DATA DE APROVAÇÃO'],
                    engine='openpyxl'
                )
                df_existente = df_existente.astype(dtypes)
            except Exception as e:
                logging.error(f"Erro ao carregar arquivo: {str(e)}")
                return True, "Erro ao ler arquivo existente", "danger"
        else:
            df_existente = pd.DataFrame(columns=dtypes.keys()).astype(dtypes)

        # 6. Adicionar novo registro
        df_novo = pd.DataFrame([novo_registro]).astype(dtypes)
        df_final = pd.concat([df_existente, df_novo], ignore_index=True)

        # 7. Salvar e formatar o arquivo
        with pd.ExcelWriter(
            file_path,
            engine='openpyxl',
            mode='a' if os.path.exists(file_path) else 'w',
            if_sheet_exists='overlay'
        ) as writer:
            # Salvar dados
            df_final.to_excel(writer, index=False, sheet_name='Sheet1')
            
            # Acessar objetos do openpyxl
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            
            # Estilização
            header_fill = PatternFill(start_color='1a064d', end_color='1a064d', fill_type='solid')
            header_font = Font(color='FFFFFF', bold=True)
            header_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            # Aplicar estilo ao cabeçalho
            for cell in worksheet[1]:  # Linha 1 é o cabeçalho
                cell.fill = header_fill
                cell.font = header_font
                cell.border = header_border
                cell.alignment = Alignment(wrap_text=True)
            
            # Ajustar largura das colunas
            worksheet.column_dimensions['A'].width = 15
            worksheet.column_dimensions['B'].width = 15
            for col in ['C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']:
                worksheet.column_dimensions[col].width = 20

            # Remover linha vazia do pandas
            worksheet.delete_rows(1)

        logging.debug("Arquivo salvo com sucesso!")
        return True, "Dados salvos com sucesso!", "success"

    except Exception as e:
        logging.error(f"Erro completo: {traceback.format_exc()}")
        return True, f"Erro crítico: {str(e)}", "danger"