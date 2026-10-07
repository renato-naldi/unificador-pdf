import streamlit as st
from pypdf import PdfWriter, PdfReader
import io

# Configuração da página
st.set_page_config(page_title="Unificador de PDF - Educação", page_icon="📄", layout="centered")

# --- CUSTOMIZAÇÃO: Cabeçalho com Identificação Visual ---
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    # Renderiza um ícone/brasão institucional no topo usando HTML de forma leve
    st.markdown(
        "<div style='font-size: 55px; text-align: center; margin-top: -5px;'>🏛️</div>", 
        unsafe_allow_html=True
    )
with col_titulo:
    st.subheader("Secretaria de Educação de Taubaté")
    st.markdown("<p style='margin-top:-15px; color:gray; font-size:14px;'>Setor de Contratos — Sistema de Unificação</p>", unsafe_allow_html=True)

st.write("---")
st.title("📄 Unificador de PDF Profissional")
st.write("Suba seus documentos, remova páginas indesejadas, ordene e comprima o resultado.")

# --- CUSTOMIZAÇÃO: Rodapé Fixo ---
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f3f5;
        color: #6c757d;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        font-weight: 500;
        border-top: 1px solid #dee2e6;
        z-index: 100;
    }
    .main .block-container {
        padding-bottom: 70px;
    }
    </style>
    <div class="footer">
        Desenvolvido por <strong>Renato Naldi</strong>
    </div>
    """,
    unsafe_allow_html=True
)

# Inicializa as estruturas na sessão se não existirem
if "lista_arquivos" not in st.session_state:
    st.session_state.lista_arquivos = []
if "config_paginas" not in st.session_state:
    st.session_state.config_paginas = {}

# Campo para upload de múltiplos arquivos
arquivos_enviados = st.file_uploader(
    "Escolha os arquivos PDF", 
    type="pdf", 
    accept_multiple_files=True
)

# Sincroniza os uploads com a sessão do Streamlit
if arquivos_enviados:
    nomes_existentes = [arq.name for arq in st.session_state.lista_arquivos]
    for arq in arquivos_enviados:
        if arq.name not in nomes_existentes:
            st.session_state.lista_arquivos.append(arq)
            
    nomes_enviados = [arq.name for arq in arquivos_enviados]
    st.session_state.lista_arquivos = [arq for arq in st.session_state.lista_arquivos if arq.name in nomes_enviados]

# Exibe as ferramentas se houver arquivos carregados
if st.session_state.lista_arquivos:
    lista = st.session_state.lista_arquivos
    tamanho = len(lista)
    
    st.subheader("🔄 1. Organizar Sequência e Filtro de Páginas")
    st.info("Ajuste a ordem pelas setas. Se precisar remover páginas, digite o intervalo desejado no campo correspondente.")
    
    for i in range(tamanho):
        arq_atual = lista[i]
        
        # Lê a quantidade total de páginas do arquivo original para orientar o usuário
        try:
            reader = PdfReader(io.BytesIO(arq_atual.getvalue()))
            total_paginas = len(reader.pages)
        except:
            total_paginas = 0

        # Cria uma caixa visual para cada arquivo
        with st.container(border=True):
            col_nome, col_paginas, col_subir, col_descer = st.columns([4, 3, 1, 1])
            
            with col_nome:
                st.write(f"**{i+1}.** `{arq_atual.name}`")
                st.caption(f"Tamanho total original: {total_paginas} página(s)")
                
            with col_paginas:
                # Input para filtrar as páginas (Ex: "1-5", "1,3,5" ou vazio para tudo)
                chave_pag = f"paginas_{arq_atual.name}_{i}"
                intervalo = st.text_input(
                    "Páginas a manter (Ex: 1-3, 5):", 
                    value="", 
                    placeholder="Deixe vazio para todas",
                    key=chave_pag
                )
                st.session_state.config_paginas[arq_atual.name] = intervalo
                
            with col_subir:
                if st.button("⬆️", key=f"subir_{i}", disabled=(i == 0)):
                    lista[i], lista[i-1] = lista[i-1], lista[i]
                    st.rerun()
                    
            with col_descer:
                if st.button("⬇️", key=f"descer_{i}", disabled=(i == tamanho - 1)):
                    lista[i], lista[i+1] = lista[i+1], lista[i]
                    st.rerun()

    st.subheader("⚙️ 2. Opções de Saída")
    comprimir = st.checkbox("⚙️ Ativar compactação de tamanho do PDF final (Reduz o peso do arquivo)", value=True)

    st.write("---")
    
    # Processamento da Unificação Avançada
    if st.button("Executar Unificação e Aplicar Filtros", type="primary"):
        if len(lista) < 2:
            st.error("Por favor, selecione pelo menos 2 arquivos PDF para combinar.")
        else:
            with st.spinner("Processando, filtrando e compactando seus documentos..."):
                try:
                    merger = PdfWriter()
                    
                    for arquivo_pdf in lista:
                        # Lê o arquivo da memória
                        pdf_bytes = arquivo_pdf.getvalue()
                        reader = PdfReader(io.BytesIO(pdf_bytes))
                        total_pags = len(reader.pages)
                        
                        filtro = st.session_state.config_paginas.get(arquivo_pdf.name, "").strip()
                        
                        # Se houver um filtro de páginas configurado
                        if filtro:
                            paginas_a_incluir = []
                            # Interpreta formatos como "1-3, 5"
                            partes = filtro.split(',')
                            for parte in partes:
                                if '-' in parte:
                                    inicio, fim = parte.split('-')
                                    idx_inicio = max(0, int(inicio.strip()) - 1)
                                    idx_fim = min(total_pags, int(fim.strip()))
                                    paginas_a_incluir.extend(range(idx_inicio, idx_fim))
                                else:
                                    if parte.strip().isdigit():
                                        idx = int(parte.strip()) - 1
                                        if 0 <= idx < total_pags:
                                            paginas_a_incluir.append(idx)
                            
                            # Adiciona ao merger apenas as páginas filtradas
                            for pag_idx in paginas_a_incluir:
                                merger.add_page(reader.pages[pag_idx])
                        else:
                            # Caso contrário, adiciona o documento inteiro
                            merger.append(reader)
                    
                    # Aplica a compressão se marcada pelo usuário
                    if comprimir:
                        # Percorre as páginas injetadas no escritor e comprime os fluxos de dados internos
                        for page in merger.pages:
                            page.compress_content_streams()

                    output_pdf = io.BytesIO()
                    merger.write(output_pdf)
                    merger.close()
                    
                    st.success("Processo concluído com sucesso!")
                    
                    st.download_button(
                        label="📥 Baixar PDF Final Formatado",
                        data=output_pdf.getvalue(),
                        file_name="contrato_unificado_final.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Erro ao processar as regras de páginas ou unificação: {e}. Certifique-se de digitar os intervalos corretamente (ex: 1-5).")
