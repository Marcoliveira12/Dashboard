# Importando as bibliotecas necessárias
from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Importando módulos personalizados
from app import *
from dash_bootstrap_templates import ThemeSwitchAIO

# Definindo temas e templates para o Dash
url_theme1 = dbc.themes.SLATE
url_theme2 = dbc.themes.COSMO
template_theme1 = 'slate'
template_theme2 = 'cosmo'

# Lendo os dados do arquivo CSV
df = pd.read_csv('dados_tratados_netflix.csv', sep=",")

# Criando opções para o dropdown de seleção de países
country_options = [{'label': x, 'value': x} for x in df['Country'].unique()]

#pegando as 5 maiores bibliotecas
def get_top_countries(df, n=5):
    top_countries = df.nlargest(n, 'Total Library Size')
    return top_countries['Country'].tolist()

# Definindo o layout da aplicação Dash
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            # Componente para alternar entre os temas de cores
            ThemeSwitchAIO(aio_id='theme', themes=[url_theme1, url_theme2]),
            # Título da página
            html.H3("Preço de inscrição Netflix"),
            # Dropdown para seleção de países
            dcc.Dropdown(
                id='Country',
                value=get_top_countries(df),
                multi=True,
                options=country_options
            ),
        ])
    ]),
    dbc.Row([
        dbc.Col([
            # Gráfico de barras
            dcc.Graph(id='bar-graph')
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                # Dropdown para seleção do primeiro país e gráfico associado
                dcc.Dropdown(
                    id='pais1',
                    value=country_options[0]['label'],
                    options=country_options
                ),
                dcc.Graph(id='indicator1'),
            ])
        ]),
        dbc.Col([
            dbc.Row([
                # Dropdown para seleção do segundo país e gráfico associado
                dcc.Dropdown(
                    id='pais2',
                    value=country_options[1]['label'],
                    options=country_options
                ),
                dcc.Graph(id='indicator2'),
            ]),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
           # Título para informações detalhadas do país selecionado
           html.H3('See full country info'),
           dcc.Dropdown(
               id='country1',
               value=country_options[0]['value'],
               multi=False,
               options=country_options
           )
        ]),
    ]),
    dbc.Row([
        dbc.Col([], id='dTable')
    ])
])

# Callback para atualizar o gráfico de barras
@app.callback(
    Output('bar-graph', 'figure'),
    Input('Country', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
)
def update_graph(selected_countries, toggle):
    # Filtrando o DataFrame com base nos países selecionados
    filtered_df = df[df['Country'].isin(selected_countries)]
    template = template_theme1 if toggle else template_theme2
    
    # Ordenando o DataFrame filtrado pelo tamanho da biblioteca
    filtered_df = filtered_df.sort_values(by='Total Library Size', ascending=False)
    
    # Criando um gráfico de barras com Plotly Express
    fig = px.bar(
        filtered_df,
        x='Country',
        y='Custo Médio Por Mês ($)',
        color='Total Library Size',  
        barmode='group',
        labels={'Country': 'País', 'Custo Médio Por Mês ($)': 'Custo Médio Por Mês ($)', 'Total Library Size': 'Tamanho da Biblioteca Total'}
    )
    
    # Atualizando o layout do gráfico
    fig.update_layout(title='Preço de inscrição Netflix por País', title_x=0.5, template=template)

    return fig

# Callback para atualizar o primeiro indicador
@app.callback(
    Output('indicator1', 'figure'),
    Input('pais1', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
)
def update_indicator1(pais1, toggle):
    return update_indicator(pais1, toggle)

# Callback para atualizar o segundo indicador
@app.callback(
    Output('indicator2', 'figure'),
    Input('pais2', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
)
def update_indicator2(pais2, toggle):
    return update_indicator(pais2, toggle)

# Função para atualizar os indicadores
def update_indicator(pais, toggle):
    df_data = df.copy(deep=True)
    template = template_theme1 if toggle else template_theme2
    
    # Filtrando os dados para o país selecionado
    data_pais = df_data[df_data['Country'] == pais]
   
    # Criando um gráfico de indicador com Plotly Graph Objects
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode='number',
        title={'text': pais},
        value=data_pais['Custo Médio Por Mês ($)'].values[0],
        number={'prefix': '$', 'valueformat': '.2f'},
    ))

    fig.update_layout(template=template)

    return fig

# Callback para atualizar a tabela de dados
@app.callback(
    Output('dTable', 'children'),
    Input('country1', 'value'),
    Input(ThemeSwitchAIO.ids.switch('theme'), 'value')
)
def update_output(value, toggle):    
    # Filtrando o DataFrame para o país selecionado
    dfT = df[df['Country'] == value].copy()
    dfT.drop(['Country', 'Custo Médio Por Mês ($)'], inplace=True, axis=1) 

    if toggle:
        # Criando uma tabela estilizada com Dash DataTable (tema escuro)
        table = dash.dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in dfT.columns],
            data=dfT.to_dict('records'),
            style_table={'margin': 'left'},
            style_header={
                'backgroundColor': 'rgb(32, 35, 38)',
                'color': 'light grey'},
            style_data={
                'backgroundColor': 'rgb(52, 58, 64)',
                'color': 'light grey'},
        )
    else:
        # Criando uma tabela com Dash DataTable (tema padrão)
        table = dash.dash_table.DataTable(  
            columns=[{"name": col, "id": col} for col in dfT.columns],
            data=dfT.to_dict('records'),
        )
    return table

# Inicialização da aplicação Dash
if __name__ == '__main__':
    app.run_server(debug=True, port=8052)
