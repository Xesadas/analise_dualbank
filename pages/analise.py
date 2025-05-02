import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output, dash_table, callback, register_page
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import logging
import traceback
import openpyxl
from openpyxl import Workbook

register_page(
    __name__,
    path='/',
    name='Analise clientes',
    title='Analise de clientes'
)

# =====================================
# CONFIGURAÇÃO DO AMBIENTE PERSISTENTE 
# =====================================

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
# CARREGAMENTO DE DADOS
# =====================================
try:
    df_cadastros = pd.read_excel(EXCEL_PATH, sheet_name='Sheet1', engine='openpyxl')
    df_transacoes = pd.read_excel(EXCEL_PATH, sheet_name='Transacoes', engine='openpyxl')
    df_transacoes['DATA'] = pd.to_datetime(df_transacoes['DATA'], dayfirst=True)
    
    df = pd.merge(df_transacoes, 
                df_cadastros[['ESTABELECIMENTO CPF/CNPJ', 'ESTABELECIMENTO NOME1']],
                left_on='CPF/CNPJ',
                right_on='ESTABELECIMENTO CPF/CNPJ',
                how='left')

except Exception as e:
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
    valores = cliente_data['Faturamento'].replace(0, np.nan).dropna()
    return np.mean(valores) if not valores.empty else 0

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

# =====================================
# PRÉ CARREGAMENTO DE DADOS 
# =====================================
cached_data = {
    'df_cadastros': pd.DataFrame(),
    'df_transacoes': pd.DataFrame(),
    'df': pd.DataFrame(),
    'df_long': pd.DataFrame(),
    'weekly_data': pd.DataFrame(),
    'last_modified': None
}

def load_data():
    global cached_data
    try:
        current_modified = os.path.getmtime(EXCEL_PATH)
        
        if cached_data['last_modified'] != current_modified:
            df_cadastros = pd.read_excel(EXCEL_PATH, sheet_name='Sheet1', engine='openpyxl')
            df_transacoes = pd.read_excel(EXCEL_PATH, sheet_name='Transacoes', engine='openpyxl')
            df_transacoes['DATA'] = pd.to_datetime(df_transacoes['DATA'], dayfirst=True)
            
            df = pd.merge(
                df_transacoes, 
                df_cadastros[['ESTABELECIMENTO CPF/CNPJ', 'ESTABELECIMENTO NOME1']],
                left_on='CPF/CNPJ',
                right_on='ESTABELECIMENTO CPF/CNPJ',
                how='left'
            )

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

            weekly_dfs = []
            try:
                xls = pd.ExcelFile(EXCEL_PATH)
                for sheet_name in xls.sheet_names:
                    if sheet_name.startswith('Faturamento '):
                        df_sheet = pd.read_excel(xls, sheet_name=sheet_name)
                        if 'CPF/CNPJ' in df_sheet.columns:
                            df_sheet.rename(columns={'CPF/CNPJ': 'ESTABELECIMENTO CPF/CNPJ'}, inplace=True)
                        
                        mes = sheet_name.replace('Faturamento ', '')
                        mes = 'Março' if mes == 'Marco' else mes
                        
                        df_sheet = pd.merge(
                            df_sheet,
                            df_cadastros[['ESTABELECIMENTO CPF/CNPJ', 'ESTABELECIMENTO NOME1']],
                            on='ESTABELECIMENTO CPF/CNPJ',
                            how='left'
                        )
                        
                        df_sheet['MÊS'] = mes
                        df_sheet['SEMANA'] = df_sheet.get('SEMANA', 0)
                        weekly_dfs.append(df_sheet)

                df_semanas = pd.concat(weekly_dfs, ignore_index=True) if weekly_dfs else pd.DataFrame()
            except Exception as e:
                print(f"Erro ao carregar semanas: {str(e)}")
                df_semanas = pd.DataFrame()

            cached_data.update({
                'df_cadastros': df_cadastros,
                'df_transacoes': df_transacoes,
                'df': df,
                'df_long': df_long,
                'weekly_data': df_semanas,
                'last_modified': current_modified
            })

    except Exception as e:
        logging.error(f"Erro geral: {str(e)}")

# =====================================
# LAYOUT 
# =====================================
layout = html.Div(style={'backgroundColor': COLORS['background'], 'minHeight': '100vh'}, children=[
    html.Div(className='container', style={'padding': '30px', 'maxWidth': '1200px', 'margin': '0 auto'}, children=[
        
        html.Div(className='header', style={'textAlign': 'center', 'marginBottom': '40px'}, children=[
            dcc.Interval(
                id='interval-component',
                interval=300*1000,
                n_intervals=0,
                disabled=False
            ),
            html.H1("📈 Análise de Faturamento", 
                   style={'color': COLORS['primary'], 'fontSize': '2.5em'}),
            html.P("Análise de faturamento de clientes DualBank", 
                  style={'color': COLORS['secondary'], 'fontSize': '1.1em'})
        ]),
        
        html.Div(className='control-card', style={
            'backgroundColor': COLORS['card'],
            'padding': '25px',
            'borderRadius': '15px',
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
            ])
        ])
    ])
])

# =====================================
# CALLBACKS 
# =====================================
@callback(
    Output('cliente-dropdown', 'options'),
    Input('interval-component', 'n_intervals')
)
def update_dropdown_options(n):
    load_data()
    df_cadastros = cached_data['df_cadastros']
    options = [{'label': str(nome), 'value': str(nome)} 
               for nome in df_cadastros['ESTABELECIMENTO NOME1'].unique() 
               if pd.notna(nome) and str(nome).strip() != '']
    return options if options else [{'label': 'Sem dados', 'value': 'NO_DATA'}]

@callback(
    Output('grafico-mensal', 'figure'),
    Output('grafico-semanal', 'figure'),
    Input('cliente-dropdown', 'value'),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date'),
    Input('interval-component', 'n_intervals')
)
def update_analysis(clientes_selecionados, start_date, end_date, n):
    fig_mensal = go.Figure()
    fig_semanal = go.Figure()

    if not clientes_selecionados or 'NO_DATA' in clientes_selecionados:
        return fig_mensal, fig_semanal

    try:
        load_data()
        
        if not cached_data['df_long'].empty:
            filtered_mensal = cached_data['df_long'].copy()
            filtered_mensal = filtered_mensal[filtered_mensal['ESTABELECIMENTO NOME1'].isin(clientes_selecionados)]
            filtered_mensal['Faturamento'] = pd.to_numeric(filtered_mensal['Faturamento'], errors='coerce').fillna(0)

            cores = px.colors.qualitative.Plotly
            
            for idx, cliente in enumerate(clientes_selecionados):
                cliente_data = filtered_mensal[filtered_mensal['ESTABELECIMENTO NOME1'] == cliente]
                if cliente_data.empty:
                    continue
                
                cliente_data = cliente_data.sort_values('Mês', key=lambda x: x.cat.codes)
                cliente_data['Faturamento Anterior'] = cliente_data['Faturamento'].shift(1)
                cliente_data['Variação %'] = (cliente_data['Faturamento'] / cliente_data['Faturamento Anterior'].replace(0, np.nan) - 1) * 100
                
                cliente_data_valida = cliente_data[cliente_data['Faturamento'] > 1]
                if cliente_data_valida.empty:
                    continue
                    
                ultimo_mes = cliente_data_valida['Mês'].iloc[-1]
                
                try:
                    idx_proximo = meses_ordem.index(ultimo_mes) + 1
                    proximo_mes = meses_ordem[idx_proximo] if idx_proximo < len(meses_ordem) else meses_ordem[0]
                except ValueError:
                    proximo_mes = 'Janeiro'

                valores_validos = cliente_data_valida['Faturamento']
                previsao = np.mean(valores_validos) if not valores_validos.empty else 0

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
                plot_bgcolor=COLORS['plot_bg'],
                paper_bgcolor=COLORS['card'],
                font=dict(color=COLORS['text']),
                margin=dict(l=50, r=50, t=80, b=50),
                title='Previsão de Faturamento',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )

        if not cached_data['weekly_data'].empty:
            try:
                clientes_cpfcnpj = df_cadastros[
                    df_cadastros['ESTABELECIMENTO NOME1'].isin(clientes_selecionados)
                ]['ESTABELECIMENTO CPF/CNPJ'].unique()

                filtered_semanas = cached_data['weekly_data'][
                    (cached_data['weekly_data']['ESTABELECIMENTO CPF/CNPJ'].isin(clientes_cpfcnpj)) &
                    (cached_data['weekly_data']['MÊS'].notna())
                ].copy()

                if not filtered_semanas.empty:
                    filtered_semanas['SEMANA'] = pd.to_numeric(filtered_semanas['SEMANA'], errors='coerce').fillna(0).astype(int)
                    filtered_semanas['MÊS_SEMANA'] = filtered_semanas['MÊS'] + ' - Semana ' + filtered_semanas['SEMANA'].astype(str)
                    
                    df_agrupado = filtered_semanas.groupby(
                        ['MÊS_SEMANA', 'ESTABELECIMENTO NOME1', 'MÊS', 'SEMANA']
                    ).agg({'VALOR (R$)': 'sum'}).reset_index()

                    meses_orden = ['Janeiro','Fevereiro','Março','Abril','Maio','Junho',
                                  'Julho','Agosto','Setembro','Outubro','Novembro','Dezembro']
                    df_agrupado['MÊS'] = pd.Categorical(
                        df_agrupado['MÊS'], 
                        categories=meses_orden, 
                        ordered=True
                    )
                    df_agrupado = df_agrupado.sort_values(['MÊS', 'SEMANA'])

                    fig_semanal = px.bar(
                        df_agrupado,
                        x='MÊS_SEMANA',
                        y='VALOR (R$)',
                        color='ESTABELECIMENTO NOME1',
                        barmode='group',
                        labels={'VALOR (R$)': 'Faturamento Semanal (R$)'},
                        category_orders={'MÊS_SEMANA': df_agrupado['MÊS_SEMANA'].unique()}
                    )
                    
                    fig_semanal.update_layout(
                        xaxis_title='Mês e Semana',
                        yaxis_title='Faturamento (R$)',
                        plot_bgcolor=COLORS['plot_bg'],
                        paper_bgcolor=COLORS['card'],
                        font=dict(color=COLORS['text']),
                        margin=dict(l=50, r=50, t=80, b=50),
                        xaxis_tickangle=-45,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )

            except Exception as e:
                print(f"Erro processamento semanal: {str(e)}")

    except Exception as e:
        print(f"Erro geral na análise: {str(e)}")

    return fig_mensal, fig_semanal