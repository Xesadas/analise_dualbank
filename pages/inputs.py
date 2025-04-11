import dash
from dash import dcc, html, Input, Output, State, callback, register_page
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime

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
                
                dbc.Button("Salvar Cadastro", 
                         id='salvar-button', 
                         className='mt-4',
                         size="lg")
            ])
        ], className="cadastro-container shadow-lg")
    ], className="py-5"),
    
    dbc.Alert(id='alert', is_open=False, duration=4000, className="animate__animated animate__fadeInRight")
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
    try:
        # Ler o arquivo existente
        df = pd.read_excel('stores.xlsx', sheet_name='listagem-de-estabelecimentos')
        
        # Criar novo registro
        novo_registro = {
            'DATA DE CADASTRO': args[0],
            'DATA DE APROVAÇÃO': args[1],
            'ESTABELECIMENTO NOME1': args[2],
            'ESTABELECIMENTO CPF/CNPJ': args[3],
            'RESPONSÁVEL DO ESTABELECIMENTO': args[4],
            'RESPONSÁVEL TELEFONE': args[5],
            'RESPONSÁVEL CPF/CNPJ': args[6],
            'REPRESENTANTE NOME1': args[7],
            'PORTAL': args[8],
            'PAGSEGURO': args[9],
            'SUB': args[10],
            'PAGSEGURO EMAIL': args[11],
            'PLANO PAG': args[12]
        }
        
        # Adicionar novo registro ao DataFrame
        df = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
        
        # Salvar de volta no Excel
        df.to_excel('stores.xlsx', index=False)
        
        return True, "Cadastro salvo com sucesso!", "success"
    
    except Exception as e:
        return True, f"Erro ao salvar: {str(e)}", "danger"