"""
Módulo de visualizações
Responsabilidade: Criação de gráficos e componentes visuais
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional
from .utils import formatar_moeda, extrair_mes_ano_legivel


class Visualizations:
    """
    Classe responsável pela criação de visualizações interativas
    Princípios: Single Responsibility, Separation of Concerns
    """
    
    # Paleta de cores moderna e profissional
    COLOR_ENTRADA = '#10b981'  # Verde
    COLOR_SAIDA = '#ef4444'    # Vermelho
    COLOR_SALDO = '#3b82f6'    # Azul
    COLOR_ACCENT = '#8b5cf6'   # Roxo
    
    TEMPLATE = 'plotly_dark'
    
    # Configurações de animação padrão
    ANIMATION_DURATION = 800  # ms
    ANIMATION_EASING = 'cubic-in-out'
    
    @staticmethod
    def _aplicar_animacoes(fig: go.Figure) -> go.Figure:
        """
        Aplica configurações de hover suave adaptáveis ao tema
        
        Args:
            fig: Figura Plotly
            
        Returns:
            Figura com hover melhorado
        """
        # Hoverlabel adaptável - usa cores que funcionam bem em ambos os temas
        # Fundo semi-transparente escuro com texto claro para melhor contraste
        fig.update_layout(
            hoverlabel=dict(
                bgcolor="rgba(30, 30, 30, 0.9)",  # Fundo escuro semi-transparente
                bordercolor="rgba(255, 255, 255, 0.2)",  # Borda clara sutil
                font_size=14,
                font_family="Arial",
                font_color="white"  # Texto branco para contraste
            )
        )
        
        return fig
    
    @staticmethod
    def criar_grafico_evolucao_temporal(df_temporal: pd.DataFrame) -> go.Figure:
        """
        Cria gráfico de evolução temporal de entradas e saídas
        
        Args:
            df_temporal: DataFrame com agregação temporal
            
        Returns:
            Figura Plotly
        """
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3],
            subplot_titles=('Fluxo de Caixa Mensal', 'Saldo Acumulado'),
            vertical_spacing=0.15
        )
        
        fig.add_trace(
            go.Bar(
                x=df_temporal['Data'],
                y=df_temporal['Entrada'],
                name='Entradas',
                marker=dict(
                    color=Visualizations.COLOR_ENTRADA,
                    opacity=0.85,
                    cornerradius=6,
                ),
                hovertemplate='<b>Entrada</b><br>Data: %{x|%b/%Y}<br>Valor: R$ %{y:,.2f}<extra></extra>'
            ),
            row=1, col=1
        )

        fig.add_trace(
            go.Bar(
                x=df_temporal['Data'],
                y=df_temporal['Saida'].abs(),
                name='Saídas',
                marker=dict(
                    color=Visualizations.COLOR_SAIDA,
                    opacity=0.85,
                    cornerradius=6,
                ),
                hovertemplate='<b>Saída</b><br>Data: %{x|%b/%Y}<br>Valor: R$ %{y:,.2f}<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Gráfico de área - Saldo Acumulado com gradiente suave
        fig.add_trace(
            go.Scatter(
                x=df_temporal['Data'],
                y=df_temporal['Saldo_Acumulado'],
                name='Saldo Acumulado',
                fill='tozeroy',
                line=dict(color=Visualizations.COLOR_SALDO, width=4, shape='spline'),
                fillcolor='rgba(59, 130, 246, 0.2)',
                marker=dict(size=8, symbol='circle'),
                hovertemplate='<b>Saldo Acumulado</b><br>Data: %{x|%b/%Y}<br>Valor: R$ %{y:,.2f}<extra></extra>'
            ),
            row=2, col=1
        )
        
        # Layout limpo e profissional
        fig.update_layout(
            template=Visualizations.TEMPLATE,
            height=700,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode='x unified'
        )
        
        fig.update_xaxes(title_text="Período", row=2, col=1)
        fig.update_yaxes(title_text="Valor (R$)", row=1, col=1)
        fig.update_yaxes(title_text="Saldo (R$)", row=2, col=1)
        
        return Visualizations._aplicar_animacoes(fig)
    
    @staticmethod
    def criar_grafico_por_grupo(df_grupo: pd.DataFrame, top_n: int = 10) -> go.Figure:
        """
        Cria gráfico de distribuição por grupo/projeto
        
        Args:
            df_grupo: DataFrame agregado por grupo
            top_n: Número de grupos a exibir
            
        Returns:
            Figura Plotly
        """
        df_top = df_grupo.head(top_n).copy()
        df_top['Saida_Display'] = df_top['Saida'].abs()
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Bar(
                y=df_top['Grupo'],
                x=df_top['Saida_Display'],
                orientation='h',
                marker=dict(
                    color=Visualizations.COLOR_SAIDA,
                    opacity=0.85,
                    cornerradius=8,
                ),
                text=df_top['Saida_Display'].apply(lambda x: f'R$ {x:,.0f}'),
                textposition='outside',
                textfont=dict(size=13, color='white', family='Arial'),
                hovertemplate='<b>%{y}</b><br>Saídas: R$ %{x:,.2f}<extra></extra>',
                cliponaxis=False
            )
        )
        
        # Calcular o range do eixo X para as barras ocuparem toda a largura
        max_valor = df_top['Saida_Display'].max()
        
        # Altura dinâmica baseada no número de grupos
        num_grupos = len(df_top)
        if num_grupos == 1:
            altura = 200  # Altura mínima para 1 grupo
        elif num_grupos <= 3:
            altura = 300
        elif num_grupos <= 5:
            altura = 400
        else:
            altura = 500  # Altura padrão para muitos grupos
        
        fig.update_layout(
            title=f'Top {top_n} Grupos/Projetos por Saídas',
            template=Visualizations.TEMPLATE,
            height=altura,
            xaxis_title='Valor (R$)',
            yaxis_title='Grupo',
            yaxis={'categoryorder': 'total ascending'},
            bargap=0.3,  # Aumentado para barras mais finas
            margin=dict(l=200, r=80, t=50, b=50),
            xaxis=dict(
                range=[0, max_valor * 1.02],  # 2% extra para o texto
                fixedrange=False
            )
        )
        
        # Ajustar espessura das barras
        fig.update_traces(width=0.6)
        
        return Visualizations._aplicar_animacoes(fig)
    
    @staticmethod
    def criar_treemap_natureza(df_natureza: pd.DataFrame) -> go.Figure:
        """
        Cria treemap de distribuição por natureza
        
        Args:
            df_natureza: DataFrame agregado por subgrupo e natureza
            
        Returns:
            Figura Plotly
        """
        df_plot = df_natureza.copy()
        df_plot['Saida_Abs'] = df_plot['Saida'].abs()
        df_plot = df_plot[df_plot['Saida_Abs'] > 0]  # Apenas saídas
        
        # Criar labels combinados
        df_plot['Label'] = df_plot['Natureza']
        
        fig = go.Figure(
            go.Treemap(
                labels=df_plot['Label'],
                parents=df_plot['Subgrupo'],
                values=df_plot['Saida_Abs'],
                text=df_plot['Saida_Abs'].apply(lambda x: f'R$ {x:,.2f}'),
                textposition='middle center',
                marker=dict(
                    colorscale='RdYlGn_r',
                    cmid=df_plot['Saida_Abs'].median()
                ),
                hovertemplate='<b>%{label}</b><br>Categoria: %{parent}<br>Valor: R$ %{value:,.2f}<extra></extra>'
            )
        )
        
        fig.update_layout(
            title='Distribuição de Despesas por Categoria',
            template=Visualizations.TEMPLATE,
            height=600
        )
        
        return Visualizations._aplicar_animacoes(fig)
    
    @staticmethod
    def criar_grafico_fornecedores(df_fornecedores: pd.DataFrame, top_n: int = 15) -> go.Figure:
        """
        Cria gráfico de top fornecedores
        
        Args:
            df_fornecedores: DataFrame de fornecedores
            top_n: Número de fornecedores a exibir
            
        Returns:
            Figura Plotly
        """
        df_top = df_fornecedores.head(top_n).copy()
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Bar(
                y=df_top['FORNECEDOR'],
                x=df_top['Valor_Abs'],
                orientation='h',
                marker=dict(
                    color=Visualizations.COLOR_ACCENT,
                    opacity=0.85,
                    cornerradius=8,
                ),
                text=df_top['Valor_Abs'].apply(lambda x: f'R$ {x:,.0f}'),
                textposition='outside',
                textfont=dict(size=13, color='white', family='Arial'),
                hovertemplate='<b>%{y}</b><br>Total: R$ %{x:,.2f}<extra></extra>',
                cliponaxis=False
            )
        )
        
        # Calcular o range do eixo X para as barras ocuparem toda a largura
        max_valor = df_top['Valor_Abs'].max()
        
        fig.update_layout(
            title=f'Top {top_n} Fornecedores por Volume',
            template=Visualizations.TEMPLATE,
            height=600,
            xaxis_title='Valor Total (R$)',
            yaxis_title='Fornecedor',
            yaxis={'categoryorder': 'total ascending'},
            bargap=0.15,
            margin=dict(l=250, r=80, t=50, b=50),
            xaxis=dict(
                range=[0, max_valor * 1.02],  # 2% extra para o texto
                fixedrange=False
            )
        )
        
        return Visualizations._aplicar_animacoes(fig)
    
    @staticmethod
    def criar_grafico_pizza_subgrupo(df: pd.DataFrame) -> go.Figure:
        """
        Cria gráfico de pizza para distribuição por subgrupo
        
        Args:
            df: DataFrame com dados
            
        Returns:
            Figura Plotly
        """
        df_subgrupo = df.groupby('Subgrupo')['Saida'].sum().abs().reset_index()
        df_subgrupo = df_subgrupo.sort_values('Saida', ascending=False).head(8)
        
        fig = go.Figure(
            go.Pie(
                labels=df_subgrupo['Subgrupo'],
                values=df_subgrupo['Saida'],
                hole=0.4,
                marker=dict(
                    colors=px.colors.qualitative.Set3,
                    line=dict(color='white', width=3)
                ),
                textinfo='label+percent',
                textfont=dict(size=12, family='Arial', color='white'),
                hovertemplate='<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Percentual: %{percent}<extra></extra>',
                pull=[0.05] * len(df_subgrupo),  # Destacar todas as fatias sutilmente
                opacity=0.95
            )
        )
        
        fig.update_layout(
            title='Distribuição de Despesas por Subgrupo',
            template=Visualizations.TEMPLATE,
            height=500
        )
        
        return Visualizations._aplicar_animacoes(fig)
    
    @staticmethod
    def criar_grafico_comparativo_mensal(df: pd.DataFrame) -> go.Figure:
        """
        Cria gráfico comparativo mês a mês
        
        Args:
            df: DataFrame com dados temporais
            
        Returns:
            Figura Plotly
        """
        df_mensal = df.groupby('AnoMes').agg({
            'Entrada': 'sum',
            'Saida': 'sum',
            'Saldo': 'sum'
        }).reset_index()
        
        df_mensal = df_mensal.tail(12)  # Últimos 12 meses
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Scatter(
                x=df_mensal['AnoMes'],
                y=df_mensal['Entrada'],
                name='Entradas',
                mode='lines+markers',
                line=dict(color=Visualizations.COLOR_ENTRADA, width=4, shape='spline'),
                marker=dict(size=12, symbol='circle', line=dict(color='white', width=2)),
                hovertemplate='<b>Entrada</b><br>Período: %{x}<br>Valor: R$ %{y:,.2f}<extra></extra>',
                fill='tozeroy',
                fillcolor='rgba(16, 185, 129, 0.1)'
            )
        )
        
        fig.add_trace(
            go.Scatter(
                x=df_mensal['AnoMes'],
                y=df_mensal['Saida'].abs(),
                name='Saídas',
                mode='lines+markers',
                line=dict(color=Visualizations.COLOR_SAIDA, width=4, shape='spline'),
                marker=dict(size=12, symbol='circle', line=dict(color='white', width=2)),
                hovertemplate='<b>Saída</b><br>Período: %{x}<br>Valor: R$ %{y:,.2f}<extra></extra>',
                fill='tozeroy',
                fillcolor='rgba(239, 68, 68, 0.1)'
            )
        )
        
        fig.update_layout(
            title='Evolução Mensal - Últimos 12 Meses',
            template=Visualizations.TEMPLATE,
            height=400,
            xaxis_title='Período',
            yaxis_title='Valor (R$)',
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return Visualizations._aplicar_animacoes(fig)
    
    @staticmethod
    def criar_grafico_aportes_corrigidos(df_aportes: pd.DataFrame) -> go.Figure:
        """
        Cria gráfico de evolução de aportes corrigidos
        
        Args:
            df_aportes: DataFrame com aportes detalhados
            
        Returns:
            Figura Plotly
        """
        if len(df_aportes) == 0:
            return go.Figure()
        
        df_plot = df_aportes.sort_values('Data').copy()
        
        fig = go.Figure()
        
        # Valor original
        fig.add_trace(
            go.Scatter(
                x=df_plot['Data'],
                y=df_plot['Entrada'],
                name='Valor Original',
                mode='lines+markers',
                line=dict(color='#3b82f6', width=3),
                marker=dict(size=10),
                fill='tozeroy',
                fillcolor='rgba(59, 130, 246, 0.1)',
                hovertemplate='<b>Original</b><br>Data: %{x|%d/%m/%Y}<br>Valor: R$ %{y:,.2f}<extra></extra>'
            )
        )
        
        # Valor corrigido
        fig.add_trace(
            go.Scatter(
                x=df_plot['Data'],
                y=df_plot['Valor_Corrigido'],
                name='Valor Corrigido',
                mode='lines+markers',
                line=dict(color='#ef4444', width=3, dash='dot'),
                marker=dict(size=10, symbol='diamond'),
                hovertemplate='<b>Corrigido</b><br>Data: %{x|%d/%m/%Y}<br>Valor: R$ %{y:,.2f}<extra></extra>'
            )
        )
        
        fig.update_layout(
            title='Evolução dos Aportes SCP (Original vs Corrigido)',
            template=Visualizations.TEMPLATE,
            height=500,
            xaxis_title='Data do Aporte',
            yaxis_title='Valor Acumulado (R$)',
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        return Visualizations._aplicar_animacoes(fig)
    
    @staticmethod
    def criar_grafico_juros_acumulados(df_aportes: pd.DataFrame) -> go.Figure:
        """
        Cria gráfico de juros acumulados por aporte
        
        Args:
            df_aportes: DataFrame com aportes detalhados
            
        Returns:
            Figura Plotly
        """
        if len(df_aportes) == 0:
            return go.Figure()
        
        df_plot = df_aportes.sort_values('Juros_Acumulados', ascending=True).tail(15).copy()
        
        # Criar label com grupo
        df_plot['Label'] = df_plot.apply(
            lambda x: f"{x['Grupo']} - {x['Data'].strftime('%m/%Y')}", 
            axis=1
        )
        
        fig = go.Figure()
        
        fig.add_trace(
            go.Bar(
                y=df_plot['Label'],
                x=df_plot['Juros_Acumulados'],
                orientation='h',
                marker=dict(
                    color=Visualizations.COLOR_SAIDA,
                    opacity=0.85,
                    cornerradius=8,
                ),
                text=df_plot['Juros_Acumulados'].apply(lambda x: f'R$ {x:,.0f}'),
                textposition='outside',
                textfont=dict(size=13, color='white', family='Arial'),
                hovertemplate='<b>%{y}</b><br>Juros: R$ %{x:,.2f}<extra></extra>',
                cliponaxis=False
            )
        )
        
        # Calcular o range do eixo X para as barras ocuparem toda a largura
        max_valor = df_plot['Juros_Acumulados'].max()
        
        fig.update_layout(
            title='Juros Acumulados por Aporte (Top 15)',
            template=Visualizations.TEMPLATE,
            height=600,
            xaxis_title='Juros Acumulados (R$)',
            yaxis_title='Aporte',
            yaxis={'categoryorder': 'total ascending'},
            bargap=0.15,
            margin=dict(l=200, r=80, t=50, b=50),
            xaxis=dict(
                range=[0, max_valor * 1.02],  # 2% extra para o texto
                fixedrange=False
            )
        )
        
        return Visualizations._aplicar_animacoes(fig)
    
    @staticmethod
    def criar_grafico_aportes_acumulativo(df_aportes: pd.DataFrame) -> go.Figure:
        """
        Cria gráfico acumulativo de aportes com juros ao longo do tempo
        
        Args:
            df_aportes: DataFrame com aportes detalhados
            
        Returns:
            Figura Plotly com evolução acumulativa
        """
        if len(df_aportes) == 0:
            return go.Figure()
        
        # Ordenar por data
        df_plot = df_aportes.sort_values('Data').copy()
        
        # Calcular valores acumulados
        df_plot['Entrada_Acumulada'] = df_plot['Entrada'].cumsum()
        df_plot['Corrigido_Acumulado'] = df_plot['Valor_Corrigido'].cumsum()
        df_plot['Juros_Acumulados_Total'] = df_plot['Corrigido_Acumulado'] - df_plot['Entrada_Acumulada']
        
        fig = go.Figure()
        
        # Área de valor original acumulado
        fig.add_trace(
            go.Scatter(
                x=df_plot['Data'],
                y=df_plot['Entrada_Acumulada'],
                name='Capital Aportado',
                mode='lines',
                line=dict(color='#3b82f6', width=0),
                fill='tozeroy',
                fillcolor='rgba(59, 130, 246, 0.3)',
                hovertemplate='<b>Capital Aportado</b><br>Data: %{x|%d/%m/%Y}<br>Valor: R$ %{y:,.2f}<extra></extra>'
            )
        )
        
        # Área de juros acumulados (área entre original e corrigido)
        fig.add_trace(
            go.Scatter(
                x=df_plot['Data'],
                y=df_plot['Corrigido_Acumulado'],
                name='Juros Acumulados',
                mode='lines',
                line=dict(color='#ef4444', width=0),
                fill='tonexty',
                fillcolor='rgba(239, 68, 68, 0.3)',
                hovertemplate='<b>Total com Juros</b><br>Data: %{x|%d/%m/%Y}<br>Valor: R$ %{y:,.2f}<extra></extra>'
            )
        )
        
        # Linha do valor total corrigido
        fig.add_trace(
            go.Scatter(
                x=df_plot['Data'],
                y=df_plot['Corrigido_Acumulado'],
                name='Total Corrigido',
                mode='lines+markers',
                line=dict(color='#dc2626', width=3),
                marker=dict(size=8, symbol='diamond'),
                hovertemplate='<b>Total Corrigido</b><br>Data: %{x|%d/%m/%Y}<br>Valor: R$ %{y:,.2f}<extra></extra>'
            )
        )
        
        # Linha do capital original
        fig.add_trace(
            go.Scatter(
                x=df_plot['Data'],
                y=df_plot['Entrada_Acumulada'],
                name='Capital Original',
                mode='lines+markers',
                line=dict(color='#2563eb', width=3),
                marker=dict(size=8),
                hovertemplate='<b>Capital Original</b><br>Data: %{x|%d/%m/%Y}<br>Valor: R$ %{y:,.2f}<extra></extra>'
            )
        )
        
        fig.update_layout(
            title='Evolução Acumulativa: Capital + Juros',
            template=Visualizations.TEMPLATE,
            height=500,
            xaxis_title='Data',
            yaxis_title='Valor Acumulado (R$)',
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return Visualizations._aplicar_animacoes(fig)
    
    @staticmethod
    def criar_grafico_financeiro_natureza(df_financeiro: pd.DataFrame) -> go.Figure:
        """
        Cria gráfico de distribuição do subgrupo financeiro por natureza
        
        Args:
            df_financeiro: DataFrame apenas com transações financeiras
            
        Returns:
            Figura Plotly
        """
        if len(df_financeiro) == 0:
            return go.Figure()
        
        df_nat = df_financeiro.groupby('Natureza').agg({
            'Entrada': 'sum',
            'Saida': 'sum',
            'Saldo': 'sum'
        }).reset_index()
        
        # Separar entradas e saídas
        df_entradas = df_nat[df_nat['Entrada'] > 0].sort_values('Entrada', ascending=False)
        df_saidas = df_nat[df_nat['Saida'] < 0].sort_values('Saida', ascending=True)
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Entradas Financeiras', 'Saídas Financeiras'),
            specs=[[{"type": "bar"}, {"type": "bar"}]]
        )
        
        # Entradas
        if len(df_entradas) > 0:
            fig.add_trace(
                go.Bar(
                    y=df_entradas['Natureza'],
                    x=df_entradas['Entrada'],
                    orientation='h',
                    name='Entradas',
                    marker=dict(color=Visualizations.COLOR_ENTRADA, opacity=0.85, cornerradius=8),
                    text=df_entradas['Entrada'].apply(lambda x: f'R$ {x:,.0f}'),
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>Valor: R$ %{x:,.2f}<extra></extra>'
                ),
                row=1, col=1
            )

        # Saídas
        if len(df_saidas) > 0:
            fig.add_trace(
                go.Bar(
                    y=df_saidas['Natureza'],
                    x=df_saidas['Saida'].abs(),
                    orientation='h',
                    name='Saídas',
                    marker=dict(color=Visualizations.COLOR_SAIDA, opacity=0.85, cornerradius=8),
                    text=df_saidas['Saida'].abs().apply(lambda x: f'R$ {x:,.0f}'),
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>Valor: R$ %{x:,.2f}<extra></extra>'
                ),
                row=1, col=2
            )
        
        fig.update_layout(
            title='Movimentações Financeiras por Natureza',
            template=Visualizations.TEMPLATE,
            height=500,
            showlegend=False
        )
        
        fig.update_xaxes(title_text="Valor (R$)", row=1, col=1)
        fig.update_xaxes(title_text="Valor (R$)", row=1, col=2)
        fig.update_yaxes(categoryorder='total ascending', row=1, col=1)
        fig.update_yaxes(categoryorder='total ascending', row=1, col=2)
        
        return Visualizations._aplicar_animacoes(fig)
    
    @staticmethod
    def criar_graficos_por_grupo_subgrupo_natureza(df: pd.DataFrame) -> dict:
        """
        Cria múltiplos gráficos de barras, um para cada combinação de Grupo + Subgrupo,
        mostrando as naturezas como barras dentro de cada gráfico
        
        Args:
            df: DataFrame com dados
            
        Returns:
            Dicionário com chave (Grupo, Subgrupo) e valor (Figura Plotly)
        """
        # Agregar por Grupo, Subgrupo e Natureza
        df_agregado = df.groupby(['Grupo', 'Subgrupo', 'Natureza'])['Saida'].sum().abs().reset_index()
        df_agregado = df_agregado[df_agregado['Saida'] > 0]  # Apenas despesas
        
        # Obter todas as combinações únicas de Grupo + Subgrupo
        combinacoes = df_agregado[['Grupo', 'Subgrupo']].drop_duplicates()
        
        # Calcular total por combinação para ordenar
        totais = df_agregado.groupby(['Grupo', 'Subgrupo'])['Saida'].sum().reset_index()
        totais.columns = ['Grupo', 'Subgrupo', 'Total']
        combinacoes = combinacoes.merge(totais, on=['Grupo', 'Subgrupo'])
        combinacoes = combinacoes.sort_values('Total', ascending=False)
        
        graficos = {}
        
        # Cores sólidas por grupo
        cores_grupo = {
            'RITHMO': '#3b82f6',
            'NORTHSIDE': '#3b82f6',
            'ÁGATA': '#8b5cf6',
            'BARILOCHE': '#f97316',
        }

        for _, row in combinacoes.iterrows():
            grupo = row['Grupo']
            subgrupo = row['Subgrupo']

            # Filtrar dados desta combinação
            df_combo = df_agregado[
                (df_agregado['Grupo'] == grupo) &
                (df_agregado['Subgrupo'] == subgrupo)
            ].copy()

            df_combo = df_combo.sort_values('Saida', ascending=True)

            # Criar gráfico
            fig = go.Figure()

            cor = cores_grupo.get(grupo, Visualizations.COLOR_SAIDA)

            fig.add_trace(
                go.Bar(
                    y=df_combo['Natureza'],
                    x=df_combo['Saida'],
                    orientation='h',
                    marker=dict(
                        color=cor,
                        opacity=0.85,
                        cornerradius=8,
                    ),
                    text=df_combo['Saida'].apply(lambda x: f'R$ {x:,.0f}'),
                    textposition='outside',
                    textfont=dict(size=12, color='white', family='Arial'),
                    hovertemplate='<b>%{y}</b><br>Valor: R$ %{x:,.2f}<extra></extra>',
                    cliponaxis=False
                )
            )
            
            max_valor = df_combo['Saida'].max()
            num_naturezas = len(df_combo)
            
            # Altura dinâmica baseada no número de naturezas
            if num_naturezas <= 3:
                altura = 300
            elif num_naturezas <= 6:
                altura = 400
            elif num_naturezas <= 10:
                altura = 500
            else:
                altura = 600
            
            fig.update_layout(
                title=f'{grupo} - {subgrupo}',
                template=Visualizations.TEMPLATE,
                height=altura,
                xaxis_title='Valor (R$)',
                yaxis_title='Natureza',
                yaxis={'categoryorder': 'total ascending'},
                bargap=0.2,
                margin=dict(l=250, r=100, t=60, b=50),
                xaxis=dict(
                    range=[0, max_valor * 1.15],
                    fixedrange=False
                )
            )
            
            fig.update_traces(width=0.6)
            fig = Visualizations._aplicar_animacoes(fig)
            
            graficos[(grupo, subgrupo)] = fig
        
        return graficos
    
    @staticmethod
    def criar_graficos_receitas_por_grupo_subgrupo_natureza(df: pd.DataFrame) -> dict:
        """
        Cria múltiplos gráficos de barras para RECEITAS (Entradas), 
        um para cada combinação de Grupo + Subgrupo, mostrando as naturezas como barras
        
        Args:
            df: DataFrame com dados
            
        Returns:
            Dicionário com chave (Grupo, Subgrupo) e valor (Figura Plotly)
        """
        # Agregar por Grupo, Subgrupo e Natureza - APENAS ENTRADAS
        df_agregado = df.groupby(['Grupo', 'Subgrupo', 'Natureza'])['Entrada'].sum().reset_index()
        df_agregado = df_agregado[df_agregado['Entrada'] > 0]  # Apenas receitas
        
        # Obter todas as combinações únicas de Grupo + Subgrupo
        combinacoes = df_agregado[['Grupo', 'Subgrupo']].drop_duplicates()
        
        # Calcular total por combinação para ordenar
        totais = df_agregado.groupby(['Grupo', 'Subgrupo'])['Entrada'].sum().reset_index()
        totais.columns = ['Grupo', 'Subgrupo', 'Total']
        combinacoes = combinacoes.merge(totais, on=['Grupo', 'Subgrupo'])
        combinacoes = combinacoes.sort_values('Total', ascending=False)
        
        graficos = {}
        
        for _, row in combinacoes.iterrows():
            grupo = row['Grupo']
            subgrupo = row['Subgrupo']

            # Filtrar dados desta combinação
            df_combo = df_agregado[
                (df_agregado['Grupo'] == grupo) &
                (df_agregado['Subgrupo'] == subgrupo)
            ].copy()

            df_combo = df_combo.sort_values('Entrada', ascending=True)

            # Criar gráfico
            fig = go.Figure()

            fig.add_trace(
                go.Bar(
                    y=df_combo['Natureza'],
                    x=df_combo['Entrada'],
                    orientation='h',
                    marker=dict(
                        color=Visualizations.COLOR_ENTRADA,
                        opacity=0.85,
                        cornerradius=8,
                    ),
                    text=df_combo['Entrada'].apply(lambda x: f'R$ {x:,.0f}'),
                    textposition='outside',
                    textfont=dict(size=12, color='white', family='Arial'),
                    hovertemplate='<b>%{y}</b><br>Receita: R$ %{x:,.2f}<extra></extra>',
                    cliponaxis=False
                )
            )
            
            max_valor = df_combo['Entrada'].max()
            num_naturezas = len(df_combo)
            
            # Altura dinâmica baseada no número de naturezas
            if num_naturezas <= 3:
                altura = 300
            elif num_naturezas <= 6:
                altura = 400
            elif num_naturezas <= 10:
                altura = 500
            else:
                altura = 600
            
            fig.update_layout(
                title=f'{grupo} - {subgrupo} (RECEITAS)',
                template=Visualizations.TEMPLATE,
                height=altura,
                xaxis_title='Valor (R$)',
                yaxis_title='Natureza',
                yaxis={'categoryorder': 'total ascending'},
                bargap=0.2,
                margin=dict(l=250, r=100, t=60, b=50),
                xaxis=dict(
                    range=[0, max_valor * 1.15],
                    fixedrange=False
                )
            )
            
            fig.update_traces(width=0.6)
            fig = Visualizations._aplicar_animacoes(fig)
            
            graficos[(grupo, subgrupo)] = fig
        
        return graficos
    
    @staticmethod
    def criar_grafico_despesas_por_natureza(df: pd.DataFrame, grupo: str, subgrupo: str) -> go.Figure:
        """
        Cria gráfico de barras de despesas por natureza para um grupo e subgrupo específicos
        
        Args:
            df: DataFrame com dados
            grupo: Grupo selecionado
            subgrupo: Subgrupo selecionado
            
        Returns:
            Figura Plotly
        """
        # Filtrar por grupo e subgrupo
        df_filtrado = df[(df['Grupo'] == grupo) & (df['Subgrupo'] == subgrupo)].copy()
        
        # Agregar por Natureza
        df_agregado = df_filtrado.groupby('Natureza')['Saida'].sum().abs().reset_index()
        df_agregado = df_agregado[df_agregado['Saida'] > 0]
        df_agregado = df_agregado.sort_values('Saida', ascending=True)
        
        if len(df_agregado) == 0:
            # Retornar gráfico vazio com mensagem
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhuma despesa encontrada para esta combinação",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=14, color="#6b7280")
            )
            fig.update_layout(
                template=Visualizations.TEMPLATE,
                height=400,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False)
            )
            return fig
        
        # Cores sólidas por grupo
        cores_grupo = {
            'RITHMO': '#3b82f6',
            'NORTHSIDE': '#3b82f6',
            'ÁGATA': '#8b5cf6',
            'BARILOCHE': '#f97316',
        }
        cor = cores_grupo.get(grupo, Visualizations.COLOR_SAIDA)

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                y=df_agregado['Natureza'],
                x=df_agregado['Saida'],
                orientation='h',
                marker=dict(
                    color=cor,
                    opacity=0.85,
                    cornerradius=8,
                ),
                text=df_agregado['Saida'].apply(lambda x: f'R$ {x:,.0f}'),
                textposition='outside',
                textfont=dict(size=12, color='white', family='Arial'),
                hovertemplate='<b>%{y}</b><br>Valor: R$ %{x:,.2f}<extra></extra>',
                cliponaxis=False
            )
        )
        
        max_valor = df_agregado['Saida'].max()
        num_naturezas = len(df_agregado)
        
        # Altura dinâmica
        if num_naturezas <= 3:
            altura = 300
        elif num_naturezas <= 6:
            altura = 400
        elif num_naturezas <= 10:
            altura = 500
        else:
            altura = 600
        
        fig.update_layout(
            title=f'💸 {grupo} - {subgrupo}',
            template=Visualizations.TEMPLATE,
            height=altura,
            xaxis_title='Valor (R$)',
            yaxis_title='Natureza',
            yaxis={'categoryorder': 'total ascending'},
            bargap=0.2,
            margin=dict(l=250, r=100, t=60, b=50),
            xaxis=dict(
                range=[0, max_valor * 1.15],
                fixedrange=False
            )
        )
        
        fig.update_traces(width=0.6)
        
        return Visualizations._aplicar_animacoes(fig)
    
    @staticmethod
    def criar_grafico_receitas_por_natureza(df: pd.DataFrame, grupo: str, subgrupo: str) -> go.Figure:
        """
        Cria gráfico de barras de receitas por natureza para um grupo e subgrupo específicos
        
        Args:
            df: DataFrame com dados
            grupo: Grupo selecionado
            subgrupo: Subgrupo selecionado
            
        Returns:
            Figura Plotly
        """
        # Filtrar por grupo e subgrupo
        df_filtrado = df[(df['Grupo'] == grupo) & (df['Subgrupo'] == subgrupo)].copy()
        
        # Agregar por Natureza - ENTRADAS
        df_agregado = df_filtrado.groupby('Natureza')['Entrada'].sum().reset_index()
        df_agregado = df_agregado[df_agregado['Entrada'] > 0]
        df_agregado = df_agregado.sort_values('Entrada', ascending=True)
        
        if len(df_agregado) == 0:
            # Retornar gráfico vazio com mensagem
            fig = go.Figure()
            fig.add_annotation(
                text="Nenhuma receita encontrada para esta combinação",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=14, color="#6b7280")
            )
            fig.update_layout(
                template=Visualizations.TEMPLATE,
                height=400,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False)
            )
            return fig
        
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                y=df_agregado['Natureza'],
                x=df_agregado['Entrada'],
                orientation='h',
                marker=dict(
                    color=Visualizations.COLOR_ENTRADA,
                    opacity=0.85,
                    cornerradius=8,
                ),
                text=df_agregado['Entrada'].apply(lambda x: f'R$ {x:,.0f}'),
                textposition='outside',
                textfont=dict(size=12, color='white', family='Arial'),
                hovertemplate='<b>%{y}</b><br>Receita: R$ %{x:,.2f}<extra></extra>',
                cliponaxis=False
            )
        )
        
        max_valor = df_agregado['Entrada'].max()
        num_naturezas = len(df_agregado)
        
        # Altura dinâmica
        if num_naturezas <= 3:
            altura = 300
        elif num_naturezas <= 6:
            altura = 400
        elif num_naturezas <= 10:
            altura = 500
        else:
            altura = 600
        
        fig.update_layout(
            title=f'💰 {grupo} - {subgrupo}',
            template=Visualizations.TEMPLATE,
            height=altura,
            xaxis_title='Valor (R$)',
            yaxis_title='Natureza',
            yaxis={'categoryorder': 'total ascending'},
            bargap=0.2,
            margin=dict(l=250, r=100, t=60, b=50),
            xaxis=dict(
                range=[0, max_valor * 1.15],
                fixedrange=False
            )
        )
        
        fig.update_traces(width=0.6)
        
        return Visualizations._aplicar_animacoes(fig)

