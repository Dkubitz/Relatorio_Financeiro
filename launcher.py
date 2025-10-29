"""
Launcher para Dashboard Financeiro
Inicia o Streamlit automaticamente e abre no navegador
"""

import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def main():
    print("="*60)
    print("📊 DASHBOARD FINANCEIRO - INICIANDO...")
    print("="*60)
    print()
    
    # Verificar se o arquivo CSV existe
    csv_path = Path("Fluxo Financeiro.csv")
    if not csv_path.exists():
        print("❌ ERRO: Arquivo 'Fluxo Financeiro.csv' não encontrado!")
        print("   Certifique-se de que o arquivo CSV está na mesma pasta.")
        input("\nPressione ENTER para fechar...")
        sys.exit(1)
    
    print("✅ Arquivo CSV encontrado!")
    print(f"   Caminho: {csv_path.absolute()}")
    print()
    
    # Iniciar Streamlit
    print("🚀 Iniciando servidor Streamlit...")
    print("   (Aguarde alguns segundos...)")
    print()
    
    try:
        # Comando para executar o Streamlit
        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "app.py",
            "--server.port=8501",
            "--server.headless=true",
            "--browser.gatherUsageStats=false"
        ]
        
        # Iniciar processo em background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Aguardar servidor iniciar
        time.sleep(3)
        
        # Abrir navegador
        url = "http://localhost:8501"
        print(f"🌐 Abrindo navegador em: {url}")
        print()
        webbrowser.open(url)
        
        print("="*60)
        print("✅ DASHBOARD INICIADO COM SUCESSO!")
        print("="*60)
        print()
        print("📌 INSTRUÇÕES:")
        print("   • O dashboard está aberto no seu navegador")
        print("   • Para atualizar os dados, edite 'Fluxo Financeiro.csv'")
        print("   • Recarregue a página (F5) para ver as mudanças")
        print()
        print("⚠️  NÃO FECHE ESTA JANELA!")
        print("   (Fechar esta janela irá parar o dashboard)")
        print()
        print("="*60)
        print()
        input("Pressione ENTER para ENCERRAR o dashboard...")
        
        # Encerrar processo
        process.terminate()
        print("\n✅ Dashboard encerrado com sucesso!")
        
    except Exception as e:
        print(f"\n❌ ERRO ao iniciar dashboard: {str(e)}")
        print("\nVerifique se todas as dependências estão instaladas.")
        input("\nPressione ENTER para fechar...")
        sys.exit(1)

if __name__ == "__main__":
    main()

