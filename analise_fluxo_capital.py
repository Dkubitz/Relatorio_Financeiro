# -*- coding: utf-8 -*-
"""
Analise do fluxo de capital - AGATA recebe aporte e distribui
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
print("ANALISE: FLUXO DE CAPITAL - AGATA RECEBE APORTE E DISTRIBUI")
print("="*80)

# 1. Verificar o aporte SCP na conta AGATA
print("\n" + "="*80)
print("1. APORTE SCP NA CONTA AGATA")
print("="*80)

df_aporte = df[
    (df['Natureza'].str.contains('APORTE', na=False)) &
    (df['Grupo'] == 'AGATA')
].copy()

if len(df_aporte) > 0:
    total_aporte = df_aporte['Entrada'].sum()
    print(f"\nTotal de Aportes SCP recebidos por AGATA: {BR(total_aporte)}")
    print(f"Numero de transacoes: {len(df_aporte)}")
else:
    print("\nNenhum aporte encontrado diretamente na AGATA")

# 2. Fluxo de transferências DA AGATA para outras contas
print("\n" + "="*80)
print("2. TRANSFERENCIAS ORIGINADAS NA CONTA AGATA (FluxoAgata)")
print("="*80)

df_transf_agata = df[
    (df['Conta'] == 'FluxoAgata') &
    (df['Natureza'].str.contains('TRANSF. ENTRE CONTAS', na=False))
].copy()

print(f"\nTotal de transacoes de transferencia em FluxoAgata: {len(df_transf_agata)}")

# Separar o que SAIU da Agata
df_agata_saida = df_transf_agata[df_transf_agata['Saida'] < 0].copy()
print(f"\nTRANSFERENCIAS QUE SAIRAM DA AGATA:")
print(f"  Total enviado: {BR(abs(df_agata_saida['Saida'].sum()))}")
print(f"  Numero de transferencias: {len(df_agata_saida)}")

# Separar o que ENTROU na Agata
df_agata_entrada = df_transf_agata[df_transf_agata['Entrada'] > 0].copy()
print(f"\nTRANSFERENCIAS QUE ENTRARAM NA AGATA:")
print(f"  Total recebido: {BR(df_agata_entrada['Entrada'].sum())}")
print(f"  Numero de transferencias: {len(df_agata_entrada)}")

# Líquido
liquido_transf_agata = df_transf_agata['Saldo'].sum()
print(f"\nLIQUIDO DE TRANSFERENCIAS NA AGATA: {BR(liquido_transf_agata)}")

# 3. Para onde foi o dinheiro da AGATA?
print("\n" + "="*80)
print("3. DESTINOS DAS TRANSFERENCIAS DA AGATA")
print("="*80)

# Buscar transferências que vieram de AGATA em outras contas
for conta in ['FluxoLifecon5', 'FluxoLifecon7', 'FluxoBariloche']:
    df_recebidas = df[
        (df['Conta'] == conta) &
        (df['Natureza'].str.contains('TRANSF. ENTRE CONTAS', na=False)) &
        (df['Natureza'].str.contains('AGATA', na=False)) &
        (df['Entrada'] > 0)
    ]
    
    if len(df_recebidas) > 0:
        total = df_recebidas['Entrada'].sum()
        print(f"\n{conta} recebeu de AGATA: {BR(total)} ({len(df_recebidas)} transacoes)")

# 4. Análise completa do fluxo de capital
print("\n" + "="*80)
print("4. FLUXO COMPLETO DE CAPITAL")
print("="*80)

# AGATA - Visão completa (não apenas transferências)
df_agata_completo = df[df['Conta'] == 'FluxoAgata'].copy()

total_entrada_agata = df_agata_completo['Entrada'].sum()
total_saida_agata = df_agata_completo['Saida'].sum()
saldo_agata = df_agata_completo['Saldo'].sum()

print(f"\nCONTA AGATA (FluxoAgata) - VISAO COMPLETA:")
print(f"  Total Entradas:  {BR(total_entrada_agata)}")
print(f"  Total Saidas:    {BR(abs(total_saida_agata))}")
print(f"  Saldo Final:     {BR(saldo_agata)}")

# Decompor as entradas
df_agata_entradas = df_agata_completo[df_agata_completo['Entrada'] > 0].copy()

print(f"\n  COMPOSICAO DAS ENTRADAS:")
for natureza in df_agata_entradas['Natureza'].unique():
    df_nat = df_agata_entradas[df_agata_entradas['Natureza'] == natureza]
    total = df_nat['Entrada'].sum()
    print(f"    {natureza[:60]:60} {BR(total)}")

# 5. Reconciliação: De onde vem os R$ 90.074,15?
print("\n" + "="*80)
print("5. RECONCILIACAO: R$ 90.074,15")
print("="*80)

aporte_scp = 3484400.00
resultado_operacional = 15467.43
saldo_real_contas = 105541.58

print(f"\nAporte SCP recebido por AGATA:     {BR(aporte_scp)}")
print(f"Resultado Operacional (sem transf): {BR(resultado_operacional)}")
print(f"Saldo Real nas Contas:              {BR(saldo_real_contas)}")
print(f"\nDiferenca (Capital nao gasto):      {BR(saldo_real_contas - resultado_operacional)}")

# Hipótese: AGATA recebeu aporte, distribuiu para contas, e essas contas gastaram
# O líquido de transferências mostra quanto "ficou retido" após a distribuição

print("\n" + "="*80)
print("6. FLUXO DE CAPITAL CONSOLIDADO")
print("="*80)

# Todas as transferências
df_transf_all = df[df['Natureza'].str.contains('TRANSF. ENTRE CONTAS', na=False)].copy()

entrada_transf_total = df_transf_all['Entrada'].sum()
saida_transf_total = df_transf_all['Saida'].sum()
liquido_transf_total = df_transf_all['Saldo'].sum()

print(f"\nTOTAL DE TRANSFERENCIAS NO SISTEMA:")
print(f"  Entradas:  {BR(entrada_transf_total)}")
print(f"  Saidas:    {BR(abs(saida_transf_total))}")
print(f"  Liquido:   {BR(liquido_transf_total)}")

print("\n" + "="*80)
print("INTERPRETACAO:")
print("="*80)
print("""
O liquido de R$ 90.074,15 representa:

1. AGATA recebeu R$ 3.484.400,00 de aporte SCP
2. AGATA distribuiu esse capital para outras contas via transferencias
3. As contas gastaram em despesas operacionais
4. Sobrou R$ 90.074,15 de capital que foi transferido MAS nao foi gasto

Este valor esta "retido" nas contas como capital de giro disponivel,
alem do resultado operacional de R$ 15.467,43.

Total em caixa = Resultado Operacional + Capital nao gasto
R$ 105.541,58 = R$ 15.467,43 + R$ 90.074,15
""")




