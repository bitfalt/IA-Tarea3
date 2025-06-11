import subprocess
import sys
import os

def check_env_file():
    """Verifica que el archivo .env exista"""
    if not os.path.exists('.env'):
        print("Archivo .env no encontrado")
        print("Crea un archivo .env con tu OPENAI_API_KEY")
        return False
    return True

def run_streamlit_app():
    """Ejecuta la aplicación Streamlit"""
    
    if not check_env_file():
        return
    
    print("Iniciando aplicación Streamlit...")
    print("La aplicación se abrirá en tu navegador")
    print("URL: http://localhost:8501")
    print("Para detener: Ctrl+C")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "app.py", 
            "--server.port=8501",
            "--server.address=localhost"
        ])
    except KeyboardInterrupt:
        print("\nAplicación detenida")

if __name__ == "__main__":
    run_streamlit_app()