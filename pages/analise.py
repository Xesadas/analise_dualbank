import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output, dash_table, callback, register_page
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os



#REFERENTE A ANÁLISE DE DADOS!!!

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
    # Carregar dados de cadastros
    df_cadastros = pd.read_excel('stores.xlsx', sheet_name='Sheet1', engine='openpyxl')
    
    # Carregar transações diárias
    df_transacoes = pd.read_excel('stores.xlsx', sheet_name='Transacoes', engine='openpyxl')
    df_transacoes['DATA'] = pd.to_datetime(df_transacoes['DATA'], dayfirst=True)
    
    # Mesclar dados para obter nomes
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
    'Faturamento Abril': 'abril',
    'Faturamento Maio': 'maio',
    'Faturamento Junho': 'junho',
    'Faturamento Julho': 'julho',
    'Faturamento Agosto': 'agosto',
    'Faturamento Setembro': 'setembro',
    'Faturamento Outubro': 'outubro',
    'Faturamento Novembro': 'novembro',
    #'Faturamento Dezembro': 'dezembro'

}

if not df_cadastros.empty:
    df_long = df_cadastros.melt(
        id_vars=['ESTABELECIMENTO NOME1', 'STATUS'],
        value_vars=meses.keys(),
        var_name='Mês',
        value_name='Faturamento'
    )
    
    df_long['Mês'] = df_long['Mês'].map(meses)
    df_long['Mês'] = pd.Categorical(
        df_long['Mês'], 
        categories=['Dezembro', 'Janeiro', 'Fevereiro', 'Março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro'], 
        ordered=True
    )
else:
    df_long = pd.DataFrame()



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
    'highlight': '#f1c40f',
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
            
            # Prepara df_long
            meses = {'Faturamento Dezembro': 'Dezembro', 'Faturamento Janeiro': 'Janeiro', 'Faturamento Fevereiro': 'Fevereiro'}
            df_long = df_cadastros.melt(
                id_vars=['ESTABELECIMENTO NOME1', 'STATUS'],
                value_vars=meses.keys(),
                var_name='Mês',
                value_name='Faturamento'
            ) if not df_cadastros.empty else pd.DataFrame()
            
            df_long['Mês'] = df_long['Mês'].map(meses)
            df_long['Mês'] = pd.Categorical(
                df_long['Mês'], 
                categories=['Dezembro', 'Janeiro', 'Fevereiro', 'Março'], 
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
            
            # Atualiza cache
            cached_data.update({
                'df_cadastros': df_cadastros,
                'df_transacoes': df_transacoes,
                'df': df,
                'df_long': df_long,
                'daily_data': daily_data,
                'last_modified': current_modified
            })
            
    except Exception as e:
        print(f"Erro ao carregar dados: {str(e)}")
    
    return cached_data
    

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
])

#=====================================
# CALLBACKS 
#=====================================

@callback(
    Output('cliente-dropdown', 'options'),
    Input('interval-component', 'n_intervals')
)

def update_dropdown(n):
    data = load_data()
    df_cadastros = data['df_cadastros']
    options = [{'label': str(nome), 'value': str(nome)} 
               for nome in df_cadastros['ESTABELECIMENTO NOME1'].unique() 
               if pd.notna(nome) and str(nome).strip() != '']
    return options if options else [{'label': 'Sem dados', 'value': 'NO_DATA'}]


@callback(
    Output('grafico-mensal', 'figure'),
    Output('grafico-diario', 'figure'),
    Output('tabela-variacao', 'data'),
    Output('tabela-variacao', 'columns'),
    Input('cliente-dropdown', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date'),
    Input('interval-component', 'n_intervals') 
)
def update_analysis(clientes_selecionados, start_date, end_date,n):

    data = load_data()
    
    fig_mensal = go.Figure()
    fig_diario = go.Figure()
    table_data = []
    columns = []

    # Verificação de seleção vazia
    if not clientes_selecionados or 'NO_DATA' in clientes_selecionados:
        return fig_mensal, fig_diario, [], []

    try:
        # =====================================
        # PROCESSAMENTO MENSAL COM PREVISÃO 
        # =====================================
        if not df_long.empty:
            # Filtragem e cálculos originais
            filtered_mensal = df_long[df_long['ESTABELECIMENTO NOME1'].isin(clientes_selecionados)].copy()
            filtered_mensal['Faturamento Anterior'] = filtered_mensal.groupby('ESTABELECIMENTO NOME1')['Faturamento'].shift(1)
            
            
            previsoes = []
            for cliente in clientes_selecionados:
                cliente_data = filtered_mensal[filtered_mensal['ESTABELECIMENTO NOME1'] == cliente]
                valores = cliente_data['Faturamento'].values
                
                
                if len(valores) >= 2:
                    pesos = [0.7, 0.3]
                    previsao = np.average(valores[-2:], weights=pesos)
                else:
                    previsao = np.mean(valores) if len(valores) > 0 else 0
                
                previsoes.append({
                    'ESTABELECIMENTO NOME1': cliente,
                    'Mês': 'Março',
                    'Faturamento': previsao,
                    'Previsão': True
                })
            
            # Mesclando dados reais + previsão
            df_previsao = pd.DataFrame(previsoes)
            df_completo = pd.concat([filtered_mensal, df_previsao])
            
            # Criação do gráfico mensal com detalhes visuais originais
            meses_ordem = ['Dezembro', 'Janeiro', 'Fevereiro', 'Março']
            cores = px.colors.qualitative.Plotly
            
            for idx, cliente in enumerate(clientes_selecionados):
                dados_cliente = df_completo[df_completo['ESTABELECIMENTO NOME1'] == cliente]
                
                # Linha principal 
                fig_mensal.add_trace(go.Scatter(
                    x=dados_cliente['Mês'],
                    y=dados_cliente['Faturamento'],
                    name=cliente,
                    mode='lines+markers',
                    line=dict(width=3, color=cores[idx]),
                    marker=dict(size=10, color=cores[idx]),
                    hovertemplate='<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>'
                ))
                
                # Linha de previsão pontilhada 
                if not dados_cliente[dados_cliente['Mês'] == 'Março'].empty:
                    fig_mensal.add_trace(go.Scatter(
                        x=['Fevereiro', 'Março'],
                        y=[
                            dados_cliente[dados_cliente['Mês'] == 'Fevereiro']['Faturamento'].values[0],
                            dados_cliente[dados_cliente['Mês'] == 'Março']['Faturamento'].values[0]
                        ],
                        mode='lines',
                        line=dict(dash='dot', color=cores[idx], width=2),
                        showlegend=False,
                        hoverinfo='none'
                    ))
                    
                    # Marcador de diamante para previsão
                    fig_mensal.add_trace(go.Scatter(
                        x=['Março'],
                        y=[dados_cliente[dados_cliente['Mês'] == 'Março']['Faturamento'].values[0]],
                        mode='markers+text',
                        marker=dict(size=14, color=cores[idx], symbol='diamond'),
                        text=[f'Previsão: R$ {dados_cliente[dados_cliente["Mês"] == "Março"]["Faturamento"].values[0]:,.2f}'],
                        textposition='top center',
                        showlegend=False,
                        hoverinfo='y'
                    ))

            # Layout do gráfico mantendo estilo original
            fig_mensal.update_layout(
                xaxis=dict(
                    categoryorder='array',
                    categoryarray=meses_ordem,
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
                title='Evolução do Faturamento com Previsão para o fim dos tempos',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

            # Adicionar setas de variação 
            filtered_mensal['Variação %'] = (filtered_mensal['Faturamento'] / filtered_mensal['Faturamento Anterior'] - 1) * 100
            for cliente in clientes_selecionados:
                cliente_data = filtered_mensal[filtered_mensal['ESTABELECIMENTO NOME1'] == cliente]
                for i, row in cliente_data.iterrows():
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

            # Preparar dados da tabela 
            table_df = filtered_mensal.copy()
            table_df['Faturamento'] = table_df['Faturamento'].apply(lambda x: f'R$ {x:,.2f}')
            table_df['Variação %'] = table_df['Variação %'].apply(lambda x: f'{x:.1f}%' if pd.notna(x) else 'N/A')
            table_data = table_df.to_dict('records')

        # =====================================
        # PROCESSAMENTO DIÁRIO 
        # =====================================
        if not daily_data.empty:
            filtered_diario = daily_data[
                (daily_data['ESTABELECIMENTO NOME1'].isin(clientes_selecionados)) &
                (daily_data['DATA'] >= pd.to_datetime(start_date)) &
                (daily_data['DATA'] <= pd.to_datetime(end_date))
            ]
            
            if not filtered_diario.empty:
                fig_diario.add_trace(go.Bar(
                    x=filtered_diario['DATA'],
                    y=filtered_diario['Faturamento Diário'],
                    name='Faturamento Diário',
                    marker_color=COLORS['primary']
                ))

        # Layout do gráfico diário 
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

        # Colunas da tabela 
        columns = [
            {'name': 'Cliente', 'id': 'ESTABELECIMENTO NOME1'},
            {'name': 'Mês', 'id': 'Mês'},
            {'name': 'Faturamento', 'id': 'Faturamento'},
            {'name': 'Variação %', 'id': 'Variação %'}
        ]

    except Exception as e:
        print(f"Erro na análise: {str(e)}")

    return fig_mensal, fig_diario, table_data, columns