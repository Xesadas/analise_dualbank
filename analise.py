import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output, dash_table, page_container, callback, register_page
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import openpyxl

df = pd.read_excel('stores.xlsx', engine='openpyxl')

meses = {
    'Faturamento Dezembro': 'Dezembro',
    'Faturamento Janeiro': 'Janeiro',
    'Faturamento Fevereiro': 'Fevereiro'
}

df_long = df.melt(
    id_vars=['ESTABELECIMENTO NOME1', 'STATUS'],
    value_vars=meses.keys(),
    var_name='Mês',
    value_name='Faturamento'
)


df_long['Mês'] = df_long['Mês'].map(meses)
df_long['Mês'] = pd.Categorical(  
    df_long['Mês'], 
    categories=['Dezembro', 'Janeiro', 'Fevereiro', 'Março'], 
    ordered=True
)



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

# =====================================
# LAYOUT PRINCIPAL
# =====================================
layout = html.Div(style={'backgroundColor': COLORS['background'], 'minHeight': '100vh'}, children=[
    html.Div(className='container', style={'padding': '30px', 'maxWidth': '1200px', 'margin': '0 auto'}, children=[
        
        # Título
        html.Div(className='header', style={'textAlign': 'center', 'marginBottom': '40px'}, children=[
            html.H1("📈 Análise de Faturamento", 
                   style={'color': COLORS['primary'], 
                          'fontSize': '2.5em',
                          'textShadow': '2px 2px 4px rgba(0,0,0,0.1)'}),
            html.P("Análise comparativa mensal de desempenho comercial", 
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
            options=[{'label': nome, 'value': nome} 
                 for nome in df['ESTABELECIMENTO NOME1'].unique()],
            multi=True,
            placeholder="🔍 Selecione até 5 clientes...",
            style={
                'width': '100%',
                'borderRadius': '8px',
                'border': f'1px solid {COLORS["primary"]}',
                'backgroundColor': COLORS['card'],
                'color': COLORS['text']
            },
            className='custom-dropdown',
            maxHeight=300
            )
        ]),
        # Gráfico
        html.Div(className='graph-card', style={
            'backgroundColor': COLORS['card'],
            'padding': '20px',
            'borderRadius': '15px',
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)'
        }, children=[
            dcc.Graph(
                id='faturamento-grafico',
                style={'height': '65vh'},
                config={'displayModeBar': True, 'scrollZoom': False}
            )
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
                    'border': f'1px solid {COLORS["background"]}'
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
                        'backgroundColor': '#f8f9fa'
                    }
                ]
            )
        ])
    ])
])

@callback(
    Output('faturamento-grafico', 'figure'),
    Output('tabela-variacao', 'data'),
    Output('tabela-variacao', 'columns'),
    Input('cliente-dropdown', 'value')
)
def update_graph(clientes_selecionados):
    if not clientes_selecionados:
        return go.Figure(), [], []

    # Processamento dos dados
    filtered_df = df_long[df_long['ESTABELECIMENTO NOME1'].isin(clientes_selecionados)].copy()
    filtered_df.sort_values(['ESTABELECIMENTO NOME1', 'Mês'], inplace=True)

    # Cálculo da previsão
    previsoes = []
    meses_ordem = ['Dezembro', 'Janeiro', 'Fevereiro', 'Março']
    
    for cliente in clientes_selecionados:
        cliente_data = filtered_df[filtered_df['ESTABELECIMENTO NOME1'] == cliente]
        valores = cliente_data['Faturamento'].values
        
        # Modelo de previsão com média ponderada
        if len(valores) >= 2:
            pesos = [0.7, 0.3]  # 70% peso no último mês
            previsao = np.average(valores[-2:], weights=pesos)
        else:
            previsao = np.mean(valores) if len(valores) > 0 else 0
        
        previsoes.append({
            'ESTABELECIMENTO NOME1': cliente,
            'Mês': 'Março',
            'Faturamento': previsao,
            'Previsão': True
        })
    
    df_previsao = pd.DataFrame(previsoes)
    df_completo = pd.concat([filtered_df, df_previsao])

    # Cálculo das variações
    filtered_df['Faturamento Anterior'] = filtered_df.groupby('ESTABELECIMENTO NOME1')['Faturamento'].shift(1)
    filtered_df['Variação R$'] = filtered_df['Faturamento'] - filtered_df['Faturamento Anterior']
    filtered_df['Variação %'] = np.where(
        filtered_df['Faturamento Anterior'] != 0,
        (filtered_df['Variação R$'] / filtered_df['Faturamento Anterior']) * 100,
        np.nan
    )

    # Preparação da tabela
    table_df = filtered_df[filtered_df['Mês'] != 'Dezembro'].copy()
    table_df = table_df[['ESTABELECIMENTO NOME1', 'Mês', 'Variação R$', 'Variação %']]
    table_df['Variação R$'] = table_df['Variação R$'].apply(lambda x: f'R$ {x:,.2f}' if pd.notna(x) else 'N/A')
    table_df['Variação %'] = table_df['Variação %'].apply(lambda x: f'{x:.2f}%' if pd.notna(x) else 'N/A')

    columns = [
        {'name': 'Cliente', 'id': 'ESTABELECIMENTO NOME1'},
        {'name': 'Mês', 'id': 'Mês'},
        {'name': 'Variação R$', 'id': 'Variação R$'},
        {'name': 'Variação %', 'id': 'Variação %'}
    ]

    # Criação do gráfico
    fig = go.Figure()
    
    # Cores para diferenciação
    cores = px.colors.qualitative.Plotly
    
    for idx, cliente in enumerate(clientes_selecionados):
        dados_cliente = df_completo[df_completo['ESTABELECIMENTO NOME1'] == cliente]
        
        # Linha histórica
        fig.add_trace(go.Scatter(
            x=dados_cliente['Mês'],
            y=dados_cliente['Faturamento'],
            name=cliente,
            mode='lines+markers',
            line=dict(width=3, color=cores[idx]),
            marker=dict(size=10, color=cores[idx]),
            hovertemplate='<b>%{x}</b><br>R$ %{y:,.2f}<extra></extra>'
        ))
        
        # Linha de previsão
        if not dados_cliente[dados_cliente['Mês'] == 'Março'].empty:
            fig.add_trace(go.Scatter(
                x=['Fevereiro', 'Março'],
                y=[
                    dados_cliente[dados_cliente['Mês'] == 'Fevereiro']['Faturamento'].values[0],
                    dados_cliente[dados_cliente['Mês'] == 'Março']['Faturamento'].values[0]
                ],
                mode='lines',
                line=dict(
                    dash='dot',
                    color=cores[idx],
                    width=2
                ),
                showlegend=False,
                hoverinfo='none'
            ))
            
            # Marcador de previsão
            fig.add_trace(go.Scatter(
                x=['Março'],
                y=[dados_cliente[dados_cliente['Mês'] == 'Março']['Faturamento'].values[0]],
                mode='markers+text',
                marker=dict(
                    size=14,
                    color=cores[idx],
                    symbol='diamond'
                ),
                text=[f'Previsão: R$ {dados_cliente[dados_cliente["Mês"] == "Março"]["Faturamento"].values[0]:,.2f}'],
                textposition='top center',
                showlegend=False,
                hoverinfo='y'
            ))

    # Atualizar layout
    fig.update_layout(
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
        title='Evolução do Faturamento com Previsão para Março',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Adicionar setas de variação
    for cliente in clientes_selecionados:
        cliente_data = filtered_df[filtered_df['ESTABELECIMENTO NOME1'] == cliente]
        for i, row in cliente_data.iterrows():
            if pd.notna(row['Variação R$']):
                symbol = '▲' if row['Variação R$'] > 0 else '▼'
                color = COLORS['success'] if row['Variação R$'] > 0 else COLORS['danger']
                fig.add_annotation(
                    x=row['Mês'],
                    y=row['Faturamento'],
                    text=f'{symbol} {abs(row["Variação %"]):.1f}%',
                    showarrow=False,
                    font=dict(color=color, size=12),
                    xshift=15,
                    yshift=10
                )
    
    return fig, table_df.to_dict('records'), columns
    