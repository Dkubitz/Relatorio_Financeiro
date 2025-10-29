# Lendo e somando os valores informados (Entradas e Saídas) para conferir o caixa e analisar o delta de R$ 90.074,15
from decimal import Decimal, getcontext

getcontext().prec = 12

def BR(x: Decimal) -> str:
    return f"R$ {x:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

entradas = [
    # Entradas
    Decimal('3484400.00'),  # ÁGATA – APORTE DE CAPITAL SCP
    Decimal('2618995.30'),  # NORTHSIDE – TRANSF. ENTRE CONTAS AGATA (ENTRADA)
    Decimal('660108.90'),   # NORTHSIDE – RECEITAS DE VENDA DE IMÓVEIS
    Decimal('390366.46'),   # NORTHSIDE – TRANSF. ENTRE CONTAS LIFECON (ENTRADA)
    Decimal('348876.63'),   # ÁGATA – TRANSF. ENTRE CONTAS LIFECON (ENTRADA)
    Decimal('222510.00'),   # BARILOCHE – TRANSF. ENTRE CONTAS ÁGATA (ENTRADA)
    Decimal('50000.00'),    # ÁGATA – EMPRÉSTIMOS (ENTRADA)
    Decimal('37120.07'),    # ÁGATA – TRANSF. ENTRE CONTAS ÁGATA (ENTRADA)
    Decimal('7100.00'),     # ÁGATA – TRANSF. ENTRE CONTAS LIFECON (SAIDA) -> listado em Entradas (conforme dado)
    Decimal('5000.00'),     # BARILOCHE – TRANSF. ENTRE CONTAS LIFECON (ENTRADA)
    Decimal('4391.53'),     # ÁGATA – RECEITA APLICAÇÕES FINANCEIRAS
    Decimal('1817.34'),     # BARILOCHE – TRANSF. ENTRE CONTAS BARILOCHE (ENTRADA)
    Decimal('1558.30'),     # BARILOCHE – OUTRAS RECEITAS FINANCEIRAS
    Decimal('1482.36'),     # NORTHSIDE – RECEITA APLICAÇÕES FINANCEIRAS
    Decimal('31.52'),       # BARILOCHE – RECEITA APLICAÇÕES FINANCEIRAS
    Decimal('10.61'),       # NORTHSIDE – OUTRAS RECEITAS FINANCEIRAS
    Decimal('0.01'),        # BARILOCHE – TAXAS BANCÁRIAS (entrada)
]

saidas = [
    # Saídas
    Decimal('2468995.30'),  # ÁGATA – TRANSF. ENTRE CONTAS LIFECON (SAIDA)
    Decimal('1260705.02'),  # NORTHSIDE – OBRAS DE INFRAESTRUTURA
    Decimal('593993.45'),   # NORTHSIDE – OBRAS DE EDIFICAÇÕES
    Decimal('450292.31'),   # NORTHSIDE – TRANSF. ENTRE CONTAS LIFECON (SAIDA)
    Decimal('235680.02'),   # NORTHSIDE – IPTU / ITR
    Decimal('226876.63'),   # NORTHSIDE – TRANSF. ENTRE CONTAS ÁGATA (SAIDA)
    Decimal('222510.00'),   # ÁGATA – TRANSF. ENTRE CONTAS BARILOCHE (SAIDA)
    Decimal('220000.00'),   # NORTHSIDE – COMISSÃO/INTERMEDIAÇÃO
    Decimal('193464.44'),   # NORTHSIDE – ASSESSORIA TÉCNICA
    Decimal('168406.25'),   # NORTHSIDE – RESULTADO DE PARTIC. SOCIETÁRIAS (PAGAR)
    Decimal('159120.07'),   # ÁGATA – TRANSF. ENTRE CONTAS ÁGATA (SAIDA)
    Decimal('139331.61'),   # NORTHSIDE – MATERIAL ELÉTRICO
    Decimal('121249.58'),   # BARILOCHE – MURO DE CONTENÇÃO
    Decimal('113290.58'),   # BARILOCHE – CUSTO DA ÁREA
    Decimal('104005.42'),   # NORTHSIDE – PROJETOS COMPLEMENTARES
    Decimal('85146.50'),    # NORTHSIDE – MARKETING
    Decimal('84114.69'),    # NORTHSIDE – IMPOSTOS (ISSQN, IRRF...)
    Decimal('79924.20'),    # ÁGATA – ASSESSORIA DE INFORMÁTICA
    Decimal('66152.21'),    # NORTHSIDE – ASSESSORIA CONTÁBIL
    Decimal('63494.32'),    # NORTHSIDE – PROJETOS AMBIENTAIS
    Decimal('62696.52'),    # ÁGATA – ASSESSORIA TÉCNICA
    Decimal('54106.00'),    # NORTHSIDE – EXECUÇÃO SISTEMA DE ELETRIFICAÇÃO
    Decimal('50000.00'),    # ÁGATA – EMPRÉSTIMOS (SAIDA)
    Decimal('49201.84'),    # NORTHSIDE – PROJETOS URBANÍSTICOS
    Decimal('46119.68'),    # NORTHSIDE – DESPESAS INICIAIS
    Decimal('44497.83'),    # BARILOCHE – IPTU / ITR
    Decimal('41592.66'),    # ÁGATA – ASSESSORIA CONTÁBIL
    Decimal('32943.70'),    # NORTHSIDE – CUSTO DA ÁREA (ROÇADA...)
    Decimal('31409.24'),    # NORTHSIDE – SUPRESSÃO VEGETAL
    Decimal('28995.30'),    # BARILOCHE – TAXAS E IMPOSTOS (ITBI...)
    Decimal('26232.79'),    # BARILOCHE – PROJETOS DE EDIFICAÇÕES
    Decimal('23013.17'),    # NORTHSIDE – PROJETOS DE EDIFICAÇÕES
    Decimal('18950.00'),    # BARILOCHE – ASSESSORIA CONTÁBIL
    Decimal('18402.78'),    # BARILOCHE – FORNECIMENTO DE MATERIAL
    Decimal('17980.00'),    # BARILOCHE – LIMPEZA DE ÁREA E TERRAPLANAGEM
    Decimal('13544.74'),    # NORTHSIDE – COFINS
    Decimal('13220.59'),    # NORTHSIDE – REGISTRO DE IMÓVEIS
    Decimal('11164.96'),    # NORTHSIDE – CSLL IRPJ
    Decimal('8212.40'),     # BARILOCHE – DESPESAS INICIAIS
    Decimal('7390.28'),     # ÁGATA – TAXAS BANCÁRIAS
    Decimal('7300.00'),     # NORTHSIDE – SERVIÇOS DE TOPOGRAFIA
    Decimal('7100.00'),     # NORTHSIDE – TRANSF. ENTRE CONTAS AGATA (SAIDA)
    Decimal('5000.00'),     # NORTHSIDE – TRANSF. ENTRE CONTAS BARILOCHE (SAIDA)
    Decimal('4472.22'),     # ÁGATA – TAXAS E CONTRIBUIÇÕES
    Decimal('4200.00'),     # NORTHSIDE – DESPESAS LEGAIS, CARTORIAIS...
    Decimal('3926.26'),     # NORTHSIDE – TAXAS BANCÁRIAS
    Decimal('3503.73'),     # BARILOCHE – DESPESAS LEGAIS, CARTORIAIS...
    Decimal('3484.40'),     # BARILOCHE – LOCAÇÃO DE APOIO
    Decimal('3451.61'),     # BARILOCHE – CONSUMO DE ÁGUA E ENERGIA
    Decimal('2934.69'),     # NORTHSIDE – PIS
    Decimal('2842.35'),     # NORTHSIDE – SEGURANÇA
    Decimal('2765.04'),     # ÁGATA – OUTRAS DESPESAS
    Decimal('2600.86'),     # NORTHSIDE – CONSUMO DE ÁGUA E ENERGIA
    Decimal('2096.62'),     # BARILOCHE – SERVIÇOS DE TOPOGRAFIA
    Decimal('2042.78'),     # NORTHSIDE – TAXAS E CONTRIBUIÇÕES
    Decimal('1977.76'),     # ÁGATA – VIAGEM
    Decimal('1817.34'),     # BARILOCHE – TRANSF. ENTRE CONTAS BARILOCHE (SAIDA)
    Decimal('1595.87'),     # BARILOCHE – TAXAS BANCÁRIAS
    Decimal('1530.00'),     # BARILOCHE – PROJETOS AMBIENTAIS
    Decimal('1500.00'),     # BARILOCHE – ASSESSORIA TÉCNICA
    Decimal('1334.06'),     # NORTHSIDE – PLACAS DE OBRAS, SINALIZAÇÃO
    Decimal('1260.36'),     # BARILOCHE – TAXAS E CONTRIBUIÇÕES
    Decimal('1220.00'),     # ÁGATA – BENS DE PEQUENO VALOR
    Decimal('975.69'),      # ÁGATA – ASSINATURA DIGITAL, CERTIFICAÇÃO
    Decimal('550.00'),      # NORTHSIDE – ASSESSORIA JURÍDICA
    Decimal('206.91'),      # NORTHSIDE – ASSINATURA DIGITAL, CERTIFICAÇÃO
    Decimal('111.82'),      # BARILOCHE – IMPOSTOS (ISSQN, IRRF...)
]

total_entradas = sum(entradas)
total_saidas = sum(saidas)
saldo = total_entradas - total_saidas

print("Total de Entradas:", BR(total_entradas))
print("Total de Saídas  :", BR(total_saidas))
print("Saldo (Entradas - Saídas):", BR(saldo))

# Agora, vamos calcular o efeito líquido apenas das transferências entre contas
# (para verificar se há dupla contagem que deveria se anular no consolidado).
def is_transfer(label: str) -> bool:
    return 'TRANSF.' in label or 'TRANSFER' in label

# Mapas com rótulos para auditar
rotulos_entradas = [
    "ÁGATA APORTE CAP",
    "NORTHSIDE TRANSF AGATA ENTRADA",
    "NORTHSIDE RECEITAS VENDAS",
    "NORTHSIDE TRANSF LIFECON ENTRADA",
    "ÁGATA TRANSF LIFECON ENTRADA",
    "BARILOCHE TRANSF AGATA ENTRADA",
    "ÁGATA EMPRÉSTIMOS ENTRADA",
    "ÁGATA TRANSF AGATA ENTRADA",
    "ÁGATA TRANSF LIFECON SAIDA (listada como entrada)",
    "BARILOCHE TRANSF LIFECON ENTRADA",
    "ÁGATA RECEITA APLICAÇÕES",
    "BARILOCHE TRANSF BARILOCHE ENTRADA",
    "BARILOCHE OUTRAS RECEITAS FIN",
    "NORTHSIDE RECEITA APLICAÇÕES",
    "BARILOCHE RECEITA APLICAÇÕES",
    "NORTHSIDE OUTRAS RECEITAS FIN",
    "BARILOCHE TAXAS BANCÁRIAS ENTRADA",
]

rotulos_saidas = [
    "ÁGATA TRANSF LIFECON SAIDA",
    "NORTHSIDE OBRAS INFRA",
    "NORTHSIDE OBRAS EDIF",
    "NORTHSIDE TRANSF LIFECON SAIDA",
    "NORTHSIDE IPTU ITR",
    "NORTHSIDE TRANSF AGATA SAIDA",
    "ÁGATA TRANSF BARILOCHE SAIDA",
    "NORTHSIDE COMISSAO",
    "NORTHSIDE ASSESSORIA TEC",
    "NORTHSIDE RESULT SOC PAGAR",
    "ÁGATA TRANSF AGATA SAIDA",
    "NORTHSIDE MAT ELETRICO",
    "BARILOCHE MURO CONTENCAO",
    "BARILOCHE CUSTO AREA",
    "NORTHSIDE PROJ COMPLEMENTARES",
    "NORTHSIDE MARKETING",
    "NORTHSIDE IMPOSTOS ISSQN",
    "ÁGATA ASSESSORIA INFORMATICA",
    "NORTHSIDE ASSESSORIA CONTÁBIL",
    "NORTHSIDE PROJ AMBIENTAIS",
    "ÁGATA ASSESSORIA TÉCNICA",
    "NORTHSIDE EXEC ELETRIFICACAO",
    "ÁGATA EMPRÉSTIMOS SAIDA",
    "NORTHSIDE PROJ URBANISTICOS",
    "NORTHSIDE DESPESAS INICIAIS",
    "BARILOCHE IPTU ITR",
    "ÁGATA ASSESSORIA CONTABIL",
    "NORTHSIDE CUSTO DA AREA",
    "NORTHSIDE SUPRESSAO VEGETAL",
    "BARILOCHE TAXAS E IMPOSTOS",
    "BARILOCHE PROJETOS EDIFICACOES",
    "NORTHSIDE PROJETOS EDIFICACOES",
    "BARILOCHE ASSESSORIA CONTABIL",
    "BARILOCHE FORNECIMENTO MATERIAL",
    "BARILOCHE LIMPEZA AREA",
    "NORTHSIDE COFINS",
    "NORTHSIDE REGISTRO IMOVEIS",
    "NORTHSIDE CSLL IRPJ",
    "BARILOCHE DESPESAS INICIAIS",
    "ÁGATA TAXAS BANCARIAS",
    "NORTHSIDE TOPOGRAFIA",
    "NORTHSIDE TRANSF AGATA SAIDA",
    "NORTHSIDE TRANSF BARILOCHE SAIDA",
    "ÁGATA TAXAS E CONTRIB",
    "NORTHSIDE DESPESAS LEGAIS",
    "NORTHSIDE TAXAS BANCARIAS",
    "BARILOCHE DESPESAS LEGAIS",
    "BARILOCHE LOCACAO APOIO",
    "BARILOCHE CONSUMO AGUA",
    "NORTHSIDE PIS",
    "NORTHSIDE SEGURANCA",
    "ÁGATA OUTRAS DESPESAS",
    "NORTHSIDE CONSUMO AGUA",
    "BARILOCHE TOPOGRAFIA",
    "NORTHSIDE TAXAS E CONTRIB",
    "ÁGATA VIAGEM",
    "BARILOCHE TRANSF BARILOCHE SAIDA",
    "BARILOCHE TAXAS BANCARIAS",
    "BARILOCHE PROJETOS AMBIENTAIS",
    "BARILOCHE ASSESSORIA TECNICA",
    "NORTHSIDE PLACAS OBRAS",
    "BARILOCHE TAXAS E CONTRIB",
    "ÁGATA BENS PEQUENO VALOR",
    "ÁGATA ASSINATURA DIGITAL",
    "NORTHSIDE ASSESSORIA JURÍDICA",
    "NORTHSIDE ASSINATURA DIGITAL",
    "BARILOCHE IMPOSTOS ISSQN",
]

# Identificar transferências por rótulo simples (contendo "TRANSF")
transfer_entradas = [v for r, v in zip(rotulos_entradas, entradas) if 'TRANSF' in r]
transfer_saidas = [v for r, v in zip(rotulos_saidas, saidas) if 'TRANSF' in r]

total_transf_entradas = sum(transfer_entradas)
total_transf_saidas = sum(transfer_saidas)
liquido_transf = total_transf_entradas - total_transf_saidas

print("\nEfeito líquido das TRANSFERÊNCIAS (devem tender a zero no consolidado):")
print("Entradas de transferências:", BR(total_transf_entradas))
print("Saídas   de transferências:", BR(total_transf_saidas))
print("Líquido de transferências  :", BR(liquido_transf))

# Saldo excluindo TODAS as transferências (para ver o caixa operacional consolidado)
entradas_sem_transf = sum(v for r, v in zip(rotulos_entradas, entradas) if 'TRANSF' not in r)
saidas_sem_transf = sum(v for r, v in zip(rotulos_saidas, saidas) if 'TRANSF' not in r)
saldo_sem_transf = entradas_sem_transf - saidas_sem_transf

print("\nTotais sem transferências:")
print("Entradas (sem transf):", BR(entradas_sem_transf))
print("Saídas   (sem transf):", BR(saidas_sem_transf))
print("Saldo    (sem transf):", BR(saldo_sem_transf))

# Delta indicado pelo usuário que precisamos explicar
saldo_desejado = Decimal('105541.58')
delta = saldo_desejado - saldo
print("\nSaldo desejado:", BR(saldo_desejado))
print("Delta (falta para bater):", BR(delta))