"""
Lanzador para IDLE - Matriz Core
Abre este archivo en IDLE y presiona F5 para levantar el servidor y abrir el navegador.
"""
import os
import sys

# 1. Fijar el directorio de trabajo en la raíz del proyecto (matriz_core)
DIRECTORIO_RAIZ = os.path.dirname(os.path.abspath(__file__))
os.chdir(DIRECTORIO_RAIZ)

# 2. Ruta al dashboard principal
DASHBOARD_PATH = os.path.join(DIRECTORIO_RAIZ, "dashboard", "app_v4.py")

print("=" * 60)
print("🔮 INICIANDO SISTEMATIZACIÓN CORE - LA MATRIZ...")
print(f"📁 Directorio base: {DIRECTORIO_RAIZ}")
print(f"🚀 Archivo de dashboard: {DASHBOARD_PATH}")
print("=" * 60)

if not os.path.exists(DASHBOARD_PATH):
    print(f"\n❌ ERROR: No se encontró el archivo en: {DASHBOARD_PATH}")
    print("Verifica que app_v4.py esté dentro de la carpeta 'dashboard'.")
else:
    try:
        # Lanzar Streamlit directamente desde el entorno de Python de IDLE
        from streamlit.web import cli as stcli
        sys.argv = ["streamlit", "run", DASHBOARD_PATH, "--server.headless=false"]
        sys.exit(stcli.main())
    except ImportError:
        print("\n❌ ERROR: Streamlit no está instalado en este Python.")
        print("Instálalo ejecutando en tu terminal: pip install streamlit")
    except SystemExit:
        pass
    except Exception as e:
        import subprocess
        # Fallback alternativo en caso de conflicto con hilos de IDLE
        subprocess.run([sys.executable, "-m", "streamlit", "run", DASHBOARD_PATH])
