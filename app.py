import dash
from dash import Dash, html, dcc, Input, Output, callback

# Importar páginas
from analise import layout as analise_layout
from dados import layout as data_layout

# Criar aplicação
app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Estilos
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
        dcc.Link('📈 Acompanhamento Clientes', href='/', style=link_style),
        dcc.Link('📁 Dados Clientes', href='/dados', style=link_style)
    ], style=navbar_style),
    html.Div(id='page-content')
])

# Callback de roteamento
@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/dados':
        return data_layout
    return analise_layout  # Retorna o layout do dashboard importado

if __name__ == '__main__':
    app.run_server(debug=True)