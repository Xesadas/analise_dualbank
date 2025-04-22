import dash
from dash import Dash, html, dcc

app = Dash(__name__, suppress_callback_exceptions=True, use_pages=True)
server = app.server

SERVER_DATA_PATH = '/data/stores.xlsx' 

link_style = {
    'color': 'white',
    'marginRight': '20px',
    'textDecoration': 'none',
    'padding': '10px',
    'backgroundColor': '#1a064d',
    'borderRadius': '5px',
    'transition': 'all 0.3s ease'
}

navbar_style = {
    'backgroundColor': 'black',
    'padding': '20px',
    'marginBottom': '30px',
    'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
    'display': 'flex',
    'justifyContent': 'center'
}

# Layout principal com navbar
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        dcc.Link('📈 Acompanhamento Clientes', href=dash.page_registry['pages.analise']['path'], style=link_style),
        dcc.Link('📁 Dados Clientes', href=dash.page_registry['pages.dados']['path'], style=link_style),
        dcc.Link('📝 Lançamento de Dados dos Clientes', href=dash.page_registry['pages.inputs']['path'], style=link_style),
        dcc.Link('🦈🦈🦈🦈Novos clientes🦈🦈🦈🦈', href=dash.page_registry['pages.novos_clientes']['path'], style=link_style),
        dcc.Link('💸 Emprestimos', href=dash.page_registry['pages.Emprestimos']['path'], style=link_style),
        dcc.Link('🕵️‍♂️ Análise Agente', href=dash.page_registry['pages.agent_analysis']['path'], style=link_style),

    ], style=navbar_style),
    dash.page_container
])

if __name__ == '__main__':
    app.run(debug=True)