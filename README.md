# 📊 Dashboard Financeiro

Sistema de análise financeira interativo desenvolvido em Python/Streamlit.

## 🌐 **ACESSO PÚBLICO**
**🔗 [Dashboard Online](https://relatorio-financeiro.streamlit.app/)** - Acesse diretamente no navegador!

---

## 🚀 Iniciar Dashboard Localmente

### Opção 1: Duplo clique (Windows)
```
Duplo clique em: Iniciar Dashboard.bat
```

### Opção 2: Terminal
```bash
streamlit run app.py
```

---

## ☁️ Deploy no Streamlit Cloud

Para disponibilizar o dashboard publicamente:

1. **Acesse:** [share.streamlit.io](https://share.streamlit.io)
2. **Conecte sua conta GitHub**
3. **Selecione o repositório:** `Dkubitz/Relatorio_Financeiro`
4. **Configure:**
   - **Main file path:** `app.py`
   - **Branch:** `master`
5. **Deploy!** 

O dashboard ficará disponível em: `https://relatorio-financeiro.streamlit.app/`

---

## 📦 Distribuição para Usuários

Você tem **2 opções** para distribuir:

### 🥇 **OPÇÃO 1: Pacote Simples (Recomendado)**

**Vantagens:**
- ✅ Mais simples
- ✅ Fácil de atualizar
- ✅ Tamanho pequeno (~10MB)

**Como distribuir:**

1. Copie toda a pasta do projeto
2. Inclua o arquivo `COMO USAR.txt`
3. Usuário precisa ter Python instalado (uma vez)
4. Execute: `pip install -r requirements.txt` (uma vez)
5. Depois é só usar `Iniciar Dashboard.bat`

**Ideal para:** Ambientes corporativos onde Python já está instalado

---

### 🥈 **OPÇÃO 2: Executável (.exe)**

**Vantagens:**
- ✅ Não precisa instalar Python
- ✅ Parece mais "profissional"
- ✅ Basta copiar e executar

**Desvantagens:**
- ⚠️ Tamanho maior (~150MB)
- ⚠️ Pode demorar para iniciar (primeira vez)

**Como criar:**

1. Execute: `1-CRIAR_EXECUTAVEL.bat`
2. Aguarde a compilação (3-5 minutos)
3. Encontre o executável em: `dist/Dashboard Financeiro/`
4. Distribua toda a pasta `Dashboard Financeiro`

**Ideal para:** Usuários que não têm Python instalado

---

## 📝 Como Atualizar Dados

1. Edite `Fluxo Financeiro.csv` no Excel
2. Salve o arquivo
3. Pressione F5 no navegador
4. Os dados serão atualizados automaticamente

---

## 📋 Estrutura de Arquivos

```
Dashboard Financeiro/
├── 📄 Iniciar Dashboard.bat    ← Duplo clique aqui
├── 📄 COMO USAR.txt           ← Instruções para usuário
├── 📄 launcher.py             ← Script de inicialização
├── 📄 app.py                  ← Aplicação principal
├── 📄 requirements.txt        ← Dependências Python
├── 📄 Fluxo Financeiro.csv   ← SEUS DADOS
└── 📁 src/                    ← Código do sistema
    ├── data_processor.py
    ├── visualizations.py
    └── utils.py
```

---

## 🛠️ Instalação Manual (Desenvolvimento)

```bash
# 1. Clone ou copie os arquivos
cd "caminho/para/pasta"

# 2. Instale dependências
pip install -r requirements.txt

# 3. Execute
streamlit run app.py
```

---

## 📚 Documentação Adicional

- `COMO USAR.txt` - Guia para usuário final
- `GUIA_DISTRIBUICAO.md` - Guia completo de distribuição
- `criar_executavel.py` - Script para criar .exe

---

## 🆘 Suporte

**Problemas comuns:**

❌ **"Python não encontrado"**
→ Instale Python e marque "Add to PATH"

❌ **"ModuleNotFoundError"**
→ Execute: `pip install -r requirements.txt`

❌ **Dashboard não abre**
→ Abra manualmente: http://localhost:8501

❌ **Dados não atualizam**
→ Pressione F5 no navegador

---

## 📞 Requisitos

- Python 3.8 ou superior
- Windows 10/11 (ou Linux/Mac com adaptações)
- Navegador web moderno

---

✨ **Desenvolvido com Python, Streamlit e Plotly**
