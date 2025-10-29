# -*- coding: utf-8 -*-
"""
Analise detalhada do resultado operacional de R$ 15.467,43
Vamos descobrir o que esta sendo considerado como "operacional"
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
df['Subgrupo'] = df['Subgrupo'].fillna('').str.upper()
df['Grupo'] = df['Grupo'].fillna('').str.upper()

print("="*80)
print("ANALISE: O QUE E O RESULTADO OPERACIONAL DE R$ 15.467,43?")
print("="*80)

# Filtrar SEM transferências (como o dashboard faz)
df_sem_transf = df[~df['Natureza'].str.contains('TRANSF. ENTRE CONTAS', na=False)].copy()

print(f"\nTotal de transacoes (sem transferencias): {len(df_sem_transf)}")

# Calcular totais
total_entrada = df_sem_transf['Entrada'].sum()
total_saida = df_sem_transf['Saida'].sum()
saldo = df_sem_transf['Saldo'].sum()

print(f"\nTOTAL ENTRADAS (sem transferencias):  {BR(total_entrada)}")
print(f"TOTAL SAIDAS (sem transferencias):    {BR(abs(total_saida))}")
print(f"SALDO (sem transferencias):           {BR(saldo)}")

# Agora vamos decompor as ENTRADAS
print("\n" + "="*80)
print("DECOMPOSICAO DAS ENTRADAS (SEM TRANSFERENCIAS)")
print("="*80)

df_entradas = df_sem_transf[df_sem_transf['Entrada'] > 0].copy()

# Agrupar por Subgrupo e Natureza
entrada_por_natureza = df_entradas.groupby(['Subgrupo', 'Natureza'])['Entrada'].sum().reset_index()
entrada_por_natureza = entrada_por_natureza.sort_values('Entrada', ascending=False)

print(f"\n{'SUBGRUPO':<30} {'NATUREZA':<50} {'VALOR':>20}")
print("-"*100)

for _, row in entrada_por_natureza.iterrows():
    print(f"{row['Subgrupo']:<30} {row['Natureza'][:50]:<50} {BR(row['Entrada']):>20}")

# Totais por subgrupo
print("\n" + "="*80)
print("TOTAIS POR SUBGRUPO (ENTRADAS)")
print("="*80)

entrada_por_subgrupo = df_entradas.groupby('Subgrupo')['Entrada'].sum().reset_index()
entrada_por_subgrupo = entrada_por_subgrupo.sort_values('Entrada', ascending=False)

for _, row in entrada_por_subgrupo.iterrows():
    percentual = (row['Entrada'] / total_entrada * 100)
    print(f"{row['Subgrupo']:<40} {BR(row['Entrada']):>20} ({percentual:>5.1f}%)")

# Agora vamos decompor as SAÍDAS
print("\n" + "="*80)
print("DECOMPOSICAO DAS SAIDAS (SEM TRANSFERENCIAS)")
print("="*80)

df_saidas = df_sem_transf[df_sem_transf['Saida'] < 0].copy()

# Totais por subgrupo
saida_por_subgrupo = df_saidas.groupby('Subgrupo')['Saida'].sum().reset_index()
saida_por_subgrupo['Saida_Abs'] = saida_por_subgrupo['Saida'].abs()
saida_por_subgrupo = saida_por_subgrupo.sort_values('Saida_Abs', ascending=False)

for _, row in saida_por_subgrupo.iterrows():
    percentual = (row['Saida_Abs'] / abs(total_saida) * 100)
    print(f"{row['Subgrupo']:<40} {BR(row['Saida_Abs']):>20} ({percentual:>5.1f}%)")

# Análise crítica: O que é REALMENTE operacional?
print("\n" + "="*80)
print("ANALISE CRITICA: CLASSIFICACAO CORRETA")
print("="*80)

print("\nO dashboard esta considerando como 'operacional':")
print("  - TUDO que NAO seja 'TRANSF. ENTRE CONTAS'")
print("\nIsso INCLUI:")

# Verificar se aporte está sendo contado
df_aporte = df_sem_transf[df_sem_transf['Natureza'].str.contains('APORTE', na=False)]
if len(df_aporte) > 0:
    total_aporte = df_aporte['Entrada'].sum()
    print(f"  [X] APORTE DE CAPITAL SCP: {BR(total_aporte)} <- NAO E OPERACIONAL!")

# Verificar empréstimos
df_emprestimos = df_sem_transf[df_sem_transf['Natureza'].str.contains('EMPRESTIMO', na=False)]
if len(df_emprestimos) > 0:
    entrada_emp = df_emprestimos['Entrada'].sum()
    saida_emp = df_emprestimos['Saida'].sum()
    print(f"  [X] EMPRESTIMOS Entrada: {BR(entrada_emp)}, Saida: {BR(abs(saida_emp))} <- NAO E OPERACIONAL!")

# Verificar receitas financeiras
df_rec_fin = df_sem_transf[df_sem_transf['Natureza'].str.contains('RECEITA APLICACOES|OUTRAS RECEITAS FINANCEIRAS', na=False)]
if len(df_rec_fin) > 0:
    total_rec_fin = df_rec_fin['Entrada'].sum()
    print(f"  [X] RECEITAS FINANCEIRAS: {BR(total_rec_fin)} <- FINANCEIRO, nao operacional")

# Calcular o VERDADEIRO resultado operacional
print("\n" + "="*80)
print("CALCULO DO VERDADEIRO RESULTADO OPERACIONAL")
print("="*80)

# Receitas operacionais = vendas, serviços, etc (excluir aporte, empréstimos, receitas financeiras)
df_receitas_op = df_sem_transf[
    (df_sem_transf['Entrada'] > 0) &
    (~df_sem_transf['Natureza'].str.contains('APORTE', na=False)) &
    (~df_sem_transf['Natureza'].str.contains('EMPRESTIMO', na=False)) &
    (~df_sem_transf['Natureza'].str.contains('RECEITA APLICACOES', na=False)) &
    (~df_sem_transf['Natureza'].str.contains('OUTRAS RECEITAS FINANCEIRAS', na=False)) &
    (~df_sem_transf['Natureza'].str.contains('RESULTADO DE PARTIC. SOCIETARIAS', na=False))
].copy()

receitas_operacionais = df_receitas_op['Entrada'].sum()

# Despesas operacionais = todas as saídas exceto empréstimos pagos
df_despesas_op = df_sem_transf[
    (df_sem_transf['Saida'] < 0) &
    (~df_sem_transf['Natureza'].str.contains('EMPRESTIMO', na=False))
].copy()

despesas_operacionais = abs(df_despesas_op['Saida'].sum())

resultado_operacional_real = receitas_operacionais - despesas_operacionais

print(f"\nRECEITAS OPERACIONAIS (vendas, servicos):  {BR(receitas_operacionais)}")
print(f"DESPESAS OPERACIONAIS (todas as saidas):   {BR(despesas_operacionais)}")
print(f"{'='*80}")
print(f"RESULTADO OPERACIONAL REAL:                {BR(resultado_operacional_real)}")

if resultado_operacional_real < 0:
    print(f"\n[!] PREJUIZO OPERACIONAL: {BR(abs(resultado_operacional_real))}")
else:
    print(f"\n[OK] LUCRO OPERACIONAL: {BR(resultado_operacional_real)}")

# Mostrar principais receitas operacionais
print("\n" + "="*80)
print("PRINCIPAIS RECEITAS OPERACIONAIS")
print("="*80)

receitas_por_natureza = df_receitas_op.groupby('Natureza')['Entrada'].sum().reset_index()
receitas_por_natureza = receitas_por_natureza.sort_values('Entrada', ascending=False)

for _, row in receitas_por_natureza.head(10).iterrows():
    print(f"  {row['Natureza'][:60]:<60} {BR(row['Entrada']):>20}")

print("\n" + "="*80)
print("CONCLUSAO")
print("="*80)
print(f"""
O dashboard esta mostrando R$ 15.467,43 porque esta incluindo:
  - Aporte SCP de R$ 3.484.400,00 como "receita"
  - Receitas financeiras
  - Emprestimos

O VERDADEIRO resultado operacional e: {BR(resultado_operacional_real)}

Isso significa que o empreendimento esta com PREJUIZO OPERACIONAL,
mas o aporte de capital cobriu as perdas e deixou saldo positivo.
""")
