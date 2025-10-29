"""
Script para criar executável portátil do Dashboard Financeiro
Usa PyInstaller para empacotar a aplicação
"""

import subprocess
import sys
from pathlib import Path
import shutil

def main():
    print("="*70)
    print("📦 CRIANDO EXECUTÁVEL DO DASHBOARD FINANCEIRO")
    print("="*70)
    print()
    
    # Verificar se PyInstaller está instalado
    try:
        import PyInstaller
        print("✅ PyInstaller encontrado!")
    except ImportError:
        print("❌ PyInstaller não encontrado!")
        print()
        print("Instalando PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller instalado com sucesso!")
    
    print()
    print("🔨 Compilando aplicação...")
    print("   (Isso pode levar alguns minutos...)")
    print()
    
    # Comando PyInstaller
    cmd = [
        "pyinstaller",
        "--name=Dashboard Financeiro",
        "--onedir",  # Criar pasta (mais rápido para iniciar)
        "--windowed",  # Sem console (comentar para debug)
        "--icon=NONE",  # Adicione um .ico se tiver
        "--add-data=src:src",  # Incluir pasta src
        "--add-data=.streamlit:.streamlit",  # Incluir config Streamlit
        "--hidden-import=streamlit",
        "--hidden-import=plotly",
        "--hidden-import=pandas",
        "--collect-all=streamlit",
        "--collect-all=plotly",
        "launcher.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print()
        print("✅ Compilação concluída!")
        print()
        
        # Copiar arquivos necessários
        print("📋 Copiando arquivos necessários...")
        dist_path = Path("dist/Dashboard Financeiro")
        
        # Copiar CSV de exemplo
        if Path("Fluxo Financeiro.csv").exists():
            shutil.copy("Fluxo Financeiro.csv", dist_path / "Fluxo Financeiro.csv")
            print("   ✅ Fluxo Financeiro.csv copiado")
        
        # Copiar README
        if Path("README.md").exists():
            shutil.copy("README.md", dist_path / "LEIA-ME.txt")
            print("   ✅ README copiado")
        
        # Criar instruções simples
        instrucoes = """
=======================================================
       📊 DASHBOARD FINANCEIRO - INSTRUÇÕES
=======================================================

🚀 COMO USAR:

1. Execute "Dashboard Financeiro.exe"
2. O dashboard abrirá automaticamente no navegador
3. Para fechar, pressione ENTER na janela que abrir

📝 ATUALIZAR DADOS:

1. Edite o arquivo "Fluxo Financeiro.csv"
2. Salve as alterações
3. Recarregue a página (F5) no navegador

⚠️ IMPORTANTE:

- Mantenha todos os arquivos juntos nesta pasta
- Não delete a pasta "_internal"
- O arquivo CSV deve estar na mesma pasta do executável

=======================================================
"""
        
        with open(dist_path / "INSTRUÇÕES.txt", "w", encoding="utf-8") as f:
            f.write(instrucoes)
        print("   ✅ Instruções criadas")
        
        print()
        print("="*70)
        print("✅ EXECUTÁVEL CRIADO COM SUCESSO!")
        print("="*70)
        print()
        print(f"📁 Local: {dist_path.absolute()}")
        print()
        print("📦 DISTRIBUIÇÃO:")
        print("   Copie toda a pasta 'Dashboard Financeiro' para onde quiser")
        print("   Execute 'Dashboard Financeiro.exe' para iniciar")
        print()
        print("="*70)
        
    except subprocess.CalledProcessError as e:
        print()
        print(f"❌ ERRO durante compilação: {e}")
        print()
        print("Verifique se todas as dependências estão instaladas:")
        print("   pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()

