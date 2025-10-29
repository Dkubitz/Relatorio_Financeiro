"""
Módulo de processamento de dados
Responsabilidade: Lógica de negócio, transformações e agregações de dados
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from .utils import limpar_valor_monetario, extrair_ano_mes


class DataProcessor:
    """
    Classe responsável pelo processamento e transformação de dados financeiros
    Princípios: Single Responsibility, Clean Architecture
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa o processador com o DataFrame de dados financeiros
        
        Args:
            df: DataFrame com dados brutos
        """
        self.df_original = df.copy()
        self.df = self._processar_dados_iniciais(df)
        
        # Classificar tipos de transação (camada de domínio)
        self.df = self._classificar_tipo_transacao(self.df)
        
        # Cache para visões especializadas
        self._df_operacional_cache = None
        self._df_por_conta_cache = None
    
    def _processar_dados_iniciais(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processa e limpa os dados iniciais
        
        Args:
            df: DataFrame bruto
            
        Returns:
            DataFrame processado
        """
        df = df.copy()
        
        # Renomear colunas removendo "Content."
        df.columns = df.columns.str.replace('Content.', '', regex=False)
        
        # Converter data
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
        
        # Limpar valores monetários
        df['Entrada'] = df['Entrada (R$)'].apply(limpar_valor_monetario)
        df['Saida'] = df['Saída (R$)'].apply(limpar_valor_monetario)
        
        # NORMALIZAR SAÍDA: garantir que seja sempre negativa
        # Se vier positiva, inverter o sinal (conforme especificação do Excel)
        df.loc[df['Saida'] > 0, 'Saida'] = -df.loc[df['Saida'] > 0, 'Saida'].abs()
        
        # Calcular saldo (entrada + saída, sendo saída negativa)
        df['Saldo'] = df['Entrada'] + df['Saida']
        
        # Criar colunas auxiliares
        df['Ano'] = df['Data'].dt.year
        df['Mes'] = df['Data'].dt.month
        df['AnoMes'] = df['Data'].apply(extrair_ano_mes)
        df['Trimestre'] = df['Data'].dt.quarter
        
        # Processar coluna de Conta Bancária (Name)
        if 'Name' in df.columns:
            df['Conta'] = df['Name'].str.strip()
        else:
            df['Conta'] = 'NÃO INFORMADO'
        
        # Normalizar textos
        for col in ['Grupo', 'Subgrupo', 'Natureza', 'FORNECEDOR']:
            if col in df.columns:
                df[col] = df[col].fillna('NÃO INFORMADO').str.strip().str.upper()
        
        # Remover linhas com data inválida
        df = df.dropna(subset=['Data'])
        
        # Ordenar por data
        df = df.sort_values('Data')
        
        return df
    
    def _classificar_tipo_transacao(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Classifica cada transação por tipo conforme regras de negócio
        
        TIPOS:
        - OPERACIONAL: Receitas/despesas reais que impactam resultado
        - FINANCEIRO_EXTERNO: Movimentações financeiras reais (aportes, aplicações, taxas)
        - FINANCEIRO_INTERNO: Transferências entre contas (sem impacto consolidado)
        
        Args:
            df: DataFrame processado
            
        Returns:
            DataFrame com coluna 'TipoTransacao' adicionada
        """
        df = df.copy()
        
        # Função auxiliar para classificar baseado na Natureza e Subgrupo
        def classificar(row):
            natureza = str(row['Natureza']).upper()
            subgrupo = str(row['Subgrupo']).upper()
            
            # FINANCEIRO_INTERNO: Transferências entre contas (movimentações que se anulam)
            if 'TRANSF. ENTRE CONTAS' in natureza or 'TRANSFERÊNCIA ENTRE CONTAS' in natureza:
                return 'FINANCEIRO_INTERNO'
            
            # FINANCEIRO_INTERNO: Empréstimos internos (entrada e saída se cancelam)
            if 'EMPRÉSTIMO' in natureza and subgrupo == 'FINANCEIRO':
                return 'FINANCEIRO_INTERNO'
            
            # FINANCEIRO_EXTERNO: Movimentações financeiras reais
            if subgrupo == 'FINANCEIRO':
                # Aportes, receitas de aplicações, taxas bancárias são FINANCEIRO_EXTERNO
                if any(keyword in natureza for keyword in [
                    'APORTE', 'SCP', 'RECEITA APLICAÇÕES', 'APLICAÇÕES FINANCEIRAS',
                    'OUTRAS RECEITAS FINANCEIRAS', 'RESULTADO DE PARTIC. SOCIETÁRIAS'
                ]):
                    return 'FINANCEIRO_EXTERNO'
                # Empréstimos de terceiros são FINANCEIRO_EXTERNO
                if 'EMPRÉSTIMO' in natureza and 'ENTRE CONTAS' not in natureza:
                    return 'FINANCEIRO_EXTERNO'
                # Default para FINANCEIRO que não se encaixa nas regras acima
                return 'FINANCEIRO_EXTERNO'
            
            # OPERACIONAL: Tudo que não é financeiro (custo do ativo, administração, receitas)
            return 'OPERACIONAL'
        
        df['TipoTransacao'] = df.apply(classificar, axis=1)
        
        return df
    
    @property
    def df_operacional(self) -> pd.DataFrame:
        """
        Retorna visão OPERACIONAL dos dados (exclui FINANCEIRO_INTERNO)
        
        USO: Análises de despesas, receitas, fornecedores, grupos
        REMOVE: Transferências entre contas que inflam artificialmente os totais
        
        Returns:
            DataFrame apenas com transações OPERACIONAL e FINANCEIRO_EXTERNO
        """
        if self._df_operacional_cache is None:
            self._df_operacional_cache = self.df[
                self.df['TipoTransacao'] != 'FINANCEIRO_INTERNO'
            ].copy()
        return self._df_operacional_cache
    
    @property
    def df_por_conta(self) -> pd.DataFrame:
        """
        Retorna visão por CONTA BANCÁRIA (inclui TODAS as transações)
        
        USO: Auditoria de contas, controle de caixa individual, reconciliação bancária
        INCLUI: Todas as movimentações incluindo transferências
        
        Returns:
            DataFrame completo com todas as transações
        """
        if self._df_por_conta_cache is None:
            self._df_por_conta_cache = self.df.copy()
        return self._df_por_conta_cache
    
    def obter_df_filtrado(self, 
                          data_inicio: Optional[datetime] = None,
                          data_fim: Optional[datetime] = None,
                          grupos: Optional[List[str]] = None,
                          fornecedores: Optional[List[str]] = None,
                          naturezas: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Retorna DataFrame filtrado baseado nos parâmetros
        
        Args:
            data_inicio: Data inicial do filtro
            data_fim: Data final do filtro
            grupos: Lista de grupos para filtrar
            fornecedores: Lista de fornecedores para filtrar
            naturezas: Lista de naturezas para filtrar
            
        Returns:
            DataFrame filtrado
        """
        df = self.df.copy()
        
        # Filtro de data
        if data_inicio:
            df = df[df['Data'] >= pd.Timestamp(data_inicio)]
        if data_fim:
            df = df[df['Data'] <= pd.Timestamp(data_fim)]
        
        # Filtro de grupos
        if grupos and len(grupos) > 0:
            df = df[df['Grupo'].isin(grupos)]
        
        # Filtro de fornecedores
        if fornecedores and len(fornecedores) > 0:
            df = df[df['FORNECEDOR'].isin(fornecedores)]
        
        # Filtro de naturezas
        if naturezas and len(naturezas) > 0:
            df = df[df['Natureza'].isin(naturezas)]
        
        return df
    
    def calcular_kpis(self, df: Optional[pd.DataFrame] = None) -> Dict[str, float]:
        """
        Calcula KPIs principais
        
        Args:
            df: DataFrame opcional (usa self.df se None)
            
        Returns:
            Dicionário com KPIs
        """
        if df is None:
            df = self.df
        
        total_entrada = df['Entrada'].sum()
        total_saida = abs(df['Saida'].sum())
        saldo = total_entrada - total_saida
        
        # Variação mês atual vs anterior (se houver dados suficientes)
        if len(df) > 0 and 'AnoMes' in df.columns:
            meses_unicos = sorted(df['AnoMes'].unique())
            if len(meses_unicos) >= 2:
                mes_atual = meses_unicos[-1]
                mes_anterior = meses_unicos[-2]
                
                saldo_atual = df[df['AnoMes'] == mes_atual]['Saldo'].sum()
                saldo_anterior = df[df['AnoMes'] == mes_anterior]['Saldo'].sum()
                
                if saldo_anterior != 0:
                    variacao = ((saldo_atual - saldo_anterior) / abs(saldo_anterior)) * 100
                else:
                    variacao = 0.0
            else:
                variacao = 0.0
        else:
            variacao = 0.0
        
        return {
            'total_entrada': total_entrada,
            'total_saida': total_saida,
            'saldo': saldo,
            'variacao_percentual': variacao,
            'num_transacoes': len(df),
            'ticket_medio': abs(df['Saldo'].mean()) if len(df) > 0 else 0.0
        }
    
    def agregacao_temporal(self, df: Optional[pd.DataFrame] = None, 
                           freq: str = 'ME') -> pd.DataFrame:
        """
        Agrega dados por período temporal
        
        Args:
            df: DataFrame opcional
            freq: Frequência ('ME' = mensal, 'QE' = trimestral, 'YE' = anual)
            
        Returns:
            DataFrame agregado por tempo
        """
        if df is None:
            df = self.df
        
        # Agrupar por data
        df_temp = df.copy()
        df_temp = df_temp.set_index('Data')
        
        # Reagrupar por frequência (ME = Month End)
        agregado = df_temp.resample(freq).agg({
            'Entrada': 'sum',
            'Saida': 'sum',
            'Saldo': 'sum'
        }).reset_index()
        
        # Adicionar saldo acumulado
        agregado['Saldo_Acumulado'] = agregado['Saldo'].cumsum()
        
        return agregado
    
    def top_fornecedores(self, df: Optional[pd.DataFrame] = None, 
                        n: int = 10, tipo: str = 'saida') -> pd.DataFrame:
        """
        Retorna top N fornecedores por entrada ou saída
        
        Args:
            df: DataFrame opcional
            n: Número de fornecedores
            tipo: 'entrada' ou 'saida'
            
        Returns:
            DataFrame com top fornecedores
        """
        if df is None:
            df = self.df
        
        coluna = 'Entrada' if tipo == 'entrada' else 'Saida'
        
        top = df.groupby('FORNECEDOR')[coluna].sum().reset_index()
        top['Valor_Abs'] = top[coluna].abs()
        top = top.sort_values('Valor_Abs', ascending=False).head(n)
        
        return top
    
    def agregacao_por_grupo(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Agrega dados por grupo/projeto
        
        Args:
            df: DataFrame opcional
            
        Returns:
            DataFrame agregado por grupo
        """
        if df is None:
            df = self.df
        
        agregado = df.groupby('Grupo').agg({
            'Entrada': 'sum',
            'Saida': 'sum',
            'Saldo': 'sum'
        }).reset_index()
        
        agregado['Saida_Abs'] = agregado['Saida'].abs()
        agregado = agregado.sort_values('Saida_Abs', ascending=False)
        
        return agregado
    
    def agregacao_por_natureza(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Agrega dados por natureza/categoria
        
        Args:
            df: DataFrame opcional
            
        Returns:
            DataFrame agregado por natureza
        """
        if df is None:
            df = self.df
        
        agregado = df.groupby(['Subgrupo', 'Natureza']).agg({
            'Entrada': 'sum',
            'Saida': 'sum',
            'Saldo': 'sum'
        }).reset_index()
        
        agregado['Saida_Abs'] = agregado['Saida'].abs()
        agregado = agregado.sort_values('Saida_Abs', ascending=False)
        
        return agregado
    
    def obter_periodos_disponiveis(self) -> Tuple[datetime, datetime]:
        """
        Retorna período mínimo e máximo disponível nos dados
        
        Returns:
            Tuple com (data_minima, data_maxima)
        """
        return (self.df['Data'].min().to_pydatetime(), 
                self.df['Data'].max().to_pydatetime())
    
    def obter_valores_unicos(self, coluna: str) -> List[str]:
        """
        Retorna valores únicos de uma coluna, ordenados
        
        Args:
            coluna: Nome da coluna
            
        Returns:
            Lista de valores únicos
        """
        if coluna not in self.df.columns:
            return []
        
        return sorted(self.df[coluna].unique().tolist())
    
    def filtrar_excluir_financeiro(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Remove transações que contenham "TRANSF. ENTRE CONTAS" ou "EMPRÉSTIMOS" na natureza
        (movimentações internas sem significado para análise)
        
        Args:
            df: DataFrame opcional
            
        Returns:
            DataFrame sem transferências entre contas e empréstimos
        """
        if df is None:
            df = self.df
        
        # Filtrar transações que NÃO sejam:
        # - Transferências entre contas
        # - Empréstimos (entrada e saída que se cancelam)
        mask = (
            ~df['Natureza'].str.contains('TRANSF. ENTRE CONTAS', case=False, na=False) &
            ~df['Natureza'].str.contains('EMPRÉSTIMOS', case=False, na=False)
        )
        
        return df[mask].copy()
    
    def calcular_aportes_corrigidos(self, taxa_juros_mensal: float = 0.9477, 
                                    considerar_bariloche_como_pagamento: bool = False) -> Dict:
        """
        Calcula total de aportes SCP corrigidos por juros compostos
        
        Args:
            taxa_juros_mensal: Taxa de juros mensal em % (padrão: 0.9477%)
            considerar_bariloche_como_pagamento: Se True, gastos com BARILOCHE reduzem base de cálculo dos juros
            
        Returns:
            Dict com análise de aportes e memorial de cálculo detalhado
        """
        # Filtrar aportes SCP
        df_aportes = self.df[
            (self.df['Natureza'].str.contains('APORTE', case=False, na=False)) |
            (self.df['Natureza'].str.contains('SCP', case=False, na=False))
        ].copy()
        
        if len(df_aportes) == 0:
            return {
                'total_aportes_original': 0.0,
                'total_corrigido': 0.0,
                'total_juros': 0.0,
                'aportes_detalhados': pd.DataFrame(),
                'data_base_calculo': datetime.now(),
                'amortizacoes_bariloche': [],
                'memorial_calculo': []
            }
        
        # Data base para cálculo (hoje)
        data_base = datetime.now()
        
        # Calcular juros compostos para cada aporte
        taxa_decimal = taxa_juros_mensal / 100
        
        # Se considerar BARILOCHE como pagamento, obter todas as saídas BARILOCHE
        amortizacoes = []
        if considerar_bariloche_como_pagamento:
            df_bariloche = self.df[
                (self.df['Grupo'] == 'BARILOCHE') & 
                (self.df['Saida'] < 0)
            ].copy()
            
            if len(df_bariloche) > 0:
                # Ordenar por data
                df_bariloche = df_bariloche.sort_values('Data')
                amortizacoes = [
                    {
                        'data': row['Data'],
                        'valor': abs(row['Saida']),
                        'natureza': row['Natureza'],
                        'fornecedor': row['FORNECEDOR']
                    }
                    for _, row in df_bariloche.iterrows()
                ]
        
        if not considerar_bariloche_como_pagamento or len(amortizacoes) == 0:
            # CÁLCULO TRADICIONAL (sem considerar BARILOCHE) - por aporte individual
            memorial_calculo = []
            
            def calcular_valor_corrigido_simples(row):
                data_aporte = row['Data']
                valor_original = row['Entrada']
                
                meses = (data_base.year - data_aporte.year) * 12 + (data_base.month - data_aporte.month)
                meses += (data_base.day - data_aporte.day) / 30
                valor_corrigido = valor_original * ((1 + taxa_decimal) ** meses)
                
                # Adicionar ao memorial de cálculo
                memorial_calculo.append({
                    'data_aporte': data_aporte.strftime('%d/%m/%Y'),
                    'valor_original': valor_original,
                    'meses_decorridos': round(meses, 4),
                    'taxa_mensal': taxa_juros_mensal,
                    'fator_juros': round((1 + taxa_decimal) ** meses, 8),
                    'valor_corrigido': round(valor_corrigido, 2),
                    'juros_acumulados': round(valor_corrigido - valor_original, 2),
                    'formula': f"R$ {valor_original:,.2f} × (1 + {taxa_decimal:.6f})^{meses:.4f} = R$ {valor_corrigido:,.2f}"
                })
                
                return {
                    'valor_corrigido': valor_corrigido,
                    'meses_decorridos': meses,
                    'juros_acumulados': valor_corrigido - valor_original
                }
            
            df_aportes['Calculos'] = df_aportes.apply(calcular_valor_corrigido_simples, axis=1)
            df_aportes['Valor_Corrigido'] = df_aportes['Calculos'].apply(lambda x: x['valor_corrigido'])
            df_aportes['Meses_Decorridos'] = df_aportes['Calculos'].apply(lambda x: x['meses_decorridos'])
            df_aportes['Juros_Acumulados'] = df_aportes['Calculos'].apply(lambda x: x['juros_acumulados'])
            
            total_original = df_aportes['Entrada'].sum()
            total_corrigido = df_aportes['Valor_Corrigido'].sum()
            total_juros = df_aportes['Juros_Acumulados'].sum()
        
        else:
            # CÁLCULO COM AMORTIZAÇÕES BARILOCHE - consolidado (não por aporte individual)
            memorial_calculo = []
            
            # Construir linha do tempo GLOBAL com todos aportes e amortizações
            eventos = []
            
            # Adicionar todos os aportes
            for _, row in df_aportes.iterrows():
                eventos.append({
                    'data': row['Data'],
                    'tipo': 'aporte',
                    'valor': row['Entrada'],
                    'referencia': row
                })
            
            # Adicionar todas as amortizações BARILOCHE
            for amort in amortizacoes:
                eventos.append({
                    'data': amort['data'],
                    'tipo': 'amortizacao',
                    'valor': amort['valor'],
                    'referencia': amort
                })
            
            # Ordenar eventos cronologicamente
            eventos = sorted(eventos, key=lambda x: x['data'])
            
            # Simular evolução do capital mês a mês
            capital_acumulado = 0
            ultima_data = eventos[0]['data']
            
            # Adicionar cabeçalho do memorial
            memorial_calculo.append({
                'data_aporte': 'INÍCIO',
                'valor_original': 0,
                'meses_decorridos': 0,
                'taxa_mensal': taxa_juros_mensal,
                'fator_juros': 1.0,
                'valor_corrigido': 0,
                'juros_acumulados': 0,
                'formula': 'INÍCIO DO CÁLCULO - MODO BARILOCHE',
                'evento': 'Início',
                'capital_antes': 0,
                'capital_depois': 0
            })
            
            # Processar cada evento
            for i, evento in enumerate(eventos):
                # Calcular juros desde última data até este evento
                meses = (evento['data'].year - ultima_data.year) * 12
                meses += (evento['data'].month - ultima_data.month)
                meses += (evento['data'].day - ultima_data.day) / 30
                
                capital_antes_juros = capital_acumulado
                
                if meses > 0 and capital_acumulado > 0:
                    # Aplicar juros compostos sobre capital acumulado
                    capital_acumulado = capital_acumulado * ((1 + taxa_decimal) ** meses)
                
                capital_antes_evento = capital_acumulado
                
                # Aplicar o evento
                if evento['tipo'] == 'aporte':
                    capital_acumulado += evento['valor']
                    evento_desc = f"APORTE: R$ {evento['valor']:,.2f}"
                elif evento['tipo'] == 'amortizacao':
                    capital_acumulado -= evento['valor']
                    if capital_acumulado < 0:
                        capital_acumulado = 0
                    evento_desc = f"AMORTIZAÇÃO BARILOCHE: -R$ {evento['valor']:,.2f}"
                
                # Adicionar ao memorial
                memorial_calculo.append({
                    'data_aporte': evento['data'].strftime('%d/%m/%Y'),
                    'valor_original': evento['valor'],
                    'meses_decorridos': round(meses, 4),
                    'taxa_mensal': taxa_juros_mensal,
                    'fator_juros': round((1 + taxa_decimal) ** meses, 8) if meses > 0 else 1.0,
                    'valor_corrigido': round(capital_acumulado, 2),
                    'juros_acumulados': round(capital_acumulado - capital_antes_juros, 2),
                    'formula': f"Capital: R$ {capital_antes_juros:,.2f} × (1 + {taxa_decimal:.6f})^{meses:.4f} + {evento_desc} = R$ {capital_acumulado:,.2f}",
                    'evento': evento_desc,
                    'capital_antes': round(capital_antes_juros, 2),
                    'capital_depois': round(capital_acumulado, 2)
                })
                
                ultima_data = evento['data']
            
            # Calcular juros desde último evento até data_base
            meses_final = (data_base.year - ultima_data.year) * 12
            meses_final += (data_base.month - ultima_data.month)
            meses_final += (data_base.day - ultima_data.day) / 30
            
            capital_antes_final = capital_acumulado
            
            if meses_final > 0 and capital_acumulado > 0:
                capital_acumulado = capital_acumulado * ((1 + taxa_decimal) ** meses_final)
            
            # Adicionar cálculo final ao memorial
            memorial_calculo.append({
                'data_aporte': data_base.strftime('%d/%m/%Y'),
                'valor_original': 0,
                'meses_decorridos': round(meses_final, 4),
                'taxa_mensal': taxa_juros_mensal,
                'fator_juros': round((1 + taxa_decimal) ** meses_final, 8) if meses_final > 0 else 1.0,
                'valor_corrigido': round(capital_acumulado, 2),
                'juros_acumulados': round(capital_acumulado - capital_antes_final, 2),
                'formula': f"FINAL: R$ {capital_antes_final:,.2f} × (1 + {taxa_decimal:.6f})^{meses_final:.4f} = R$ {capital_acumulado:,.2f}",
                'evento': 'CÁLCULO FINAL',
                'capital_antes': round(capital_antes_final, 2),
                'capital_depois': round(capital_acumulado, 2)
            })
            
            # Valores consolidados
            total_original = df_aportes['Entrada'].sum()
            total_corrigido = capital_acumulado
            total_juros = total_corrigido - total_original
            
            # Para cada aporte individual, calcular proporcionalmente (para tabela detalhada)
            def calcular_proporcional(row):
                valor_original = row['Entrada']
                proporcao = valor_original / total_original if total_original > 0 else 0
                
                meses = (data_base.year - row['Data'].year) * 12
                meses += (data_base.month - row['Data'].month)
                meses += (data_base.day - row['Data'].day) / 30
                
                # Valor corrigido proporcional ao total
                valor_corrigido_prop = total_corrigido * proporcao
                juros_prop = valor_corrigido_prop - valor_original
                
                return {
                    'valor_corrigido': valor_corrigido_prop,
                    'meses_decorridos': meses,
                    'juros_acumulados': juros_prop
                }
            
            df_aportes['Calculos'] = df_aportes.apply(calcular_proporcional, axis=1)
            df_aportes['Valor_Corrigido'] = df_aportes['Calculos'].apply(lambda x: x['valor_corrigido'])
            df_aportes['Meses_Decorridos'] = df_aportes['Calculos'].apply(lambda x: x['meses_decorridos'])
            df_aportes['Juros_Acumulados'] = df_aportes['Calculos'].apply(lambda x: x['juros_acumulados'])
        
        return {
            'total_aportes_original': total_original,
            'total_corrigido': total_corrigido,
            'total_juros': total_juros,
            'aportes_detalhados': df_aportes,
            'data_base_calculo': data_base,
            'taxa_juros': taxa_juros_mensal,
            'amortizacoes_bariloche': amortizacoes,
            'memorial_calculo': memorial_calculo
        }
    
    def analise_subgrupo_financeiro(self) -> Dict:
        """
        Análise detalhada do subgrupo FINANCEIRO
        
        Returns:
            Dict com análise financeira completa
        """
        df_fin = self.df[self.df['Subgrupo'] == 'FINANCEIRO'].copy()
        
        if len(df_fin) == 0:
            return {
                'total_entradas': 0.0,
                'total_saidas': 0.0,
                'saldo': 0.0,
                'num_transacoes': 0,
                'por_natureza': pd.DataFrame()
            }
        
        # Agregação por natureza
        por_natureza = df_fin.groupby('Natureza').agg({
            'Entrada': 'sum',
            'Saida': 'sum',
            'Saldo': 'sum'
        }).reset_index()
        
        por_natureza = por_natureza.sort_values('Saldo', ascending=False)
        
        return {
            'total_entradas': df_fin['Entrada'].sum(),
            'total_saidas': abs(df_fin['Saida'].sum()),
            'saldo': df_fin['Saldo'].sum(),
            'num_transacoes': len(df_fin),
            'por_natureza': por_natureza,
            'df_financeiro': df_fin
        }
    
    def calcular_saldos_por_conta(self, df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Calcula saldos por conta bancária
        
        Args:
            df: DataFrame opcional
            
        Returns:
            Dicionário com saldos por conta e consolidados
        """
        if df is None:
            df = self.df
        
        if 'Conta' not in df.columns:
            return {}
        
        # Saldos por conta individual
        saldos_por_conta = {}
        for conta in df['Conta'].unique():
            df_conta = df[df['Conta'] == conta]
            saldos_por_conta[conta] = {
                'saldo': df_conta['Saldo'].sum(),
                'entradas': df_conta['Entrada'].sum(),
                'saidas': abs(df_conta['Saida'].sum()),
                'transacoes': len(df_conta)
            }
        
        # Consolidar NORTHSIDE (Lifecon5 + Lifecon7)
        saldo_lifecon5 = saldos_por_conta.get('FluxoLifecon5', {}).get('saldo', 0)
        saldo_lifecon7 = saldos_por_conta.get('FluxoLifecon7', {}).get('saldo', 0)
        
        saldos_consolidados = {
            'NORTHSIDE': saldo_lifecon5 + saldo_lifecon7,
            'ÁGATA': saldos_por_conta.get('FluxoAgata', {}).get('saldo', 0),
            'BARILOCHE': saldos_por_conta.get('FluxoBariloche', {}).get('saldo', 0)
        }
        
        return {
            'por_conta': saldos_por_conta,
            'consolidados': saldos_consolidados,
            'total': sum(saldos_consolidados.values())
        }

