"""
Módulo de utilitários
Responsabilidade: Funções auxiliares e helpers reutilizáveis
"""

import pandas as pd
import numpy as np
from typing import Tuple
import re


def limpar_valor_monetario(valor_str: str) -> float:
    """
    Converte string de valor monetário para float
    
    Args:
        valor_str: String no formato brasileiro (ex: "1.234,56")
        
    Returns:
        float: Valor numérico
    """
    if pd.isna(valor_str) or valor_str == '':
        return 0.0
    
    # Remove espaços e converte vírgula para ponto
    valor_limpo = str(valor_str).strip().replace('.', '').replace(',', '.')
    
    try:
        return float(valor_limpo)
    except ValueError:
        return 0.0


def formatar_moeda(valor: float, simbolo: str = "R$") -> str:
    """
    Formata valor numérico para string monetária brasileira
    
    Args:
        valor: Valor numérico
        simbolo: Símbolo da moeda
        
    Returns:
        str: Valor formatado (ex: "R$ 1.234,56")
    """
    if pd.isna(valor):
        valor = 0.0
    
    sinal = "-" if valor < 0 else ""
    valor_abs = abs(valor)
    
    # Formata com separador de milhares e 2 casas decimais
    valor_formatado = f"{valor_abs:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    return f"{sinal}{simbolo} {valor_formatado}"


def formatar_percentual(valor: float, decimais: int = 1) -> str:
    """
    Formata valor numérico para percentual
    
    Args:
        valor: Valor numérico (ex: 0.1523 para 15.23%)
        decimais: Número de casas decimais
        
    Returns:
        str: Valor formatado (ex: "15.2%")
    """
    if pd.isna(valor) or np.isinf(valor):
        return "N/A"
    
    return f"{valor:.{decimais}f}%"


def calcular_variacao_percentual(valor_atual: float, valor_anterior: float) -> float:
    """
    Calcula variação percentual entre dois valores
    
    Args:
        valor_atual: Valor atual
        valor_anterior: Valor anterior
        
    Returns:
        float: Variação percentual
    """
    if valor_anterior == 0:
        return 0.0
    
    return ((valor_atual - valor_anterior) / abs(valor_anterior)) * 100


def extrair_ano_mes(data: pd.Timestamp) -> str:
    """
    Extrai ano e mês de uma data no formato "YYYY-MM"
    
    Args:
        data: Data pandas Timestamp
        
    Returns:
        str: String no formato "YYYY-MM"
    """
    if pd.isna(data):
        return ""
    
    return data.strftime("%Y-%m")


def extrair_mes_ano_legivel(data: pd.Timestamp) -> str:
    """
    Extrai mês e ano de uma data no formato legível
    
    Args:
        data: Data pandas Timestamp
        
    Returns:
        str: String no formato "Jan/2023"
    """
    if pd.isna(data):
        return ""
    
    meses = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }
    
    return f"{meses[data.month]}/{data.year}"


def normalizar_texto(texto: str) -> str:
    """
    Normaliza texto removendo espaços extras e convertendo para maiúsculas
    
    Args:
        texto: Texto a normalizar
        
    Returns:
        str: Texto normalizado
    """
    if pd.isna(texto):
        return ""
    
    return str(texto).strip().upper()


def criar_periodo_legivel(data_inicio: pd.Timestamp, data_fim: pd.Timestamp) -> str:
    """
    Cria string legível de período
    
    Args:
        data_inicio: Data inicial
        data_fim: Data final
        
    Returns:
        str: Período formatado (ex: "Jan/2023 a Dez/2023")
    """
    inicio = extrair_mes_ano_legivel(data_inicio)
    fim = extrair_mes_ano_legivel(data_fim)
    
    return f"{inicio} a {fim}"

