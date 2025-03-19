import streamlit as st
import requests
import pandas as pd
import time
from utils import generate_pdf
import plotly.express as px
import subprocess


API_URL = "http://127.0.0.1:5000"

# Inicia a API Flask em segundo plano
api_process = subprocess.Popen(["python", "app.py"])


st.set_page_config(page_title="Gerenciamento de Produtos", page_icon="📦")
st.title("📦 Gerenciamento de Produtos")
sidebar_options_produtos = [
                            'Listar Produtos', 
                            'Alterar Produto', 
                            'Excluir Produto',
                            'Entrada de Produtos',
                            'Saída de Produtos',
                            'Gráficos'
                            ]
f_pagina = st.sidebar.selectbox("Selecione a página:", sidebar_options_produtos, placeholder='Selecione a opção', index=0)
st.subheader(f_pagina)

# Aguarde até que a API esteja disponível
max_retries = 20  # Número máximo de tentativas
attempts = 0

while attempts < max_retries:
    try:
        response = requests.get(f"{API_URL}/produtos")

        if response.status_code == 200:
            st.sidebar.warning("✅ API carregada com sucesso!")
            break
    except requests.exceptions.ConnectionError as error:
        
        print(f"⏳ Aguardando API carregar...{error}")
    
    attempts += 1
    time.sleep(2)  # Espera 2 segundos antes de tentar novamente
    

if attempts == max_retries:
    st.sidebar.error("❌ Falha ao conectar à API. Verifique se o app.py está rodando corretamente.")
    exit(1)  # Encerra o script caso a API não carregue


if f_pagina == 'Listar Produtos':

    response = requests.get(f"{API_URL}/produtos")
    if response.status_code == 200:
        produtos = response.json()  # Assume que a resposta é uma lista de produtos em formato JSON
        
        # Cria um DataFrame para exibir no Streamlit
        df = pd.DataFrame(produtos)

        # Se o índice não for desejado, você pode resetá-lo
        df = df.reset_index(drop=True)

        # Define a nova ordem das colunas
        nova_ordem = ['id', 'nome', 'descricao', 'quantidade_estoque', 'preco']  # Substitua pelos nomes reais das colunas
        
        # Reorganiza as colunas conforme a nova ordem
        df = df[nova_ordem]
        df = df.rename(columns={
            
            'nome': 'Nome', 
            'descricao': 'Descricao',
            'quantidade_estoque': 'Qtd',
            'preco': 'Preço'
            # Adicione mais colunas conforme necessário
        })
        
        # Exibe os dados em uma tabela no Streamlit
        st.table(df)
    else:
        st.error(f"Erro ao buscar produtos: {response.status_code}")

    st.divider()
    if st.button("Exportar para PDF"):
        pdf_buffer = generate_pdf(df)
        st.download_button(
            label="Baixar PDF",
            data=pdf_buffer,
            file_name="lista_produtos.pdf",
            mime="application/pdf"
        )
    st.divider()
    st.markdown("### Adicionar Produto")
    nome = st.text_input("Nome do Produto")
    descricao = st.text_input("Descrição do Produto")
    preco = st.number_input("Preço do Produto")
    if st.button("Adicionar Produto"):
        data = {"nome": nome, "descricao": descricao, "preco": preco}
        response = requests.post(f"{API_URL}/produtos", json=data)
        if response.status_code == 200:
            st.success("Produto adicionado com sucesso!")
            st.rerun()
            

        else:
            st.error("Erro ao adicionar produto")

if f_pagina == 'Adicionar Produto':
    nome = st.text_input("Nome do Produto")
    descricao = st.text_input("Descrição do Produto")
    preco = st.number_input("Preço do Produto")
    if st.button("Adicionar Produto"):
        data = {"nome": nome, "descricao": descricao, "preco": preco}
        response = requests.post(f"{API_URL}/produtos", json=data)
        if response.status_code == 200:
            st.success("Produto adicionado com sucesso!")
        else:
            st.error("Erro ao adicionar produto")

if f_pagina == 'Alterar Produto':
    response = requests.get(f"{API_URL}/produtos")
    # Criar um dicionário para mapear nome -> id
    produto_dict = {produto['nome']: produto['id'] for produto in response.json()}
    # Criar o selectbox com os nomes dos produtos
    produto_selecionado = st.selectbox("Selecione um produto", list(produto_dict.keys()))
    # ID do produto selecionado
    id_produto_selecionado = produto_dict[produto_selecionado]

    novo_nome = st.text_input('Informe o novo nome')

    if st.button("Atualizar Produto"):
        data = {"nome": novo_nome }
        response = requests.put(f"{API_URL}/produto/{id_produto_selecionado}", json=data)
        if response.status_code == 200:
            st.success("Produto atualizado!")
        else:
            st.error("Erro ao atualizar produto")

if f_pagina == 'Excluir Produto':
    
    response = requests.get(f"{API_URL}/produtos")
    # Criar um dicionário para mapear nome -> id
    produto_dict = {produto['nome']: produto['id'] for produto in response.json()}
    # Criar o selectbox com os nomes dos produtos
    produto_selecionado = st.selectbox("Selecione um produto", list(produto_dict.keys()))
    # ID do produto selecionado
    id_produto_selecionado = produto_dict[produto_selecionado]
    

    if st.button("Deletar Produto"):
        response = requests.delete(f"{API_URL}/produto/{id_produto_selecionado}")
        if response.status_code == 200:
            st.success("Produto deletado!")
        else:
            st.error("Erro ao deletar produto")

if f_pagina == 'Entrada de Produtos':

    response = requests.get(f"{API_URL}/entradas")
    if response.status_code == 200:
        entradas = response.json()  # Assume que a resposta é uma lista de produtos em formato JSON
        
        # Cria um DataFrame para exibir no Streamlit
        df = pd.DataFrame(entradas)

        # Formatar 'data'
        df['data'] = pd.to_datetime(df['data']).dt.strftime('%d/%m/%Y %H:%M:%S')

        # Se o índice não for desejado, você pode resetá-lo
        df = df.reset_index(drop=True)

        # Define a nova ordem das colunas
        nova_ordem = ['id', 'produto', 'quantidade', 'data']
        df = df[nova_ordem]

        df = df.rename(columns={
            
            'id': 'ID', 
            'produto': 'Produto',
            'quantidade': 'Qtd',
            'data': 'Data'
            # Adicione mais colunas conforme necessário
        })
                      
        # Exibe os dados em uma tabela no Streamlit
        st.table(df)
    else:
        st.error(f"Erro ao buscar produtos: {response.status_code}")
    st.divider()
    if st.button("Exportar para PDF"):
        pdf_buffer = generate_pdf(df)
        st.download_button(
            label="Baixar PDF",
            data=pdf_buffer,
            file_name="lista_entradas.pdf",
            mime="application/pdf"
        )
    st.divider()
    st.markdown("### Adicionar Entrada")
    produtos = requests.get(f"{API_URL}/produtos")
    # Criar um dicionário para mapear nome -> id
    produto_dict = {produto['nome']: produto['id'] for produto in produtos.json()}
    # Criar o selectbox com os nomes dos produtos
    produto_selecionado = st.selectbox("Selecione um produto", list(produto_dict.keys()))
    # ID do produto selecionado
    id_produto_selecionado = produto_dict[produto_selecionado]
    quantidade = st.number_input("Informe a quantidade", min_value=1)
    
    if st.button("Adicionar Entrada"):
        entrada = {"produto_id": id_produto_selecionado, "quantidade": quantidade}
        
        response = requests.post(f"{API_URL}/entradas", json=entrada)
        if response.status_code == 201:
            with st.empty():
                st.success("Entrada registrada com sucesso!")
                time.sleep(1)
                st.rerun()
        else:
            st.error("Erro ao adicionar entrada")

if f_pagina == 'Saída de Produtos':
    response = requests.get(f"{API_URL}/saidas")
    if response.status_code == 200:
        saidas = response.json()  # Assume que a resposta é uma lista de produtos em formato JSON
        
        # Cria um DataFrame para exibir no Streamlit
        df = pd.DataFrame(saidas)

        # Formatar 'data'
        df['data'] = pd.to_datetime(df['data']).dt.strftime('%d/%m/%Y %H:%M:%S')

        # Se o índice não for desejado, você pode resetá-lo
        df = df.reset_index(drop=True)

        # Define a nova ordem das colunas
        nova_ordem = ['id', 'produto', 'quantidade', 'data']
        df = df[nova_ordem]

        df = df.rename(columns={
            
            'id': 'ID', 
            'produto': 'Produto',
            'quantidade': 'Qtd',
            'data': 'Data'
            # Adicione mais colunas conforme necessário
        })
                      
        # Exibe os dados em uma tabela no Streamlit
        st.table(df)
    else:
        st.error(f"Erro ao buscar produtos: {response.status_code}")
    st.divider()
    if st.button("Exportar para PDF"):
        pdf_buffer = generate_pdf(df)
        st.download_button(
            label="Baixar PDF",
            data=pdf_buffer,
            file_name="lista_saidas.pdf",
            mime="application/pdf"
        )
    st.divider()
    st.markdown("### Adicionar Saída")
    produtos = requests.get(f"{API_URL}/produtos")
    # Criar um dicionário para mapear nome -> id
    produto_dict = {produto['nome']: produto['id'] for produto in produtos.json()}
    # Criar o selectbox com os nomes dos produtos
    produto_selecionado = st.selectbox("Selecione um produto", list(produto_dict.keys()))
    # ID do produto selecionado
    id_produto_selecionado = produto_dict[produto_selecionado]
    quantidade = st.number_input("Informe a quantidade", min_value=1)
    
    if st.button("Adicionar Saída"):
        entrada = {"produto_id": id_produto_selecionado, "quantidade": quantidade}
        
        response = requests.post(f"{API_URL}/saidas", json=entrada)
        if response.status_code == 201:
            with st.empty():
                st.success("Saída registrada com sucesso!")
                time.sleep(1)
                st.rerun()
        else:
            st.error(response.json())


if f_pagina == 'Gráficos':
    
    response = requests.get(f"{API_URL}/entradas")
    if response.status_code == 200:
        entradas = response.json()  # Assume que a resposta é uma lista de produtos em formato JSON
        
        # Cria um DataFrame para exibir no Streamlit
        df = pd.DataFrame(entradas)
        df = df.sort_values(['data'], ascending=True)
        # Convertendo a coluna 'data' para datetime
        df['data'] = pd.to_datetime(df['data'])
        # Convertendo para apenas a parte da data
        df['data'] = df['data'].dt.date
        df_grouped = df.groupby('data')['quantidade'].sum().reset_index()

        fig_total_tesouro_diario = px.line(df_grouped, x='data', y='quantidade', title='Entradas', markers=True)
        st.plotly_chart(fig_total_tesouro_diario, use_container_width=True)

    response = requests.get(f"{API_URL}/saidas")
    if response.status_code == 200:
        saidas = response.json()  # Assume que a resposta é uma lista de produtos em formato JSON
        
        # Cria um DataFrame para exibir no Streamlit
        df = pd.DataFrame(saidas)
        df = df.sort_values(['data'], ascending=True)
        # Convertendo a coluna 'data' para datetime
        df['data'] = pd.to_datetime(df['data'])
        # Convertendo para apenas a parte da data
        df['data'] = df['data'].dt.date
        df_grouped = df.groupby('data')['quantidade'].sum().reset_index()
        fig_total_tesouro_diario = px.line(df_grouped, x='data', y='quantidade', title='Saídas', markers=True)
        st.plotly_chart(fig_total_tesouro_diario, use_container_width=True)
    