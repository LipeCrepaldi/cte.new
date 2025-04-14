import streamlit as st
import bcrypt
import pandas as pd
import xml.etree.ElementTree as ET
import plotly.express as px
import streamlit_authenticator as stauth

# ----------------- AUTENTICAÇÃO -----------------
names = ["Cliente 1", "Cliente 2"]
usernames = ["cliente1", "cliente2"]

# Senhas em texto simples (somente para exemplo, as senhas reais devem ser protegidas)
passwords = ["senha123", "senha456"]

# Gerando os hashes das senhas
hashed_passwords = [bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8') for password in passwords]

# Configuração da autenticação
authenticator = stauth.Authenticate(
    names, usernames, hashed_passwords,
    "painel_cte", "abcdef", cookie_expiry_days=1
)

# Login
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    authenticator.logout("Sair", "sidebar")
    st.sidebar.success(f"Logado como: {name}")

    # ----------------- APP PRINCIPAL -----------------
    st.set_page_config(page_title="Painel de CT-e", layout="wide")
    st.title("📦 Painel de Gestão de CT-e")

    # Upload do arquivo XML
    uploaded_file = st.file_uploader("Faça o upload de um arquivo XML de CT-e", type=["xml"])

    if uploaded_file is not None:
        try:
            tree = ET.parse(uploaded_file)
            root = tree.getroot()
            ns = {'cte': 'http://www.portalfiscal.inf.br/cte'}

            # Extração das informações do XML
            numero = root.find(".//cte:ide/cte:nCT", ns)
            emitente = root.find(".//cte:emit/cte:xNome", ns)
            valor_total = root.find(".//cte:vPrest/cte:vTPrest", ns)
            peso_total = root.find(".//cte:infCarga/cte:pesoBruto", ns)
            motorista = root.find(".//cte:infModal/cte:rodo/cte:mot/cte:xNome", ns)
            placa = root.find(".//cte:infModal/cte:rodo/cte:veic/cte:placa", ns)
            destino = root.find(".//cte:dest/cte:xNome", ns)
            data_emissao = root.find(".//cte:ide/cte:dhEmi", ns)

            # Exibir dados extraídos
            st.subheader("📄 Informações extraídas do XML:")
            st.write(f"Número do CT-e: {numero.text if numero is not None else 'N/A'}")
            st.write(f"Emitente: {emitente.text if emitente is not None else 'N/A'}")
            st.write(f"Valor Total: R$ {valor_total.text if valor_total is not None else '0.00'}")
            st.write(f"Peso Total: {peso_total.text if peso_total is not None else '0.00'} kg")
            st.write(f"Motorista: {motorista.text if motorista is not None else 'Desconhecido'}")
            st.write(f"Placa do Veículo: {placa.text if placa is not None else 'Não informada'}")
            st.write(f"Destino: {destino.text if destino is not None else 'N/A'}")
            st.write(f"Data de Emissão: {data_emissao.text if data_emissao is not None else 'N/A'}")

            # Exibir gráfico de valores (opcional)
            data = {
                'Descrição': ['Número do CT-e', 'Valor Total', 'Peso Total'],
                'Valor': [
                    numero.text if numero is not None else 'N/A', 
                    valor_total.text if valor_total is not None else '0.00', 
                    peso_total.text if peso_total is not None else '0.00'
                ]
            }
            df = pd.DataFrame(data)
            fig = px.bar(df, x='Descrição', y='Valor', title="Informações do CT-e")
            st.plotly_chart(fig)

        except Exception as e:
            st.error(f"Erro ao processar o XML: {str(e)}")
    else:
        st.warning("Envie um arquivo XML válido.")

elif authentication_status is False:
    st.error("Usuário ou senha incorretos.")
elif authentication_status is None:
    st.warning("Por favor, insira suas credenciais.")