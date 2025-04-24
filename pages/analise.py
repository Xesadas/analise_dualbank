import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output, dash_table, callback, register_page
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

register_page(
    __name__,
    path='/',
    name='Analise clientes',
    title='Analise de clientes'
)

# =====================================
# CARREGAMENTO DE DADOS
# =====================================
try:
    df_cadastros = pd.read_excel('stores.xlsx', sheet_name='Sheet1', engine='openpyxl')
    df_transacoes = pd.read_excel('stores.xlsx', sheet_name='Transacoes', engine='openpyxl')
    df_transacoes['DATA'] = pd.to_datetime(df_transacoes['DATA'], dayfirst=True)
    
    df = pd.merge(df_transacoes, 
                df_cadastros[['ESTABELECIMENTO CPF/CNPJ', 'ESTABELECIMENTO NOME1']],
                left_on='CPF/CNPJ',
                right_on='ESTABELECIMENTO CPF/CNPJ',
                how='left')

except Exception as e:
    print(f"Erro ao carregar dados: {str(e)}")
    df_cadastros = pd.DataFrame()
    df_transacoes = pd.DataFrame()
    df = pd.DataFrame()

# =====================================
# PREPARAÇÃO DOS DADOS MENSAL
# =====================================
meses = {
    'Faturamento Dezembro': 'Dezembro',
    'Faturamento Janeiro': 'Janeiro',
    'Faturamento Fevereiro': 'Fevereiro',
    'Faturamento Marco': 'Março',
    'Faturamento Abril': 'Abril',
    'Faturamento Maio': 'Maio',
    'Faturamento Junho': 'Junho',
    'Faturamento Julho': 'Julho',
    'Faturamento Agosto': 'Agosto',
    'Faturamento Setembro': 'Setembro',
    'Faturamento Outubro': 'Outubro',
    'Faturamento Novembro': 'Novembro',
    'Faturamento Dezembro.1': 'Dezembro Atual'
}

meses_ordem = [
    'Dezembro', 'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio',
    'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro Atual'
]

proximo_mes_map = {
    'Dezembro': 'Janeiro',
    'Janeiro': 'Fevereiro',
    'Fevereiro': 'Março',
    'Março': 'Abril',
    'Abril': 'Maio',
    'Maio': 'Junho',
    'Junho': 'Julho',
    'Julho': 'Agosto',
    'Agosto': 'Setembro',
    'Setembro': 'Outubro',
    'Outubro': 'Novembro',
    'Novembro': 'Dezembro Atual',
    'Dezembro Atual': 'Janeiro'
}

if not df_cadastros.empty:
    df_long = df_cadastros.melt(
        id_vars=['ESTABELECIMENTO NOME1', 'STATUS'],
        value_vars=meses.keys(),
        var_name='Mês',
        value_name='Faturamento'
    )
    df_long['Mês'] = df_long['Mês'].map(meses)
    df_long['Mês'] = pd.Categorical(df_long['Mês'], categories=meses_ordem, ordered=True)
else:
    df_long = pd.DataFrame()


# =====================================
# FUNÇÕES AUXILIARES
# =====================================
def get_proximo_mes(mes_atual):
    return proximo_mes_map.get(mes_atual, 'Janeiro')

def calcular_previsao(cliente_data):
    """Calcula a média dos meses VÁLIDOS (não zero/não vazios)"""
    valores = cliente_data['Faturamento'].replace(0, np.nan).dropna()
    return np.mean(valores) if not valores.empty else 0



# =====================================
# PREPARAÇÃO DOS DADOS DIÁRIOS 
# =====================================
def prepare_daily_data():
    if not df.empty:
        daily_df = df.groupby(['ESTABELECIMENTO NOME1', pd.Grouper(key='DATA', freq='D')]).agg({
            'VALOR (R$)': 'sum',
            'CPF/CNPJ': 'count'
        }).rename(columns={
            'VALOR (R$)': 'Faturamento Diário',
            'CPF/CNPJ': 'Transações'
        }).reset_index()
        return daily_df
    return pd.DataFrame()

daily_data = prepare_daily_data() 

# =====================================
# PALETA DE CORES & ESTILOS 
# =====================================
COLORS = {
    'background': '#000000',
    'text': '#ffffff',
    'primary': '#a991f7',
    'secondary': '#333333',  
    'success': '#2ecc71',
    'danger': '#e74c3c',
    'highlight':'#161691',
    'card': '#1a1a1a',  
    'plot_bg': '#1a1a1a',
    'header': '#1a064d'
}

FONT_STYLE = {
    'family': 'Open Sans, sans-serif',
    'size': 14,
    'color': COLORS['text']
}

options = [{'label': str(nome), 'value': str(nome)} 
           for nome in df_cadastros['ESTABELECIMENTO NOME1'].unique() 
           if pd.notna(nome) and str(nome).strip() != '']

if not options:
    options = [{'label': 'Sem dados disponíveis', 'value': 'NO_DATA'}]


#=====================================
# PRÉ CARREGAMENTO DE DADOS 
#=====================================

cached_data = {
    'df_cadastros': pd.DataFrame(),
    'df_transacoes': pd.DataFrame(),
    'df': pd.DataFrame(),
    'df_long': pd.DataFrame(),
    'daily_data': pd.DataFrame(),
    'weekly_data': pd.DataFrame(),
    'last_modified': None
}

def load_data():
    global cached_data
    file_path = 'stores.xlsx'
    
    try:
        current_modified = os.path.getmtime(file_path)
        
        if cached_data['last_modified'] != current_modified:
            # Carrega dados
            df_cadastros = pd.read_excel(file_path, sheet_name='Sheet1', engine='openpyxl')
            df_transacoes = pd.read_excel(file_path, sheet_name='Transacoes', engine='openpyxl')
            df_transacoes['DATA'] = pd.to_datetime(df_transacoes['DATA'], dayfirst=True)
            
            df = pd.merge(
                df_transacoes, 
                df_cadastros[['ESTABELECIMENTO CPF/CNPJ', 'ESTABELECIMENTO NOME1']],
                left_on='CPF/CNPJ',
                right_on='ESTABELECIMENTO CPF/CNPJ',
                how='left'
            )
            
            # Prepara df_long CORREÇÃO AQUI
            df_long = df_cadastros.melt(
                id_vars=['ESTABELECIMENTO NOME1', 'STATUS'],
                value_vars=meses.keys(),  # Usa todas as colunas de meses
                var_name='Mês',
                value_name='Faturamento'
            ) if not df_cadastros.empty else pd.DataFrame()
            
            df_long['Mês'] = df_long['Mês'].map(meses)
            df_long['Mês'] = pd.Categorical(
                df_long['Mês'], 
                categories=meses_ordem,  # Usa a lista completa de meses
                ordered=True
            )
            
            # Prepara dados diários
            daily_data = df.groupby(['ESTABELECIMENTO NOME1', pd.Grouper(key='DATA', freq='D')]).agg({
                'VALOR (R$)': 'sum',
                'CPF/CNPJ': 'count'
            }).rename(columns={
                'VALOR (R$)': 'Faturamento Diário',
                'CPF/CNPJ': 'Transações'
            }).reset_index() if not df.empty else pd.DataFrame()

            weekly_dfs = []
            xls = pd.ExcelFile(file_path)
            for sheet_name in xls.sheet_names:
                if sheet_name.startswith('Faturamento '):
                    df_sheet = pd.read_excel(xls, sheet_name=sheet_name)
                    df_sheet['MÊS'] = sheet_name.replace('Faturamento ', '')
                    weekly_dfs.append(df_sheet)
            
            df_semanas = pd.concat(weekly_dfs, ignore_index=True) if weekly_dfs else pd.DataFrame()

            if not df_semanas.empty:
                df_semanas['DATA REGISTRO'] = pd.to_datetime(
                    df_semanas['DATA REGISTRO'], 
                    dayfirst=True,  # Adicionei dayfirst aqui
                    format='%d/%m/%Y %H:%M'  # Especificar formato explícito
                )
            
            # Atualiza cache
            cached_data.update({
                'df_cadastros': df_cadastros,
                'df_transacoes': df_transacoes,
                'df': df,
                'df_long': df_long,
                'daily_data': daily_data,
                'last_modified': current_modified,
                'weekly_data': df_semanas
            })
            
    except Exception as e:
        print(f"Erro ao carregar dados: {str(e)}")
    
    return cached_data

def determinar_meses_relevantes(df):
    # Encontrar o último mês com dados
    meses_disponiveis = df['Mês'].unique()
    meses_validos = [m for m in meses_ordem if m in meses_disponiveis]
    
    if not meses_validos:
        return [], None, None
    
    ultimo_mes = meses_validos[-1]
    idx_ultimo = meses_ordem.index(ultimo_mes)
    
    # Determinar meses para mostrar (últimos 3 + previsão)
    start_idx = max(0, idx_ultimo - 2)
    meses_mostrar = meses_ordem[start_idx:idx_ultimo+1]
    
    # Calcular próximo mês para previsão
    if idx_ultimo < len(meses_ordem) - 1:
        proximo_mes = meses_ordem[idx_ultimo + 1]
    else:  # Se for dezembro, prever janeiro
        proximo_mes = meses_ordem[0]
    
    return meses_mostrar, ultimo_mes, proximo_mes

    

# =====================================
# LAYOUT COMPLETO
# =====================================
layout = html.Div(style={'backgroundColor': COLORS['background'], 'minHeight': '100vh'}, children=[
    html.Div(className='container', style={'padding': '30px', 'maxWidth': '1200px', 'margin': '0 auto'}, children=[
        
        # Título
        html.Div(className='header', style={'textAlign': 'center', 'marginBottom': '40px'}, children=[
            dcc.Interval(
                id='interval-component',
                interval=1*1000,  # Atualiza a cada segundo 
                n_intervals=0,
                disabled=True  # Desativado por padrão
            ),
            html.H1("📈 Análise de Faturamento", 
                   style={'color': COLORS['primary'], 
                          'fontSize': '2.5em',
                          'textShadow': '2px 2px 4px rgba(0,0,0,0.1)'}),
            html.P("Análise de faturamento de clientes DualBank", 
                  style={'color': COLORS['secondary'], 'fontSize': '1.1em'})
        ]),
        
        # Controles
        html.Div(className='control-card', style={
            'backgroundColor': COLORS['card'],
            'padding': '25px',
            'borderRadius': '15px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
            'marginBottom': '30px'
        }, children=[
            dcc.Dropdown(
                id='cliente-dropdown',
                options=options,
                multi=True,
                placeholder="🔍 Selecione o cliente desejado...",
                style={
                    'width': '100%',
                    'borderRadius': '8px',
                    'border': f'1px solid {COLORS["primary"]}',
                    'backgroundColor': COLORS['card'],
                    'color': COLORS['text']
                }
            ),
            dcc.DatePickerRange(
                id='date-range',
                start_date=datetime.today() - timedelta(days=30),
                end_date=datetime.today(),
                display_format='DD/MM/YYYY',
                style={'marginTop': '15px'}
            )
        ]),
        
        html.Div(className='graph-container', children=[
            html.Div(className='graph-card', style={
                'backgroundColor': COLORS['card'],
                'padding': '20px',
                'borderRadius': '15px',
                'marginBottom': '20px'
            }, children=[
                dcc.Graph(
                    id='grafico-mensal',
                    style={'height': '400px'},
                    config={'displayModeBar': False}
                )
            ]),
        html.Div(className='graph-card', style={
            'backgroundColor': COLORS['card'],
            'padding': '20px',
            'borderRadius': '15px',
            'marginBottom': '20px'
        }, children=[
            dcc.Graph(
                id='grafico-semanal',
                style={'height': '400px'},
                config={'displayModeBar': False}
            )
        ]),
            ]),
            
            html.Div(className='graph-card', style={
                'backgroundColor': COLORS['card'],
                'padding': '20px',
                'borderRadius': '15px'
            }, children=[
                dcc.Graph(
                    id='grafico-diario',
                    style={'height': '400px'},
                    config={'displayModeBar': False}
                )
            ])
        ]),
        
        # Tabela
        html.Div(className='table-card', style={
            'marginTop': '30px',
            'backgroundColor': COLORS['card'],
            'borderRadius': '15px',
            'overflow': 'hidden',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
        }, children=[
            dash_table.DataTable(
                id='tabela-variacao',
                style_table={'overflowX': 'auto'},
                style_cell={
                    'textAlign': 'center',
                    'padding': '12px',
                    'fontFamily': FONT_STYLE['family'],
                    'border': f'1px solid {COLORS["background"]}',
                    'color': COLORS['text'],
                    'backgroundColor': COLORS['card']
                },
                style_header={
                    'backgroundColor': COLORS['primary'],
                    'color': 'white',
                    'fontWeight': 'bold',
                    'borderRadius': '0',
                    'textTransform': 'uppercase'
                },
                style_data_conditional=[
                    {
                        'if': {'column_id': 'Variação %', 'filter_query': '{Variação %} > 0'},
                        'color': COLORS['success'],
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {'column_id': 'Variação %', 'filter_query': '{Variação %} < 0'},
                        'color': COLORS['danger'],
                        'fontWeight': 'bold'
                    },
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#333333'
                    }
                ]
            )
        ])
    ])
#])

#=====================================
# CALLBACKS 
#=====================================

@callback(
    Output('grafico-mensal', 'figure'),
    Output('grafico-diario', 'figure'),
    Output('grafico-semanal', 'figure'), 
    Output('tabela-variacao', 'data'),
    Output('tabela-variacao', 'columns'),
    Input('cliente-dropdown', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date'),
    Input('interval-component', 'n_intervals') 
)
def update_analysis(clientes_selecionados, start_date, end_date, n):
    fig_mensal = go.Figure()
    fig_diario = go.Figure()
    fig_semanal = go.Figure()
    table_data = []
    columns = []

    if not clientes_selecionados or 'NO_DATA' in clientes_selecionados:
        return fig_mensal, fig_diario,fig_semanal, [], []

    try:
        load_data()
        
        # =====================================
        # LÓGICA DE MESES
        # =====================================
        if not cached_data['df_long'].empty:
            filtered_mensal = cached_data['df_long'].copy()
            filtered_mensal = filtered_mensal[filtered_mensal['ESTABELECIMENTO NOME1'].isin(clientes_selecionados)]
            
            # Converter para numérico
            filtered_mensal['Faturamento'] = pd.to_numeric(
                filtered_mensal['Faturamento'], 
                errors='coerce'
            ).fillna(0)

            previsoes = []
            cores = px.colors.qualitative.Plotly
            
            for idx, cliente in enumerate(clientes_selecionados):
                cliente_data = filtered_mensal[filtered_mensal['ESTABELECIMENTO NOME1'] == cliente]
                
                if cliente_data.empty:
                    continue
                
                # CORREÇÃO 1: Ordenar corretamente por categoria temporal
                cliente_data = cliente_data.sort_values('Mês', key=lambda x: x.cat.codes)
                
                # CORREÇÃO 2: Pegar último mês COM DADOS VÁLIDOS (>0)
                cliente_data_valida = cliente_data[cliente_data['Faturamento'] > 0]
                if cliente_data_valida.empty:
                    continue
                    
                ultimo_mes = cliente_data_valida['Mês'].iloc[-1]
                
                # CORREÇÃO 3: Nova lógica de próximo mês
                try:
                    idx_proximo = meses_ordem.index(ultimo_mes) + 1
                    if idx_proximo >= len(meses_ordem):
                        proximo_mes = meses_ordem[0]  # Volta para Janeiro
                    else:
                        proximo_mes = meses_ordem[idx_proximo]
                except ValueError:
                    proximo_mes = 'Janeiro'

                # Calcular variação
                cliente_data['Faturamento Anterior'] = cliente_data['Faturamento'].shift(1)
                cliente_data['Variação %'] = (cliente_data['Faturamento'] / cliente_data['Faturamento Anterior'].replace(0, np.nan) - 1) * 100
                
                # Calcular previsão
                valores_validos = cliente_data_valida['Faturamento']
                previsao = np.mean(valores_validos) if not valores_validos.empty else 0
                
                # Adicionar previsão
                previsoes.append({
                    'ESTABELECIMENTO NOME1': cliente,
                    'Mês': proximo_mes,
                    'Faturamento': previsao,
                    'Variação %': None,
                    'Previsão': True
                })

                meses_ativos = cliente_data_valida['Mês'].tolist() + [proximo_mes]
                dados_plot = cliente_data[cliente_data['Mês'].isin(meses_ativos)]

                fig_mensal.add_trace(go.Scatter(
                    x=dados_plot['Mês'],
                    y=dados_plot['Faturamento'],
                    name=cliente,
                    mode='lines+markers',
                    line=dict(width=3, color=cores[idx]),
                    marker=dict(size=10, color=cores[idx]),
                    hovertemplate='<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>'
                ))

                # Plotar previsão
                if proximo_mes in meses_ordem:
                    fig_mensal.add_trace(go.Scatter(
                        x=[ultimo_mes, proximo_mes],
                        y=[cliente_data_valida['Faturamento'].iloc[-1], previsao],
                        mode='lines+markers',
                        line=dict(dash='dot', color=cores[idx]),
                        marker=dict(symbol='diamond', size=12),
                        showlegend=False
                    ))

                    # Adicionar anotações de variação
                    for _, row in cliente_data.iterrows():
                        if pd.notna(row['Variação %']):
                            symbol = '▲' if row['Variação %'] > 0 else '▼'
                            color = COLORS['success'] if row['Variação %'] > 0 else COLORS['danger']
                            fig_mensal.add_annotation(
                                x=row['Mês'],
                                y=row['Faturamento'],
                                text=f'{symbol} {abs(row["Variação %"]):.1f}%',
                                showarrow=False,
                                font=dict(color=color, size=12),
                                xshift=15,
                                yshift=10
                            )

            # Combinar dados para tabela
            df_previsao = pd.DataFrame(previsoes)
            df_completo = pd.concat([filtered_mensal, df_previsao], ignore_index=True)
            
            # Atualizar layout do gráfico
            fig_mensal.update_layout(
                xaxis=dict(
                    categoryorder='array',
                    categoryarray=meses_ativos,
                    gridcolor=COLORS['secondary'],
                    linecolor=COLORS['primary'],
                    title='Mês'
                ),
                yaxis=dict(
                    gridcolor=COLORS['secondary'],
                    linecolor=COLORS['primary'],
                    title='Faturamento (R$)',
                    tickprefix='R$ '
                ),
                hoverlabel=dict(
                    bgcolor=COLORS['card'],
                    font_size=14,
                    font_family=FONT_STYLE['family']
                ),
                plot_bgcolor=COLORS['plot_bg'],
                paper_bgcolor=COLORS['card'],
                font=dict(color=COLORS['text']),
                margin=dict(l=50, r=50, t=80, b=50),
                title=f'Previsão de Faturamento',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            # Preparar dados da tabela
            table_df = df_completo.copy()
            table_df['Faturamento'] = table_df['Faturamento'].apply(lambda x: f'R$ {x:,.2f}' if x else 'N/A')
            table_df['Variação %'] = table_df['Variação %'].apply(
                lambda x: f'{x:.1f}%' if pd.notna(x) else ('Previsão' if x is None else 'N/A')
            )
            table_data = table_df.to_dict('records')

        # =====================================
        # PROCESSAMENTO DIÁRIO 
        # =====================================
        if not cached_data['daily_data'].empty:
            filtered_diario = cached_data['daily_data'][
                (cached_data['daily_data']['ESTABELECIMENTO NOME1'].isin(clientes_selecionados)) &
                (cached_data['daily_data']['DATA'] >= pd.to_datetime(start_date)) &
                (cached_data['daily_data']['DATA'] <= pd.to_datetime(end_date))
            ]

            if not filtered_diario.empty:
                fig_diario.add_trace(go.Bar(
                    x=filtered_diario['DATA'],
                    y=filtered_diario['Faturamento Diário'],
                    name='Faturamento Diário',
                    marker_color=COLORS['primary']
                ))

        fig_diario.update_layout(
            xaxis=dict(
                gridcolor=COLORS['secondary'],
                linecolor=COLORS['primary'],
                title='Data'
            ),
            yaxis=dict(
                gridcolor=COLORS['secondary'],
                linecolor=COLORS['primary'],
                title='Faturamento Diário (R$)',
                tickprefix='R$ '
            ),
            plot_bgcolor=COLORS['plot_bg'],
            paper_bgcolor=COLORS['card'],
            font=dict(color=COLORS['text']),
            margin=dict(l=50, r=50, t=80, b=50),
            showlegend=False
        )

        if not cached_data['df'].empty:
            # Carregar dados semanais das abas correspondentes
            weekly_dfs = []
            xls = pd.ExcelFile('stores.xlsx')
            for sheet_name in xls.sheet_names:
                if sheet_name.startswith('Faturamento '):
                    df_sheet = pd.read_excel(xls, sheet_name=sheet_name)
                    df_sheet['MÊS'] = sheet_name.replace('Faturamento ', '')
                    weekly_dfs.append(df_sheet)
            
            if weekly_dfs:
                df_semanas = pd.concat(weekly_dfs, ignore_index=True)
                df_semanas = df_semanas.merge(
                    cached_data['df_cadastros'][['ESTABELECIMENTO CPF/CNPJ', 'ESTABELECIMENTO NOME1']],
                    left_on='CPF/CNPJ',
                    right_on='ESTABELECIMENTO CPF/CNPJ',
                    how='left'
                )
                
                filtered_semanas = df_semanas[
                    (df_semanas['ESTABELECIMENTO NOME1'].isin(clientes_selecionados)) &
                    (pd.to_datetime(df_semanas['DATA REGISTRO']) >= pd.to_datetime(start_date)) &
                    (pd.to_datetime(df_semanas['DATA REGISTRO']) <= pd.to_datetime(end_date))
                ]

                if not filtered_semanas.empty:
                    fig_semanal.add_trace(go.Bar(
                        x=filtered_semanas['MÊS'] + ' - Sem ' + filtered_semanas['SEMANA'].astype(str),
                        y=filtered_semanas['VALOR (R$)'],
                        marker_color=COLORS['highlight'],
                        opacity=0.8
                    ))

                    fig_semanal.update_layout(
                        title='Faturamento Semanal',
                        xaxis_title='Período',
                        yaxis_title='Valor (R$)',
                        plot_bgcolor=COLORS['plot_bg'],
                        paper_bgcolor=COLORS['card'],
                        font=dict(color=COLORS['text']),
                        margin=dict(l=50, r=50, t=80, b=50)
                    )

        columns = [
            {'name': 'Cliente', 'id': 'ESTABELECIMENTO NOME1'},
            {'name': 'Mês', 'id': 'Mês'},
            {'name': 'Faturamento', 'id': 'Faturamento'},
            {'name': 'Variação %', 'id': 'Variação %'}
        ]

    except Exception as e:
        print(f"Erro na análise: {str(e)}")

    return fig_mensal, fig_diario, fig_semanal, table_data, columns