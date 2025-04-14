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

# Layout inputs
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
        # Função para processar datas
        def processar_data(date_str):
            if not date_str:
                return None
            try:
                # Converter de string ISO (YYYY-MM-DD) para date
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except Exception as e:
                logging.error(f"Erro na conversão da data: {str(e)}")
                return None

        # Processar datas
        data_cadastro_dt = processar_data(data_cadastro)
        data_aprovacao_dt = processar_data(data_aprovacao)

        # Criar dicionário com novo registro
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

        # Carregar ou criar arquivo Excel
        if os.path.exists(file_path):
            df_existente = pd.read_excel(
                file_path,
                parse_dates=['DATA DE CADASTRO', 'DATA DE APROVAÇÃO'],
                engine='openpyxl'
            )
        else:
            df_existente = pd.DataFrame()

        # Criar DataFrame com novo registro
        df_novo = pd.DataFrame([novo_registro])
        df_final = pd.concat([df_existente, df_novo], ignore_index=True)

        # Salvar com formatação
        with pd.ExcelWriter(
            file_path,
            engine='openpyxl',
            mode='w'
        ) as writer:
            df_final.to_excel(writer, index=False, sheet_name='Sheet1')
            
            # Acessar objetos do openpyxl para formatação
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            
            # Estilização do cabeçalho
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
                cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
            
            # Formatar colunas de data
            date_format = 'DD/MM/YYYY'
            for col in ['A', 'B']:
                for cell in worksheet[col][1:]:  # Começa da segunda linha
                    cell.number_format = date_format
            
            # Ajustar largura das colunas
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