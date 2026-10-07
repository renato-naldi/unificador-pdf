import streamlit as st
from pypdf import PdfWriter
import io

# Configuração da página
st.set_page_config(page_title="Unificador de PDF", page_icon="📄", layout="centered")

st.title("📄 Unificar Arquivos PDF")
st.write("Arraste seus arquivos abaixo e utilize as setas para ajustar a ordem final.")

# Inicializa a lista de arquivos na sessão do Streamlit se ela não existir
if "lista_arquivos" not in st.session_state:
    st.session_state.lista_arquivos = []

# Campo para upload de múltiplos arquivos
arquivos_enviados = st.file_uploader(
    "Escolha os arquivos PDF", 
    type="pdf", 
    accept_multiple_files=True
)

# Atualiza a lista da sessão quando novos arquivos são carregados
if arquivos_enviados:
    # Cria uma lista com os arquivos mantendo o estado anterior se eles já existirem
    nomes_existentes = [arq.name for arq in st.session_state.lista_arquivos]
    for arq in arquivos_enviados:
        if arq.name not in nomes_existentes:
            st.session_state.lista_arquivos.append(arq)
            
    # Remove arquivos da sessão caso o usuário limpe do uploader
    nomes_enviados = [arq.name for arq in arquivos_enviados]
    st.session_state.lista_arquivos = [arq for arq in st.session_state.lista_arquivos if arq.name in nomes_enviados]

if st.session_state.lista_arquivos:
    st.subheader("🔄 Organizar Sequência dos Documentos")
    st.info("Clique nos botões de seta para mover a ordem dos arquivos para cima ou para baixo.")
    
    # Renderiza a lista de arquivos com botões de ordenação
    lista = st.session_state.lista_arquivos
    tamanho = len(lista)
    
    for i in range(tamanho):
        # Cria colunas para alinhar o nome do arquivo e os botões de ação
        col_nome, col_subir, col_descer = st.columns([7, 1, 1])
        
        with col_nome:
            st.write(f"**{i+1}.** {lista[i].name}")
            
        with col_subir:
            # Desabilita o botão subir se for o primeiro arquivo da lista
            if st.button("⬆️", key=f"subir_{i}", disabled=(i == 0)):
                lista[i], lista[i-1] = lista[i-1], lista[i]
                st.rerun()
                
        with col_descer:
            # Desabilita o botão descer se for o último arquivo da lista
            if st.button("⬇️", key=f"descer_{i}", disabled=(i == tamanho - 1)):
                lista[i], lista[i+1] = lista[i+1], lista[i]
                st.rerun()

    st.write("---")
    
    # Botão para processar a unificação
    if st.button("Combinar PDFs na Ordem Acima", type="primary"):
        if len(lista) < 2:
            st.error("Por favor, selecione pelo menos 2 arquivos PDF.")
        else:
            with st.spinner("Mesclando documentos..."):
                try:
                    merger = PdfWriter()
                    
                    # Junta seguindo exatamente a ordem atualizada da lista na sessão
                    for arquivo_pdf in lista:
                        merger.append(arquivo_pdf)
                    
                    output_pdf = io.BytesIO()
                    merger.write(output_pdf)
                    merger.close()
                    
                    st.success("PDFs unificados com sucesso!")
                    
                    st.download_button(
                        label="📥 Baixar PDF Unificado",
                        data=output_pdf.getvalue(),
                        file_name="pdf_unificado_final.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Ocorreu um erro no processamento: {e}")
