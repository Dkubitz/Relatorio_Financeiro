"""
Script para obter o saldo da conta bancária da Ágata
exatamente como calculado no Streamlit (DataProcessor + calcular_saldos_por_conta).
"""
import csv
import sys
from pathlib import Path


def limpar_valor_monetario(valor_str: str) -> float:
    """Mesma lógica de src.utils (formato BR: 1.234,56)."""
    if valor_str is None or str(valor_str).strip() == '':
        return 0.0
    valor_limpo = str(valor_str).strip().replace('.', '').replace(',', '.')
    try:
        return float(valor_limpo)
    except ValueError:
        return 0.0


def formatar_moeda(valor: float) -> str:
    """Formato R$ X.XXX,XX (BR: ponto milhares, vírgula decimais)."""
    sinal = "-" if valor < 0 else ""
    valor_abs = abs(valor)
    int_part = int(valor_abs)
    dec_part = round((valor_abs - int_part) * 100)
    miles = f"{int_part:,}".replace(",", ".")
    return f"{sinal}R$ {miles},{dec_part:02d}"

def main_com_csv_stdlib():
    """Cálculo igual ao Streamlit: só FluxoAgata, Entrada + Saída (saída negativa)."""
    arquivo_csv = Path(__file__).resolve().parent / "Fluxo Financeiro.csv"
    if not arquivo_csv.exists():
        print(f"Arquivo não encontrado: {arquivo_csv}")
        return None

    saldo = 0.0
    with open(arquivo_csv, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            conta = (row.get('Name') or '').strip()
            if conta != 'FluxoAgata':
                continue
            entrada = limpar_valor_monetario(row.get('Content.Entrada (R$)', 0))
            saida = limpar_valor_monetario(row.get('Content.Saída (R$)', 0))
            if saida > 0:
                saida = -saida
            saldo += entrada + saida
    return saldo


def main_com_processor():
    """Usa DataProcessor (igual ao Streamlit)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import pandas as pd
    from src.data_processor import DataProcessor
    from src.utils import formatar_moeda

    arquivo_csv = Path(__file__).resolve().parent / "Fluxo Financeiro.csv"
    if not arquivo_csv.exists():
        return None

    df = pd.read_csv(
        arquivo_csv,
        sep=';',
        encoding='utf-8',
        usecols=[
            'Content.Data', 'Content.Grupo', 'Content.Subgrupo',
            'Content.Natureza', 'Content.FORNECEDOR',
            'Content.Entrada (R$)', 'Content.Saída (R$)', 'Name'
        ]
    )
    processor = DataProcessor(df)
    saldos = processor.calcular_saldos_por_conta(processor.df)
    if not saldos:
        return None
    return saldos['consolidados']['ÁGATA'], formatar_moeda


def main():
    # Tentar com DataProcessor (igual ao Streamlit)
    try:
        result = main_com_processor()
        if result is not None:
            valor_agata, fmt = result
            print("Saldo da conta bancária da Ágata (igual ao Streamlit):")
            print(fmt(valor_agata))
            print(f"(Valor numérico: {valor_agata:.2f})")
            return
    except Exception as e:
        print(f"DataProcessor indisponível ({e}), usando cálculo direto do CSV...")

    # Fallback: mesma regra (FluxoAgata, Entrada + Saída negativa)
    valor_agata = main_com_csv_stdlib()
    if valor_agata is not None:
        print("Saldo da conta bancária da Ágata (mesma lógica do Streamlit):")
        print(formatar_moeda(valor_agata))
        print(f"(Valor numérico: {valor_agata:.2f})")
    else:
        print("Não foi possível calcular o saldo.")
    return


if __name__ == "__main__":
    main()
