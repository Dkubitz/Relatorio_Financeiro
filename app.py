"""
Dashboard Financeiro Interativo
Aplicação principal usando Streamlit para visualização de dados financeiros

Arquitetura: Clean Architecture com Separation of Concerns
- Apresentação: Streamlit (este arquivo)
- Domínio: DataProcessor (src/data_processor.py)
- Visualização: Visualizations (src/visualizations.py)
- Utilitários: utils (src/utils.py)
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from pathlib import Path
import plotly.graph_objects as go
import io

from src.data_processor import DataProcessor
from src.visualizations import Visualizations
from src.utils import formatar_moeda, formatar_percentual, criar_periodo_legivel

# Configuração da página
st.set_page_config(
    page_title="Dashboard Financeiro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado para melhorar a aparência COM ANIMAÇÕES E SUPORTE A TEMA ESCURO/CLARO
st.markdown("""
<style>
    /* Header - Adaptável ao tema usando cores que funcionam bem em ambos */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        animation: fadeInDown 0.8s ease-out;
        /* Cor será herdada do Streamlit - funciona em ambos os temas */
    }
    .sub-header {
        font-size: 1.1rem;
        margin-bottom: 2rem;
        animation: fadeIn 1s ease-out;
        opacity: 0.85;
        /* Cor será herdada do Streamlit - funciona em ambos os temas */
    }
    
    /* Garantir que elementos customizados herdem cor do tema */
    .main-header, .sub-header {
        color: inherit;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.5rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        animation: slideInUp 0.6s ease-out;
    }
    
    /* ANIMAÇÕES NOS MÉTRICAS - Remove background fixo para usar tema do Streamlit */
    .stMetric {
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
        animation: slideInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 10px 20px rgba(0,0,0,0.15);
    }
    
    /* Animação para os números das métricas - Remove cor fixa para usar tema */
    [data-testid="stMetricValue"] {
        animation: countUp 1.2s cubic-bezier(0.16, 1, 0.3, 1);
        font-weight: 700;
        /* Remove cor fixa - Streamlit ajusta automaticamente */
    }
    
    /* Animação para os labels das métricas - Remove cor fixa para usar tema */
    [data-testid="stMetricLabel"] {
        animation: fadeIn 0.8s ease-out;
        font-weight: 600;
        /* Remove cor fixa - Streamlit ajusta automaticamente */
    }
    
    /* Animação para delta - Mantém cores originais do Streamlit */
    [data-testid="stMetricDelta"] {
        animation: bounceIn 1s ease-out;
    }
    
    /* Keyframes */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes countUp {
        from {
            opacity: 0;
            transform: scale(0.5);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    @keyframes bounceIn {
        0% {
            opacity: 0;
            transform: scale(0.3);
        }
        50% {
            opacity: 1;
            transform: scale(1.05);
        }
        70% {
            transform: scale(0.9);
        }
        100% {
            transform: scale(1);
        }
    }
    
    /* Animação suave para gráficos */
    .js-plotly-plot {
        animation: fadeIn 0.8s ease-out;
    }
    
    /* Animação para dataframes */
    [data-testid="stDataFrame"] {
        animation: slideInUp 0.6s ease-out;
    }
    
    /* Animação para info boxes */
    .stAlert {
        animation: slideInRight 0.5s ease-out;
    }
    
    /* Remover cores fixas de texto - deixa Streamlit usar tema padrão */
    /* Streamlit já ajusta automaticamente as cores baseado no tema selecionado */
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def carregar_dados():
    """
    Carrega dados do arquivo CSV
    Cache para melhor performance
    
    Returns:
        DataProcessor: Processador de dados inicializado ou None em caso de erro
    """
    # Caminho do arquivo CSV
    arquivo_csv = Path("Fluxo Financeiro.csv")
    
    if not arquivo_csv.exists():
        return None
    
    try:
        # Leitura do CSV com configurações específicas
        # O arquivo já tem as colunas com prefixo "Content."
        df = pd.read_csv(
            arquivo_csv,
            sep=';',
            encoding='utf-8',
            usecols=[
                'Content.Data',
                'Content.Grupo', 
                'Content.Subgrupo',
                'Content.Natureza',
                'Content.FORNECEDOR',
                'Content.Entrada (R$)',
                'Content.Saída (R$)',
                'Name'  # Conta bancária
            ]
        )
        
        # Inicializar processador (já com nomes corretos)
        processor = DataProcessor(df)
        
        return processor
        
    except Exception as e:
        import traceback
        st.error(f"❌ Erro ao carregar arquivo: {str(e)}")
        st.code(traceback.format_exc())
        return None


def renderizar_kpis(kpis: dict):
    """
    Renderiza cards de KPIs principais
    
    Args:
        kpis: Dicionário com KPIs calculados
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 Total de Entradas",
            value=formatar_moeda(kpis['total_entrada']),
            delta=None
        )
    
    with col2:
        st.metric(
            label="💸 Total de Saídas",
            value=formatar_moeda(kpis['total_saida']),
            delta=None
        )
    
    with col3:
        variacao_delta = f"{kpis['variacao_percentual']:+.1f}%" if kpis['variacao_percentual'] != 0 else None
        st.metric(
            label="📈 Saldo Líquido",
            value=formatar_moeda(kpis['saldo']),
            delta=variacao_delta
        )
    
    with col4:
        st.metric(
            label="📊 Transações",
            value=f"{kpis['num_transacoes']:,}".replace(',', '.'),
            delta=None
        )


def renderizar_composicao_kpis(df: pd.DataFrame):
    """
    Renderiza composição detalhada dos KPIs
    Mostra de onde vêm os valores de entradas e saídas
    
    Args:
        df: DataFrame filtrado
    """
    with st.expander("🔍 Ver composição detalhada dos valores", expanded=False):
        col1, col2 = st.columns(2)
        
        # ENTRADAS
        with col1:
            st.markdown("### 💰 Composição das Entradas")
            
            # Agregar por Grupo → Subgrupo → Natureza (mostra TODAS, não só top 10)
            df_entradas = df[df['Entrada'] > 0].groupby(['Grupo', 'Subgrupo', 'Natureza'])['Entrada'].sum().reset_index()
            df_entradas = df_entradas.sort_values('Entrada', ascending=False)
            
            total_entradas = df['Entrada'].sum()
            
            if len(df_entradas) > 0:
                # Container com scroll para entradas
                with st.container(height=500):
                    for _, row in df_entradas.iterrows():
                        percentual = (row['Entrada'] / total_entradas * 100) if total_entradas > 0 else 0
                        st.markdown(
                            f"**{row['Grupo']}** → {row['Subgrupo']} → {row['Natureza'][:40]}  \n"
                            f"`{formatar_moeda(row['Entrada'])}` ({percentual:.1f}%)"
                        )
            else:
                st.info("Nenhuma entrada no período filtrado")
        
        # SAÍDAS
        with col2:
            st.markdown("### 💸 Composição das Saídas")
            
            # Agregar por Grupo → Subgrupo → Natureza (mostra TODAS, não só top 10)
            df_saidas = df[df['Saida'] < 0].groupby(['Grupo', 'Subgrupo', 'Natureza'])['Saida'].sum().reset_index()
            df_saidas['Saida_Abs'] = df_saidas['Saida'].abs()
            df_saidas = df_saidas.sort_values('Saida_Abs', ascending=False)
            
            total_saidas = abs(df['Saida'].sum())
            
            if len(df_saidas) > 0:
                # Container com scroll para saídas
                with st.container(height=500):
                    for _, row in df_saidas.iterrows():
                        percentual = (row['Saida_Abs'] / total_saidas * 100) if total_saidas > 0 else 0
                        st.markdown(
                            f"**{row['Grupo']}** → {row['Subgrupo']} → {row['Natureza'][:40]}  \n"
                            f"`{formatar_moeda(row['Saida_Abs'])}` ({percentual:.1f}%)"
                        )
            else:
                st.info("Nenhuma saída no período filtrado")


def renderizar_filtros(processor: DataProcessor):
    """
    Renderiza sidebar com filtros
    
    Args:
        processor: DataProcessor com dados
        
    Returns:
        dict: Dicionário com filtros selecionados
    """
    st.sidebar.header("🔍 Filtros")
    
    # Período
    data_min, data_max = processor.obter_periodos_disponiveis()
    
    st.sidebar.subheader("📅 Período")
    data_inicio = st.sidebar.date_input(
        "Data Inicial",
        value=data_min,
        min_value=data_min,
        max_value=data_max
    )
    data_fim = st.sidebar.date_input(
        "Data Final",
        value=data_max,
        min_value=data_min,
        max_value=data_max
    )
    
    # Grupos
    st.sidebar.subheader("🏢 Grupos/Projetos")
    grupos_disponiveis = processor.obter_valores_unicos('Grupo')
    grupos_selecionados = st.sidebar.multiselect(
        "Selecione grupos",
        options=grupos_disponiveis,
        default=[]
    )
    
    # Fornecedores
    st.sidebar.subheader("🏪 Fornecedores")
    fornecedores_disponiveis = processor.obter_valores_unicos('FORNECEDOR')
    fornecedores_selecionados = st.sidebar.multiselect(
        "Selecione fornecedores",
        options=fornecedores_disponiveis,
        default=[]
    )
    
    # Naturezas
    st.sidebar.subheader("📑 Naturezas")
    naturezas_disponiveis = processor.obter_valores_unicos('Natureza')
    naturezas_selecionadas = st.sidebar.multiselect(
        "Selecione naturezas",
        options=naturezas_disponiveis,
        default=[]
    )
    
    return {
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'grupos': grupos_selecionados if grupos_selecionados else None,
        'fornecedores': fornecedores_selecionados if fornecedores_selecionados else None,
        'naturezas': naturezas_selecionadas if naturezas_selecionadas else None
    }


def main():
    """
    Função principal da aplicação
    """
    # Header
    st.markdown('<p class="main-header">Dashboard Financeiro</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Análise completa de fluxo de caixa, despesas e receitas</p>', unsafe_allow_html=True)
    
    # Carregar dados
    with st.spinner("Carregando dados..."):
        processor = carregar_dados()
    
    # Verificar se carregamento foi bem sucedido
    if processor is None:
        st.error("❌ Não foi possível carregar os dados.")
        st.info("📁 Certifique-se de que o arquivo 'Fluxo Financeiro.csv' está no diretório do projeto.")
        st.code(f"Caminho esperado: {Path('Fluxo Financeiro.csv').absolute()}")
        st.stop()
    
    # Renderizar filtros
    filtros = renderizar_filtros(processor)
    
    # ==============================================================================
    # ARQUITETURA DE VISÕES INTELIGENTES
    # ==============================================================================
    # As abas usam automaticamente a visão correta:
    # - VISÃO OPERACIONAL: Evolução Temporal, Grupos, Categoria, Natureza, Fornecedores
    #   (exclui transferências internas que inflam artificialmente os valores)
    # - VISÃO COMPLETA: Análise Financeira e Contas Bancárias
    #   (inclui todas as transações para controle de caixa e auditoria)
    # ==============================================================================
    
    # Aplicar filtros na visão operacional (base para maioria das análises)
    df_operacional_filtrado = processor.obter_df_filtrado(
        data_inicio=filtros['data_inicio'],
        data_fim=filtros['data_fim'],
        grupos=filtros['grupos'],
        fornecedores=filtros['fornecedores'],
        naturezas=filtros['naturezas']
    )
    
    # Remover transações FINANCEIRO_INTERNO da visão operacional
    df_operacional_filtrado = df_operacional_filtrado[
        df_operacional_filtrado['TipoTransacao'] != 'FINANCEIRO_INTERNO'
    ].copy()
    
    # Aplicar filtros na visão completa (para análises financeiras e contas)
    df_completo_filtrado = processor.obter_df_filtrado(
        data_inicio=filtros['data_inicio'],
        data_fim=filtros['data_fim'],
        grupos=filtros['grupos'],
        fornecedores=filtros['fornecedores'],
        naturezas=filtros['naturezas']
    )
    
    # Indicador visual inteligente na sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 Sistema de Visões Inteligentes")
    st.sidebar.info(
        "✅ **Visão Operacional** (padrão)\n"
        "→ Análises sem transferências internas\n\n"
        "🔍 **Visão Completa** (automática)\n"
        "→ Abas Financeira e Contas\n"
        "→ Inclui todas as movimentações"
    )
    
    # Estatísticas das visões
    total_transacoes = len(df_completo_filtrado)
    transacoes_internas = len(df_completo_filtrado[df_completo_filtrado['TipoTransacao'] == 'FINANCEIRO_INTERNO'])
    transacoes_operacionais = len(df_operacional_filtrado)
    
    st.sidebar.markdown(f"""
    **📊 Estatísticas:**
    - Total de transações: {total_transacoes:,}
    - Operacionais: {transacoes_operacionais:,}
    - Internas (filtradas): {transacoes_internas:,}
    """.replace(',', '.'))
    
    # Verificar se há dados
    if len(df_operacional_filtrado) == 0 and len(df_completo_filtrado) == 0:
        st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados.")
        return
    
    # ============================================================================
    # KPIs PRINCIPAIS - SEMPRE VISÍVEIS NO TOPO
    # ============================================================================
    
    # Informação do período (usando visão operacional como padrão)
    periodo_info = criar_periodo_legivel(
        df_operacional_filtrado['Data'].min(),
        df_operacional_filtrado['Data'].max()
    )
    st.info(f"📅 Período analisado: **{periodo_info}** | 📊 {len(df_operacional_filtrado):,} transações operacionais".replace(',', '.'))
    
    # KPIs principais fixos no topo - APENAS SE HOUVER FILTRO DE GRUPOS ATIVO
    tem_filtro_grupos = filtros['grupos'] is not None and len(filtros['grupos']) > 0
    
    if tem_filtro_grupos:
        st.markdown("---")
        kpis = processor.calcular_kpis(df_operacional_filtrado)
        
        # Criar container com background destacado para os KPIs
        with st.container():
            st.markdown("### 📊 Resumo Executivo")
            renderizar_kpis(kpis)
            
            # Composição detalhada dos KPIs (visão operacional)
            renderizar_composicao_kpis(df_operacional_filtrado)
        
        st.markdown("---")
    
    # ============================================================================
    # NAVEGAÇÃO POR ABAS
    # ============================================================================
    
    # Abas de visualizações
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "💳 Contas Bancárias",
        "📈 Evolução Temporal",
        "🏢 Análise por Grupo",
        "📑 Análise por Categoria",
        "🔍 Análise por Natureza",
        "🏪 Fornecedores",
        "💰 Análise Financeira",
        "📋 Dados Detalhados"
    ])
    
    with tab1:
        st.success("🔍 **Visão Completa** - Inclui TODAS as movimentações (inclusive transferências) para controle de caixa por conta")
        st.subheader("💳 Saldo por Conta Bancária")
        
        # Calcular saldos por conta (usando visão completa com todas as transações)
        saldos_contas = processor.calcular_saldos_por_conta(df_completo_filtrado)
        
        if saldos_contas:
            # KPIs de Contas Consolidadas
            st.markdown("### 🏦 Saldos Consolidados (Caixa Real)")
            
            col1, col2, col3, col4 = st.columns(4)
            
            consolidados = saldos_contas['consolidados']
            
            with col1:
                st.metric(
                    "💼 RITHMO",
                    formatar_moeda(consolidados['RITHMO']),
                    help="Soma de Lifecon5 + Lifecon7"
                )
            
            with col2:
                st.metric(
                    "💎 ÁGATA",
                    formatar_moeda(consolidados['ÁGATA'])
                )
            
            with col3:
                st.metric(
                    "🏔️ BARILOCHE",
                    formatar_moeda(consolidados['BARILOCHE'])
                )
            
            with col4:
                st.metric(
                    "💰 TOTAL",
                    formatar_moeda(saldos_contas['total'])
                )
            
            st.markdown("---")
            
            # Detalhamento por conta individual
            st.markdown("### 🏦 Detalhamento por Conta Individual")
            
            por_conta = saldos_contas['por_conta']
            
            # Criar DataFrame para exibição
            dados_contas = []
            for conta, info in por_conta.items():
                # Remover prefixo "Fluxo" e formatar nome
                nome_conta = conta.replace('Fluxo', '')
                dados_contas.append({
                    'Conta': nome_conta,
                    'Saldo': info['saldo'],
                    'Entradas': info['entradas'],
                    'Saídas': info['saidas'],
                    'Transações': info['transacoes']
                })
            
            df_contas = pd.DataFrame(dados_contas).sort_values('Saldo', ascending=False)
            
            # Formatar para exibição
            df_contas_display = df_contas.copy()
            df_contas_display['Saldo'] = df_contas_display['Saldo'].apply(formatar_moeda)
            df_contas_display['Entradas'] = df_contas_display['Entradas'].apply(formatar_moeda)
            df_contas_display['Saídas'] = df_contas_display['Saídas'].apply(formatar_moeda)
            
            st.dataframe(
                df_contas_display,
                hide_index=True,
                use_container_width=True,
                height=250
            )
            
            # Gráfico de barras
            st.markdown("---")
            st.markdown("### 📊 Comparativo de Saldos")
            
            fig_contas = go.Figure()
            
            # Cores personalizadas
            cores = {
                'Lifecon5': '#3B82F6',
                'Lifecon7': '#60A5FA', 
                'Agata': '#8B5CF6',
                'Bariloche': '#EC4899'
            }
            
            for _, row in df_contas.iterrows():
                cor = cores.get(row['Conta'], '#6B7280')
                fig_contas.add_trace(
                    go.Bar(
                        name=row['Conta'],
                        x=[row['Conta']],
                        y=[row['Saldo']],
                        text=[formatar_moeda(row['Saldo'])],
                        textposition='outside',
                        marker_color=cor,
                        hovertemplate='<b>%{x}</b><br>Saldo: %{text}<extra></extra>'
                    )
                )
            
            fig_contas.update_layout(
                title='Saldo em Cada Conta Bancária',
                template='plotly_white',
                height=600,
                width=800,
                showlegend=False,
                xaxis_title='Conta',
                yaxis_title='Saldo (R$)',
                bargap=0.3  # Espaçamento entre barras para deixá-las mais esbeltas
            )
            
            # Centralizar o gráfico com largura controlada
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.plotly_chart(fig_contas, use_container_width=False)
            
            # Informação adicional
            st.info("💡 **Nota:** Estes são os saldos reais das contas bancárias, diferentes da análise por GRUPO (que classifica despesas por projeto).")
        else:
            st.warning("⚠️ Não foi possível calcular saldos por conta bancária.")
    
    with tab2:
        st.info("🎯 **Visão Operacional** - Análise sem transferências internas")
        st.subheader("Evolução Temporal do Fluxo de Caixa")
        df_temporal = processor.agregacao_temporal(df_operacional_filtrado, freq='ME')
        fig_temporal = Visualizations.criar_grafico_evolucao_temporal(df_temporal)
        st.plotly_chart(fig_temporal, use_container_width=True)
        
        st.subheader("Comparativo Mensal")
        fig_comparativo = Visualizations.criar_grafico_comparativo_mensal(df_operacional_filtrado)
        st.plotly_chart(fig_comparativo, use_container_width=True)
    
    with tab3:
        st.info("🎯 **Visão Operacional** - Análise sem transferências internas")
        st.subheader("Distribuição por Grupo/Projeto")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            df_grupo = processor.agregacao_por_grupo(df_operacional_filtrado)
            fig_grupo = Visualizations.criar_grafico_por_grupo(df_grupo, top_n=10)
            st.plotly_chart(fig_grupo, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Resumo por Grupo")
            df_grupo_display = df_grupo.head(10).copy()
            df_grupo_display['Saídas'] = df_grupo_display['Saida'].apply(lambda x: formatar_moeda(abs(x)))
            df_grupo_display['Entradas'] = df_grupo_display['Entrada'].apply(formatar_moeda)
            st.dataframe(
                df_grupo_display[['Grupo', 'Entradas', 'Saídas']],
                hide_index=True,
                use_container_width=True
            )
    
    with tab4:
        st.info("🎯 **Visão Operacional** - Análise sem transferências internas")
        st.subheader("Distribuição por Categoria/Natureza")
        
        # Interface interativa dividida: Despesas | Receitas
        col_despesas, col_receitas = st.columns(2)
        
        # ==================== COLUNA DESPESAS ====================
        with col_despesas:
            st.markdown("### 💸 Despesas por Natureza")
            
            # Obter grupos e subgrupos disponíveis para despesas
            df_despesas = df_operacional_filtrado[df_operacional_filtrado['Saida'] < 0].copy()
            grupos_despesas = sorted(df_despesas['Grupo'].unique().tolist())
            
            if len(grupos_despesas) > 0:
                grupo_desp_selecionado = st.selectbox(
                    "Selecione o Grupo",
                    options=grupos_despesas,
                    key='grupo_despesas'
                )
                
                # Filtrar subgrupos deste grupo
                subgrupos_despesas = sorted(
                    df_despesas[df_despesas['Grupo'] == grupo_desp_selecionado]['Subgrupo'].unique().tolist()
                )
                
                if len(subgrupos_despesas) > 0:
                    subgrupo_desp_selecionado = st.selectbox(
                        "Selecione o Subgrupo",
                        options=subgrupos_despesas,
                        key='subgrupo_despesas'
                    )
                    
                    # Calcular total de despesas desta combinação
                    df_filtrado_desp = df_operacional_filtrado[
                        (df_operacional_filtrado['Grupo'] == grupo_desp_selecionado) &
                        (df_operacional_filtrado['Subgrupo'] == subgrupo_desp_selecionado)
                    ]
                    total_despesas = abs(df_filtrado_desp['Saida'].sum())
                    
                    # Mostrar total
                    st.metric(
                        label="💸 Total de Despesas",
                        value=formatar_moeda(total_despesas)
                    )
                    
                    # Gerar e exibir gráfico
                    fig_despesas = Visualizations.criar_grafico_despesas_por_natureza(
                        df_operacional_filtrado,
                        grupo_desp_selecionado,
                        subgrupo_desp_selecionado
                    )
                    st.plotly_chart(fig_despesas, use_container_width=True)
                else:
                    st.warning("Nenhum subgrupo disponível para este grupo")
            else:
                st.warning("Nenhuma despesa disponível no período filtrado")
        
        # ==================== COLUNA RECEITAS ====================
        with col_receitas:
            st.markdown("### 💰 Receitas por Natureza")
            
            # Obter grupos e subgrupos disponíveis para receitas
            df_receitas = df_operacional_filtrado[df_operacional_filtrado['Entrada'] > 0].copy()
            grupos_receitas = sorted(df_receitas['Grupo'].unique().tolist())
            
            if len(grupos_receitas) > 0:
                grupo_rec_selecionado = st.selectbox(
                    "Selecione o Grupo",
                    options=grupos_receitas,
                    key='grupo_receitas'
                )
                
                # Filtrar subgrupos deste grupo
                subgrupos_receitas = sorted(
                    df_receitas[df_receitas['Grupo'] == grupo_rec_selecionado]['Subgrupo'].unique().tolist()
                )
                
                if len(subgrupos_receitas) > 0:
                    subgrupo_rec_selecionado = st.selectbox(
                        "Selecione o Subgrupo",
                        options=subgrupos_receitas,
                        key='subgrupo_receitas'
                    )
                    
                    # Calcular total de receitas desta combinação
                    df_filtrado_rec = df_operacional_filtrado[
                        (df_operacional_filtrado['Grupo'] == grupo_rec_selecionado) &
                        (df_operacional_filtrado['Subgrupo'] == subgrupo_rec_selecionado)
                    ]
                    total_receitas = df_filtrado_rec['Entrada'].sum()
                    
                    # Mostrar total
                    st.metric(
                        label="💰 Total de Receitas",
                        value=formatar_moeda(total_receitas)
                    )
                    
                    # Gerar e exibir gráfico
                    fig_receitas = Visualizations.criar_grafico_receitas_por_natureza(
                        df_operacional_filtrado,
                        grupo_rec_selecionado,
                        subgrupo_rec_selecionado
                    )
                    st.plotly_chart(fig_receitas, use_container_width=True)
                else:
                    st.warning("Nenhum subgrupo disponível para este grupo")
            else:
                st.warning("Nenhuma receita disponível no período filtrado")
    
    with tab5:
        st.info("🎯 **Visão Operacional** - Análise sem transferências internas")
        st.subheader("🔍 Análise Detalhada por Natureza")
        
        # Seletor de grupo para análise detalhada
        col1, col2 = st.columns([1, 3])
        
        with col1:
            grupos_disponiveis = ['TODOS'] + processor.obter_valores_unicos('Grupo')
            grupo_selecionado = st.selectbox(
                "Selecione o Grupo",
                options=grupos_disponiveis,
                index=0
            )
        
        # Filtrar dados por grupo se selecionado (usando visão operacional)
        if grupo_selecionado == 'TODOS':
            df_analise = df_operacional_filtrado.copy()
        else:
            df_analise = df_operacional_filtrado[df_operacional_filtrado['Grupo'] == grupo_selecionado].copy()
        
        if len(df_analise) > 0:
            # Agregação por Subgrupo e Natureza
            df_natureza_detalhado = df_analise.groupby(['Grupo', 'Subgrupo', 'Natureza']).agg({
                'Entrada': 'sum',
                'Saida': 'sum',
                'Saldo': 'sum'
            }).reset_index()
            
            df_natureza_detalhado['Saida_Abs'] = df_natureza_detalhado['Saida'].abs()
            df_natureza_detalhado = df_natureza_detalhado.sort_values(['Grupo', 'Subgrupo', 'Saida_Abs'], ascending=[True, True, False])
            
            # Resumo por Subgrupo
            st.markdown("### 📊 Resumo por Subgrupo")
            df_subgrupo_resumo = df_analise.groupby(['Grupo', 'Subgrupo']).agg({
                'Entrada': 'sum',
                'Saida': 'sum',
                'Saldo': 'sum'
            }).reset_index()
            
            df_subgrupo_resumo['Saida_Abs'] = df_subgrupo_resumo['Saida'].abs()
            df_subgrupo_resumo = df_subgrupo_resumo.sort_values(['Grupo', 'Saida_Abs'], ascending=[True, False])
            
            # Gráfico de barras por subgrupo
            fig_subgrupo = go.Figure()
            
            for grupo in df_subgrupo_resumo['Grupo'].unique():
                df_grupo_temp = df_subgrupo_resumo[df_subgrupo_resumo['Grupo'] == grupo]
                fig_subgrupo.add_trace(
                    go.Bar(
                        name=grupo,
                        x=df_grupo_temp['Subgrupo'],
                        y=df_grupo_temp['Saida_Abs'],
                        text=df_grupo_temp['Saida_Abs'].apply(lambda x: f'R$ {x:,.0f}'),
                        textposition='outside',
                        hovertemplate='<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>'
                    )
                )
            
            fig_subgrupo.update_layout(
                title='Comparativo de Saídas por Subgrupo e Grupo',
                template='plotly_white',
                height=500,
                xaxis_title='Subgrupo',
                yaxis_title='Valor (R$)',
                barmode='group',
                showlegend=True,
                bargap=0.15,
                bargroupgap=0.1,
                xaxis=dict(
                    categoryorder='array',
                    categoryarray=['CUSTO DO ATIVO', 'ADMINISTRAÇÃO', 'FINANCEIRO', 'RECEITA DO ATIVO']
                )
            )
            
            # Fixar largura das barras
            fig_subgrupo.update_traces(width=0.3)
            
            st.plotly_chart(fig_subgrupo, use_container_width=True)
            
            # Tabela detalhada estilo Excel
            st.markdown("---")
            st.markdown("### 📋 Detalhamento por Grupo, Subgrupo e Natureza")
            
            # Criar tabela formatada
            for grupo in df_natureza_detalhado['Grupo'].unique():
                with st.expander(f"**{grupo}**", expanded=(grupo_selecionado != 'TODOS')):
                    df_grupo = df_natureza_detalhado[df_natureza_detalhado['Grupo'] == grupo].copy()
                    
                    # Criar tabela pivotada
                    tabela_display = []
                    
                    for subgrupo in df_grupo['Subgrupo'].unique():
                        df_sub = df_grupo[df_grupo['Subgrupo'] == subgrupo]
                        
                        # Linha de cabeçalho do subgrupo
                        total_entrada = df_sub['Entrada'].sum()
                        total_saida = df_sub['Saida'].sum()
                        total_saldo = df_sub['Saldo'].sum()
                        
                        tabela_display.append({
                            'Subgrupo/Natureza': f"🔵 {subgrupo}",
                            'Entradas': formatar_moeda(total_entrada),
                            'Saídas': formatar_moeda(abs(total_saida)),
                            'Saldo': formatar_moeda(total_saldo)
                        })
                        
                        # Linhas de natureza
                        for _, row in df_sub.iterrows():
                            tabela_display.append({
                                'Subgrupo/Natureza': f"    ↳ {row['Natureza']}",
                                'Entradas': formatar_moeda(row['Entrada']),
                                'Saídas': formatar_moeda(abs(row['Saida'])),
                                'Saldo': formatar_moeda(row['Saldo'])
                            })
                    
                    # Total do grupo
                    total_grupo_entrada = df_grupo['Entrada'].sum()
                    total_grupo_saida = df_grupo['Saida'].sum()
                    total_grupo_saldo = df_grupo['Saldo'].sum()
                    
                    tabela_display.append({
                        'Subgrupo/Natureza': f"**TOTAL {grupo}**",
                        'Entradas': f"**{formatar_moeda(total_grupo_entrada)}**",
                        'Saídas': f"**{formatar_moeda(abs(total_grupo_saida))}**",
                        'Saldo': f"**{formatar_moeda(total_grupo_saldo)}**"
                    })
                    
                    df_display = pd.DataFrame(tabela_display)
                    st.dataframe(
                        df_display,
                        hide_index=True,
                        use_container_width=True,
                        height=min(600, len(tabela_display) * 35 + 50)
                    )
            
            # Opção de download
            st.markdown("---")
            st.markdown("### 📥 Exportar Análise Detalhada")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Preparar dados para exportação
                df_export = df_natureza_detalhado.copy()
                df_export['Entradas'] = df_export['Entrada'].apply(lambda x: f"{x:.2f}".replace('.', ','))
                df_export['Saídas'] = df_export['Saida'].apply(lambda x: f"{abs(x):.2f}".replace('.', ','))
                df_export['Saldo'] = df_export['Saldo'].apply(lambda x: f"{x:.2f}".replace('.', ','))
                
                csv_natureza = df_export[['Grupo', 'Subgrupo', 'Natureza', 'Entradas', 'Saídas', 'Saldo']].to_csv(
                    index=False, 
                    encoding='utf-8-sig', 
                    sep=';'
                )
                
                st.download_button(
                    label="📥 Baixar Análise por Natureza (CSV)",
                    data=csv_natureza,
                    file_name=f"analise_natureza_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        else:
            st.warning("⚠️ Nenhum dado encontrado para o grupo selecionado.")
    
    with tab6:
        st.info("🎯 **Visão Operacional** - Análise sem transferências internas")
        st.subheader("Análise de Fornecedores")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            df_fornecedores = processor.top_fornecedores(df_operacional_filtrado, n=15, tipo='saida')
            fig_fornecedores = Visualizations.criar_grafico_fornecedores(df_fornecedores, top_n=15)
            st.plotly_chart(fig_fornecedores, use_container_width=True)
        
        with col2:
            st.markdown("### 🏆 Top 15 Fornecedores")
            df_forn_display = df_fornecedores.copy()
            df_forn_display['Total'] = df_forn_display['Valor_Abs'].apply(formatar_moeda)
            st.dataframe(
                df_forn_display[['FORNECEDOR', 'Total']],
                hide_index=True,
                use_container_width=True,
                height=500
            )
    
    with tab7:
        st.success("🔍 **Visão Completa** - Inclui todas as movimentações financeiras para análise de aportes e auditoria")
        st.subheader("💰 Análise Financeira - Aportes SCP")
        
        # Configuração da taxa de juros e opção BARILOCHE
        col_info1, col_config1, col_config2 = st.columns([2, 1, 1])
        
        with col_info1:
            st.info("📊 Esta seção analisa os **Aportes de Capital SCP** e calcula o valor corrigido por juros compostos.")
        
        with col_config1:
            taxa_juros = st.number_input(
                "Taxa mensal (%)",
                min_value=0.0,
                max_value=10.0,
                value=0.9477,
                step=0.0001,
                format="%.4f"
            )
        
        with col_config2:
            considerar_bariloche = st.checkbox(
                "🏔️ BARILOCHE como pagamento",
                value=True,
                help="Considera gastos com BARILOCHE como amortizações dos aportes, reduzindo a base de cálculo dos juros"
            )
        
        # Calcular aportes corrigidos
        analise_aportes = processor.calcular_aportes_corrigidos(
            taxa_juros_mensal=taxa_juros,
            considerar_bariloche_como_pagamento=considerar_bariloche
        )
        
        if analise_aportes['total_aportes_original'] > 0:
            # KPIs de Aportes
            st.markdown("### 📊 Resumo de Aportes SCP")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "💵 Total Original",
                    formatar_moeda(analise_aportes['total_aportes_original'])
                )
            
            with col2:
                st.metric(
                    "📈 Total Corrigido",
                    formatar_moeda(analise_aportes['total_corrigido'])
                )
            
            with col3:
                percentual_juros = (analise_aportes['total_juros'] / analise_aportes['total_aportes_original']) * 100
                st.metric(
                    "💸 Juros Acumulados",
                    formatar_moeda(analise_aportes['total_juros']),
                    delta=f"+{percentual_juros:.1f}%"
                )
            
            with col4:
                st.metric(
                    "📅 Data Base",
                    analise_aportes['data_base_calculo'].strftime('%d/%m/%Y')
                )
            
            st.markdown("---")
            
            # Mostrar amortizações BARILOCHE se opção ativada
            if considerar_bariloche and len(analise_aportes.get('amortizacoes_bariloche', [])) > 0:
                st.info(
                    f"🏔️ **Modo BARILOCHE ativado:** {len(analise_aportes['amortizacoes_bariloche'])} "
                    f"amortizações sendo consideradas como pagamentos dos aportes"
                )
                
                with st.expander("📋 Ver detalhes das amortizações BARILOCHE"):
                    total_amortizado = sum(a['valor'] for a in analise_aportes['amortizacoes_bariloche'])
                    st.metric("💰 Total Amortizado (BARILOCHE)", formatar_moeda(total_amortizado))
                    
                    # Tabela de amortizações
                    df_amort = pd.DataFrame(analise_aportes['amortizacoes_bariloche'])
                    df_amort['Data_Display'] = pd.to_datetime(df_amort['data']).dt.strftime('%d/%m/%Y')
                    df_amort['Valor_Display'] = df_amort['valor'].apply(formatar_moeda)
                    
                    st.dataframe(
                        df_amort[['Data_Display', 'Valor_Display', 'natureza', 'fornecedor']].rename(columns={
                            'Data_Display': 'Data',
                            'Valor_Display': 'Valor',
                            'natureza': 'Natureza',
                            'fornecedor': 'Fornecedor'
                        }),
                        hide_index=True,
                        use_container_width=True,
                        height=min(300, len(df_amort) * 35 + 50)
                    )
                
                st.markdown("---")
            
            # MEMORIAL DE CÁLCULO
            st.markdown("### 📋 Memorial de Cálculo")
            st.info("🔍 **Auditoria Completa:** Este memorial mostra exatamente como os juros foram calculados, similar a uma planilha Excel auditável.")
            
            with st.expander("📊 Ver Memorial de Cálculo Detalhado", expanded=False):
                if len(analise_aportes.get('memorial_calculo', [])) > 0:
                    # Converter memorial para DataFrame
                    df_memorial = pd.DataFrame(analise_aportes['memorial_calculo'])
                    
                    # Formatação para exibição
                    df_memorial['Valor_Original_Display'] = df_memorial['valor_original'].apply(formatar_moeda)
                    df_memorial['Valor_Corrigido_Display'] = df_memorial['valor_corrigido'].apply(formatar_moeda)
                    df_memorial['Juros_Display'] = df_memorial['juros_acumulados'].apply(formatar_moeda)
                    df_memorial['Fator_Juros_Display'] = df_memorial['fator_juros'].apply(lambda x: f"{x:.8f}")
                    
                    # Colunas para exibição
                    colunas_exibir = [
                        'data_aporte', 'Valor_Original_Display', 'meses_decorridos', 
                        'taxa_mensal', 'Fator_Juros_Display', 'Valor_Corrigido_Display', 
                        'Juros_Display', 'formula'
                    ]
                    
                    # Renomear colunas para exibição
                    df_display = df_memorial[colunas_exibir].copy()
                    df_display.columns = [
                        'Data', 'Valor Original', 'Meses', 'Taxa (%)', 
                        'Fator Juros', 'Valor Corrigido', 'Juros', 'Fórmula'
                    ]
                    
                    st.dataframe(
                        df_display,
                        hide_index=True,
                        use_container_width=True,
                        height=min(400, len(df_memorial) * 35 + 50)
                    )
                    
                    # Resumo do memorial
                    st.markdown("#### 📈 Resumo do Memorial:")
                    col_res1, col_res2, col_res3 = st.columns(3)
                    
                    with col_res1:
                        st.metric(
                            "📅 Total de Etapas",
                            len(df_memorial)
                        )
                    
                    with col_res2:
                        st.metric(
                            "💰 Valor Final",
                            formatar_moeda(analise_aportes['total_corrigido'])
                        )
                    
                    with col_res3:
                        st.metric(
                            "📊 Taxa Aplicada",
                            f"{analise_aportes['taxa_juros']:.4f}% a.m."
                        )
                    
                    # Opção para download do memorial
                    st.markdown("#### 💾 Exportar Memorial:")
                    if st.button("📥 Baixar Memorial de Cálculo (Excel)"):
                        # Criar arquivo Excel com memorial
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            # Memorial detalhado
                            df_memorial.to_excel(writer, sheet_name='Memorial_Calculo', index=False)
                            
                            # Resumo
                            resumo_data = {
                                'Métrica': ['Total Aportes Original', 'Total Corrigido', 'Total Juros', 'Taxa Mensal (%)', 'Data Base'],
                                'Valor': [
                                    analise_aportes['total_aportes_original'],
                                    analise_aportes['total_corrigido'],
                                    analise_aportes['total_juros'],
                                    analise_aportes['taxa_juros'],
                                    analise_aportes['data_base_calculo'].strftime('%d/%m/%Y')
                                ]
                            }
                            pd.DataFrame(resumo_data).to_excel(writer, sheet_name='Resumo', index=False)
                        
                        st.download_button(
                            label="📥 Download Memorial de Cálculo.xlsx",
                            data=output.getvalue(),
                            file_name=f"Memorial_Calculo_Aportes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.warning("⚠️ Nenhum memorial de cálculo disponível.")
            
            # Alerta destacado
            st.error(f"🚨 **DÍVIDA TOTAL CORRIGIDA:** {formatar_moeda(analise_aportes['total_corrigido'])} "
                    f"(Taxa: {taxa_juros}% a.m.)")
            
            st.markdown("---")
            
            # Gráficos - Layout organizado e simétrico
            st.markdown("### 📈 Visualizações Gráficas")
            
            # Linha 1: Evolução Acumulativa (destaque - largura total)
            st.markdown("#### 📊 Evolução Acumulativa do Capital + Juros")
            fig_acumulativo = Visualizations.criar_grafico_aportes_acumulativo(
                analise_aportes['aportes_detalhados']
            )
            st.plotly_chart(fig_acumulativo, use_container_width=True)
            
            st.markdown("---")
            
            # Linha 2: Dois gráficos lado a lado (simétrico)
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Evolução Individual dos Aportes")
                fig_aportes = Visualizations.criar_grafico_aportes_corrigidos(
                    analise_aportes['aportes_detalhados']
                )
                st.plotly_chart(fig_aportes, use_container_width=True)
            
            with col2:
                st.markdown("#### 💸 Juros por Aporte (Top 15)")
                fig_juros = Visualizations.criar_grafico_juros_acumulados(
                    analise_aportes['aportes_detalhados']
                )
                st.plotly_chart(fig_juros, use_container_width=True)
            
            # Tabela detalhada de aportes
            st.markdown("---")
            st.markdown("### 📋 Detalhamento dos Aportes")
            
            df_aportes_display = analise_aportes['aportes_detalhados'].copy()
            df_aportes_display['Data_Display'] = df_aportes_display['Data'].dt.strftime('%d/%m/%Y')
            df_aportes_display['Original'] = df_aportes_display['Entrada'].apply(formatar_moeda)
            df_aportes_display['Corrigido'] = df_aportes_display['Valor_Corrigido'].apply(formatar_moeda)
            df_aportes_display['Juros'] = df_aportes_display['Juros_Acumulados'].apply(formatar_moeda)
            df_aportes_display['Meses'] = df_aportes_display['Meses_Decorridos'].apply(lambda x: f"{x:.1f}")
            
            st.dataframe(
                df_aportes_display[['Data_Display', 'Grupo', 'Natureza', 'Original', 
                                   'Meses', 'Juros', 'Corrigido']].rename(columns={
                    'Data_Display': 'Data',
                    'Original': 'Valor Original',
                    'Corrigido': 'Valor Corrigido',
                    'Meses': 'Meses Decorridos'
                }),
                hide_index=True,
                use_container_width=True,
                height=400
            )
        else:
            st.warning("⚠️ Nenhum aporte SCP encontrado nos dados.")
        
        # Análise do Subgrupo Financeiro
        st.markdown("---")
        st.markdown("### 💼 Análise do Subgrupo FINANCEIRO")
        
        analise_fin = processor.analise_subgrupo_financeiro()
        
        if analise_fin['num_transacoes'] > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "📥 Entradas Financeiras",
                    formatar_moeda(analise_fin['total_entradas'])
                )
            
            with col2:
                st.metric(
                    "📤 Saídas Financeiras",
                    formatar_moeda(analise_fin['total_saidas'])
                )
            
            with col3:
                st.metric(
                    "💰 Saldo Financeiro",
                    formatar_moeda(analise_fin['saldo'])
                )
            
            with col4:
                st.metric(
                    "📊 Transações",
                    f"{analise_fin['num_transacoes']:,}".replace(',', '.')
                )
            
            st.markdown("---")
            
            # Gráfico de distribuição por natureza
            fig_fin = Visualizations.criar_grafico_financeiro_natureza(analise_fin['df_financeiro'])
            st.plotly_chart(fig_fin, use_container_width=True)
            
            # Tabela por natureza
            st.markdown("### 📊 Resumo por Natureza")
            df_nat_display = analise_fin['por_natureza'].copy()
            df_nat_display['Entradas'] = df_nat_display['Entrada'].apply(formatar_moeda)
            df_nat_display['Saídas'] = df_nat_display['Saida'].apply(lambda x: formatar_moeda(abs(x)))
            df_nat_display['Saldo'] = df_nat_display['Saldo'].apply(formatar_moeda)
            
            st.dataframe(
                df_nat_display[['Natureza', 'Entradas', 'Saídas', 'Saldo']],
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("ℹ️ Nenhuma transação financeira encontrada no período filtrado.")
    
    with tab8:
        st.subheader("Dados Detalhados")
        
        # Seletor de visão
        col_visao, col_busca, col_linhas = st.columns([1, 2, 1])
        
        with col_visao:
            tipo_visao = st.radio(
                "Visão dos Dados",
                ["Operacional", "Completa"],
                index=0,
                help="Operacional: sem transferências internas | Completa: todas as transações"
            )
        
        with col_busca:
            busca = st.text_input("🔍 Buscar (fornecedor, natureza, grupo...)", "")
        
        with col_linhas:
            num_linhas = st.selectbox("Linhas/página", [50, 100, 200, 500], index=1)
        
        # Selecionar DataFrame baseado na visão escolhida
        df_display = df_operacional_filtrado.copy() if tipo_visao == "Operacional" else df_completo_filtrado.copy()
        
        # Indicador visual da visão ativa
        if tipo_visao == "Operacional":
            st.info("🎯 Exibindo **Visão Operacional** - Transferências internas excluídas")
        else:
            st.success("🔍 Exibindo **Visão Completa** - Todas as movimentações incluídas")
        if busca:
            mask = (
                df_display['FORNECEDOR'].str.contains(busca, case=False, na=False) |
                df_display['Natureza'].str.contains(busca, case=False, na=False) |
                df_display['Grupo'].str.contains(busca, case=False, na=False)
            )
            df_display = df_display[mask]
        
        # Preparar para exibição
        df_display['Data_Display'] = df_display['Data'].dt.strftime('%d/%m/%Y')
        df_display['Entrada_Display'] = df_display['Entrada'].apply(formatar_moeda)
        df_display['Saida_Display'] = df_display['Saida'].apply(lambda x: formatar_moeda(abs(x)))
        df_display['Saldo_Display'] = df_display['Saldo'].apply(formatar_moeda)
        
        colunas_exibir = ['Data_Display', 'Grupo', 'Subgrupo', 'Natureza', 'FORNECEDOR', 
                         'Entrada_Display', 'Saida_Display', 'Saldo_Display']
        
        st.dataframe(
            df_display[colunas_exibir].head(num_linhas),
            hide_index=True,
            use_container_width=True,
            height=600
        )
        
        # Botão de download
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            csv = df_display.to_csv(index=False, encoding='utf-8-sig', sep=';')
            st.download_button(
                label="📥 Baixar CSV",
                data=csv,
                file_name=f"dados_financeiros_{tipo_visao.lower()}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Estatísticas rápidas
            st.metric("Total de Registros", f"{len(df_display):,}".replace(',', '.'))
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; opacity: 0.7; padding: 1rem;'>
            Dashboard Financeiro v1.0 | Desenvolvido com ❤️ usando Python, Streamlit e Plotly
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

