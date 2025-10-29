# -*- coding: utf-8 -*-
"""
Script para investigar o liquido de R$ 90.074,15 nas transferencias
"""

import pandas as pd

def BR(x):
    return f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# Carregar CSV
df = pd.read_csv('Fluxo Financeiro.csv', sep=';', encoding='utf-8')

# Limpar nomes de colunas
df.columns = df.columns.str.replace('Content.', '', regex=False)

# Limpar valores monetários
def limpar_valor(valor_str):
    if pd.isna(valor_str) or valor_str == '':
        return 0.0
    valor_limpo = str(valor_str).strip().replace('.', '').replace(',', '.')
    try:
        return float(valor_limpo)
    except:
        return 0.0

df['Entrada'] = df['Entrada (R$)'].apply(limpar_valor)
df['Saida'] = df['Saída (R$)'].apply(limpar_valor)

# Garantir que saída seja negativa
df.loc[df['Saida'] > 0, 'Saida'] = -df.loc[df['Saida'] > 0, 'Saida'].abs()

# Calcular saldo
df['Saldo'] = df['Entrada'] + df['Saida']

# Normalizar textos
df['Natureza'] = df['Natureza'].fillna('').str.upper()
df['Conta'] = df['Name'].fillna('').str.strip()
df['Grupo'] = df['Grupo'].fillna('').str.upper()

print("="*80)
print("INVESTIGACAO: LIQUIDO DE TRANSFERENCIAS R$ 90.074,15")
print("="*80)

# Filtrar transferências
df_transf = df[df['Natureza'].str.contains('TRANSF. ENTRE CONTAS', na=False)].copy()

print(f"\nTotal de transacoes de transferencia: {len(df_transf)}")

# Calcular por conta
print("\n" + "="*80)
print("SALDO DE TRANSFERENCIAS POR CONTA BANCARIA")
print("="*80)

for conta in df_transf['Conta'].unique():
    df_conta = df_transf[df_transf['Conta'] == conta]
    entrada = df_conta['Entrada'].sum()
    saida = df_conta['Saida'].sum()
    saldo = df_conta['Saldo'].sum()
    
    print(f"\n{conta}")
    print(f"   Entradas:   {BR(entrada)}")
    print(f"   Saidas:     {BR(abs(saida))}")
    print(f"   Saldo:      {BR(saldo)}")
    print(f"   Transacoes: {len(df_conta)}")

# Total de transferências
total_entrada_transf = df_transf['Entrada'].sum()
total_saida_transf = df_transf['Saida'].sum()
total_saldo_transf = df_transf['Saldo'].sum()

print("\n" + "="*80)
print("TOTAL DE TRANSFERENCIAS (deveria ser ~zero)")
print("="*80)
print(f"Entradas:   {BR(total_entrada_transf)}")
print(f"Saidas:     {BR(abs(total_saida_transf))}")
print(f"Liquido:    {BR(total_saldo_transf)} <- ESTE E O VALOR QUE PROCURAMOS!")

# Saldo total por conta (todas as transações)
print("\n" + "="*80)
print("SALDO TOTAL POR CONTA (TODAS AS TRANSACOES)")
print("="*80)

for conta in df['Conta'].unique():
    df_conta = df[df['Conta'] == conta]
    saldo_total = df_conta['Saldo'].sum()
    print(f"{conta:20} -> {BR(saldo_total)}")

# Consolidado
saldo_lifecon5 = df[df['Conta'] == 'FluxoLifecon5']['Saldo'].sum()
saldo_lifecon7 = df[df['Conta'] == 'FluxoLifecon7']['Saldo'].sum()
saldo_agata = df[df['Conta'] == 'FluxoAgata']['Saldo'].sum()
saldo_bariloche = df[df['Conta'] == 'FluxoBariloche']['Saldo'].sum()

print("\n" + "="*80)
print("CONSOLIDADO POR PROJETO")
print("="*80)
print(f"NORTHSIDE (Lifecon5 + Lifecon7): {BR(saldo_lifecon5 + saldo_lifecon7)}")
print(f"AGATA:                            {BR(saldo_agata)}")
print(f"BARILOCHE:                        {BR(saldo_bariloche)}")
print(f"{'-'*80}")
print(f"TOTAL:                            {BR(saldo_lifecon5 + saldo_lifecon7 + saldo_agata + saldo_bariloche)}")

# Transferências por grupo
print("\n" + "="*80)
print("TRANSFERENCIAS DETALHADAS POR GRUPO")
print("="*80)

for grupo in ['NORTHSIDE', 'AGATA', 'BARILOCHE']:
    df_grupo = df_transf[df_transf['Grupo'] == grupo]
    if len(df_grupo) > 0:
        entrada = df_grupo['Entrada'].sum()
        saida = df_grupo['Saida'].sum()
        saldo = df_grupo['Saldo'].sum()
        
        print(f"\n{grupo}")
        print(f"   Entradas:   {BR(entrada)}")
        print(f"   Saidas:     {BR(abs(saida))}")
        print(f"   Liquido:    {BR(saldo)}")
        print(f"   Transacoes: {len(df_grupo)}")

print("\n" + "="*80)
print("ANALISE CONCLUIDA")
print("="*80)
