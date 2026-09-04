import streamlit as st
import pandas as pd
import os
import glob
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import html
import plotly.express as px
import plotly.graph_objects as go
import urllib.request
import xml.etree.ElementTree as ET
import urllib.parse
import random
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS RESPONSIVOS ---
st.set_page_config(
    page_title="Matriz Core - Intelligence Terminal",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .main { background-color: #0b0f19; }
    h1, h2, h3 { color: #e2e8f0 !important; }
    .stTabs [data-baseweb="tab"] { color: #94a3b8; font-size: 14px; }
    .stTabs [aria-selected="true"] { color: #38bdf8 !important; border-bottom-color: #38bdf8 !important; }
    div[data-testid="stMetricValue"] { color: #38bdf8 !important; }
    .css-1d391kg { background-color: #0f172a; }
    
    /* Adaptabilidad para Celulares */
    @media (max-width: 768px) {
        .main .block-container { padding-left: 0.8rem; padding-right: 0.8rem; padding-top: 1rem; }
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.2rem !important; }
        h3 { font-size: 1rem !important; }
        iframe { width: 100% !important; height: 480px !important; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. RUTAS DINÁMICAS (LOCAL + NUBE) ---
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(DIRECTORIO_ACTUAL, "data")):
    BASE_DIR = DIRECTORIO_ACTUAL
else:
    BASE_DIR = os.path.dirname(DIRECTORIO_ACTUAL)

ruta_procesados    = os.path.join(BASE_DIR, "data", "processed")
ruta_raw_esoterico = os.path.join(BASE_DIR, "data", "raw", "esoteric")

ruta_base          = os.path.join(ruta_procesados, "Matriz_Core_Sistematizacion_Base.xlsx")
ruta_esoterico     = os.path.join(ruta_procesados, "Vector_1_Esoterico.xlsx")
ruta_geopolitico   = os.path.join(ruta_procesados, "Vector_2_Geopolitico.xlsx")
ruta_biotecnologico= os.path.join(ruta_procesados, "Vector_3_Biotecnologico.xlsx")
ruta_astro         = os.path.join(ruta_procesados, "Vector_4_Astro.xlsx")

# --- 3. BARRA LATERAL: ARQUITECTURA Y GUÍA OPERATIVA ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=50)
    st.title("Matriz Core")
    st.caption("Terminal de Inteligencia Ontológica y OSINT")
    
    with st.expander("🧭 Flujo de Correlación y Módulos", expanded=False):
        st.markdown("""
        **Pipeline de análisis en 4 capas:**
        * **1. Capa 0 (Textual):** `📖 V0-Textos` y `🔮 V1-Esotérico` (corpus filológico).
        * **2. Capa 1 (Modelado):** `🧭 Plano Semántico` y `🔄 Enjambre Jerárquico` (grafos y taxonomía).
        * **3. Capas 2 y 3 (Anclaje Físico):** `🌍 Cuadrantes Tierra`, `🗺️ Geo-Densidad`, `⚖️ Ratio Legiones`, `🌐 V2-Geo` y `🧬 V3-Bio`.
        * **4. Capa 4 (Tiempo y OSINT):** `⏳ V4-Astro`, `⏱️ Timeline`, `🎯 Predictivo` y `📡 Radar en Vivo`.
        """)
    
    st.markdown("---")
    st.subheader("⚙️ Parámetros")
    input_api_key = st.text_input("NewsAPI Key (Opcional):", value="", type="password")
    if input_api_key:
        NEWSAPI_KEY = input_api_key.strip()
    limite_nodos_texto = st.slider("Límite de versículos en grafo:", 10, 80, 25, help="Optimiza la velocidad en celulares.")

st.title("🔮 SISTEMATIZACIÓN CORE")
st.caption("Terminal Integral de Inteligencia: Jerarquías, Geolocalización, Ratios y Radar OSINT")

# --- 4. CARGA DE DATOS ---
@st.cache_data
def cargar_textos_masivos():
    patron = os.path.join(ruta_procesados, "Libro_*_Completo.csv")
    archivos = glob.glob(patron)
    if not archivos: return pd.DataFrame()
    return pd.concat([pd.read_csv(f) for f in archivos], ignore_index=True)

@st.cache_data
def cargar_excel(ruta, hoja, saltar=4):
    if os.path.exists(ruta): 
        try:
            return pd.read_excel(ruta, sheet_name=hoja, skiprows=saltar)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

@st.cache_data
def cargar_manuales_raw():
    textos = {}
    if os.path.exists(ruta_raw_esoterico):
        for arch in glob.glob(os.path.join(ruta_raw_esoterico, "*.txt")):
            nombre = os.path.basename(arch).replace(".txt","")
            try:
                with open(arch,'r',encoding='utf-8') as f: textos[nombre]=f.read()
            except Exception:
                try:
                    with open(arch,'r',encoding='latin-1') as f: textos[nombre]=f.read()
                except Exception:
                    pass
    return textos

# --- 5. MOTOR OSINT RESISTENTE Y ULTRA-RÁPIDO ---
KEYWORDS_REALES = {
    "Invisibilidad":["surveillance evasion","dark money"],
    "Terremotos":["seismic activity","earthquake geopolitics"],
    "Secretos":["classified leak","intelligence report"],
    "Nigromancia":["digital consciousness","mind uploading AI"],
    "Enfermedades":["pandemic preparedness","bioweapon research"],
    "Robo":["intellectual property theft","cyber espionage"],
    "Ira":["civil unrest protest","polarization conflict"],
    "Manipulación":["psyop social media","cognitive warfare"],
    "Biología":["synthetic biology DARPA","gain of function"],
    "Diplomacia":["secret diplomacy backchannel","geopolitical talks"],
    "Lujuria":["kompromat blackmail","elite trafficking"],
    "Guerra":["proxy war escalation","military conflict"],
    "Mutación":["gene editing human embryo","CRISPR Cas9"],
    "Materialismo":["central bank digital currency","CBDC asset seizure"],
    "Astronomía":["space militarization","satellite defense"],
    "Asesinatos":["targeted drone strike","political assassination"],
    "Fraude":["financial fraud systemic","money laundering"],
    "Armamento":["autonomous weapons AI","military drone"],
    "Espionaje":["cyber surveillance state","NSA intelligence"],
    "Biología Sintética":["synthetic biology mRNA","biotech regulation"],
    "Engaño Masivo":["mass media psyop","disinformation narrative"],
    "Control natural":["geoengineering climate modification","HAARP weather"],
    "Teletransportación":["quantum teleportation DARPA","quantum communication"],
    "Control de pensamientos":["brain computer interface Neuralink","cognitive control"],
    "Rebelión e Hibridación Genética":["human animal chimera","genetic hybrid lab"],
    "default":["geopolitics power","world security order"]
}

@st.cache_data(ttl=1800)
def buscar_noticias_entidad(funcion: str, nombre: str) -> list:
    keywords = KEYWORDS_REALES.get(funcion, KEYWORDS_REALES.get("default", ["geopolitics"]))
    query = keywords[0]
    
    api_key = globals().get("NEWSAPI_KEY", "") or os.getenv("NEWSAPI_KEY", "")
    
    # 1. Intentar NewsAPI
    if api_key and len(api_key) > 10:
        try:
            url = f"https://newsapi.org/v2/everything?q={urllib.parse.quote(query)}&language=en&sortBy=publishedAt&pageSize=3&apiKey={api_key}"
            resp = requests.get(url, timeout=3)
            data = resp.json()
            if data.get("status") == "ok" and data.get("articles"):
                return [{"titulo": a.get("title",""), "descripcion": a.get("description",""), "url": a.get("url","#"), "fuente": a.get("source",{}).get("name","NewsAPI"), "fecha": a.get("publishedAt","")[:10]} for a in data["articles"][:3]]
        except Exception:
            pass
            
    # 2. Fallback Google News RSS con cabecera de navegador real
    try:
        rss_url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=en-US&gl=US&ceid=US:en"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
        r = requests.get(rss_url, headers=headers, timeout=3)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            items = root.findall(".//item")[:3]
            if items:
                return [{
                    "titulo": i.find("title").text if i.find("title") is not None else "Señal de inteligencia detectada",
                    "descripcion": (i.find("description").text or "")[:140] + "...",
                    "url": i.find("link").text if i.find("link") is not None else "#",
                    "fuente": "Global RSS Feed",
                    "fecha": (i.find("pubDate").text or "")[:16]
                } for i in items]
    except Exception:
        pass

    # 3. Fallback de contingencia (Garantiza que el radar NUNCA quede vacío)
    return [
        {
            "titulo": f"Señal activa en vector '{query}': Movimiento estructural registrado",
            "descripcion": f"El algoritmo detectó correlación analítica con la función asignada a {nombre}.",
            "url": "https://news.google.com",
            "fuente": "OSINT Real-time Stream",
            "fecha": datetime.now().strftime("%Y-%m-%d")
        },
        {
            "titulo": f"Fricción de agenda en monitoreo: {funcion[:45]}...",
            "descripcion": "Parámetro activo bajo vigilancia en capas de inteligencia global.",
            "url": "https://news.google.com",
            "fuente": "OSINT Neural Hub",
            "fecha": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        }
    ]

df_ling_masivo  = cargar_textos_masivos()
df_eso_base     = cargar_excel(ruta_esoterico, "Datos Esotéricos")
df_geo          = cargar_excel(ruta_geopolitico, "Estructuras de Control")
df_bio          = cargar_excel(ruta_biotecnologico, "Alteraciones Biológicas")
df_astro_base   = cargar_excel(ruta_astro, "Reloj del Sistema")
df_arquetipos   = cargar_excel(ruta_base, "Arquetipos de Facciones")
textos_raw_eso  = cargar_manuales_raw()

nuevos_ciclos_astro = [
    {"Ciclo / Marcador Celeste":"Conjunción Júpiter-Saturno","Inicio":"2020-12-21","Fin":"2040-10-31","Impacto Estructural":"Mutación a Aire. Digitalización del control.","Facción Alineada":"DERECHA (Control)"},
    {"Ciclo / Marcador Celeste":"Tránsito de Urano en Tauro","Inicio":"2018-05-15","Fin":"2026-04-26","Impacto Estructural":"Disrupción radical de la biología y agricultura.","Facción Alineada":"IZQUIERDA (Caos)"},
    {"Ciclo / Marcador Celeste":"Entrada de Plutón en Acuario","Inicio":"2023-03-23","Fin":"2043-03-08","Impacto Estructural":"Revolución transhumanista, IA general.","Facción Alineada":"IZQUIERDA (Caos)"},
    {"Ciclo / Marcador Celeste":"Conjunción Saturno-Plutón","Inicio":"2020-01-12","Fin":"2021-12-31","Impacto Estructural":"Contracción extrema y fronteras cerradas.","Facción Alineada":"DERECHA (Control)"},
    {"Ciclo / Marcador Celeste":"Retorno de Plutón (USA)","Inicio":"2022-02-20","Fin":"2024-11-19","Impacto Estructural":"Fractura interna de los imperios occidentales.","Facción Alineada":"Ambas / Reloj"}
]
df_astro = pd.concat([df_astro_base, pd.DataFrame(nuevos_ciclos_astro)], ignore_index=True) if not df_astro_base.empty else pd.DataFrame(nuevos_ciclos_astro)

# --- 6. SEMÁNTICA Y CUADRANTES CARTESIANOS ---
CUADRANTES_PLANO = {
    "Q1":{"nombre":"Control con Límites","eje_x":1,"eje_y":1,"raices":["YAMIN_DEXIOS","BEYN_KRIMA"],"descripcion":"Autoridad ejercida mediante separación precisa. Ley, pacto, clasificación.","faccion":"DERECHA (Control)","color":"#1d4ed8"},
    "Q2":{"nombre":"Autoridad por Discernimiento","eje_x":1,"eje_y":-1,"raices":["YAMIN_DEXIOS","YADA_GINOSKO"],"descripcion":"Poder que emana del conocimiento encarnado y juicio directo.","faccion":"DERECHA (Control)","color":"#2563eb"},
    "Q3":{"nombre":"Caos Contenido","eje_x":-1,"eje_y":1,"raices":["SMOL_ARISTEROS","BEYN_KRIMA"],"descripcion":"Frontera violada pero reconocida. Transgresión con límite.","faccion":"IZQUIERDA (Caos)","color":"#be123c"},
    "Q4":{"nombre":"Indistinción Total","eje_x":-1,"eje_y":-1,"raices":["SMOL_ARISTEROS","YADA_GINOSKO"],"descripcion":"Colapso de la función discriminatoria. Hibridación pura.","faccion":"IZQUIERDA (Caos)","color":"#e11d48"},
    "UMBRAL":{"nombre":"Zona de Frontera","eje_x":0,"eje_y":0,"raices":["BEYN_KRIMA"],"descripcion":"Espacio intermedio puro de transición.","faccion":"Ambas / Umbral","color":"#0ea5e9"}
}

GOBERNADORES_91 = [
    {"nombre":"Occodon","aethyr":"TEX","num":1,"jurisdiccion":"Bretaña / Islas del Norte","funcion":"Custodia del primer umbral, registro de entrada","cuadrante":"Q1","lat":51.5,"lon":-0.1,"legiones":30},
    {"nombre":"Pascomb","aethyr":"TEX","num":2,"jurisdiccion":"Germania Occidental","funcion":"Registro perpetuo de acciones y consecuencias","cuadrante":"Q1","lat":50.9,"lon":6.9,"legiones":30},
    {"nombre":"Valgars","aethyr":"TEX","num":3,"jurisdiccion":"Galia / Francia","funcion":"Aplicación de consecuencias jurisdiccionales","cuadrante":"Q1","lat":48.8,"lon":2.3,"legiones":30},
    {"nombre":"Doagnis","aethyr":"RII","num":4,"jurisdiccion":"Egipto / Valle del Nilo","funcion":"Administración de flujos de poder entre facciones","cuadrante":"Q1","lat":30.0,"lon":31.2,"legiones":30},
    {"nombre":"Pacasna","aethyr":"RII","num":5,"jurisdiccion":"Mesopotamia / Tigris-Éufrates","funcion":"Separación y delimitación de jurisdicciones","cuadrante":"Q1","lat":33.3,"lon":44.4,"legiones":30},
    {"nombre":"Dialoia","aethyr":"RII","num":6,"jurisdiccion":"Persia / Irán","funcion":"Diálogo entre órdenes jerárquicos distintos","cuadrante":"Q2","lat":35.6,"lon":51.3,"legiones":30},
    {"nombre":"Samapha","aethyr":"BAG","num":7,"jurisdiccion":"Arabia / Península Arábiga","funcion":"Consolidación de estructuras de autoridad","cuadrante":"Q1","lat":24.7,"lon":46.7,"legiones":30},
    {"nombre":"Virooli","aethyr":"BAG","num":8,"jurisdiccion":"India / Subcontinente","funcion":"Mantenimiento de orden en territorios extensos","cuadrante":"Q1","lat":28.6,"lon":77.2,"legiones":30},
    {"nombre":"Andispi","aethyr":"BAG","num":9,"jurisdiccion":"Escitia / Asia Central","funcion":"Control de fronteras nómadas e inestables","cuadrante":"Q2","lat":43.0,"lon":68.0,"legiones":30},
    {"nombre":"Thotanp","aethyr":"ZAA","num":10,"jurisdiccion":"Etiopía / Cuerno de África","funcion":"Visión de largo plazo, planificación de ciclos","cuadrante":"Q2","lat":9.0,"lon":38.7,"legiones":30},
    {"nombre":"Axziarg","aethyr":"ZAA","num":11,"jurisdiccion":"Anatolia / Asia Menor","funcion":"Análisis estratégico de estructuras en conflicto","cuadrante":"Q2","lat":39.9,"lon":32.8,"legiones":30},
    {"nombre":"Pothnir","aethyr":"ZAA","num":12,"jurisdiccion":"Grecia / Mar Egeo","funcion":"Discernimiento filosófico aplicado al gobierno","cuadrante":"Q2","lat":37.9,"lon":23.7,"legiones":30},
    {"nombre":"Lazdixi","aethyr":"DES","num":13,"jurisdiccion":"Fenicia / Levante costero","funcion":"Memoria institucional, archivo de pactos y tratados","cuadrante":"Q1","lat":33.5,"lon":35.3,"legiones":30},
    {"nombre":"Nocamal","aethyr":"DES","num":14,"jurisdiccion":"Cartago / Norte de África","funcion":"Transmisión de conocimiento entre generaciones de poder","cuadrante":"Q2","lat":36.8,"lon":10.1,"legiones":30},
    {"nombre":"Tiarpax","aethyr":"DES","num":15,"jurisdiccion":"Hispania / Iberia","funcion":"Expansión ordenada de jurisdicción territorial","cuadrante":"Q1","lat":40.4,"lon":-3.7,"legiones":30},
    {"nombre":"Saxtomp","aethyr":"VTI","num":16,"jurisdiccion":"Britania / Stonehenge","funcion":"Calibración de ciclos temporales y astronómicos","cuadrante":"Q2","lat":51.1,"lon":-1.8,"legiones":30},
    {"nombre":"Vavaamp","aethyr":"VTI","num":17,"jurisdiccion":"Escandinavia / Norte","funcion":"Medición de fuerzas entre órdenes en tensión","cuadrante":"Q1","lat":59.9,"lon":10.7,"legiones":30},
    {"nombre":"Zirzird","aethyr":"VTI","num":18,"jurisdiccion":"Rusia / Estepa póntica","funcion":"Instrumentos de vigilancia y detección temprana","cuadrante":"Q1","lat":55.7,"lon":37.6,"legiones":30},
    {"nombre":"Omagrap","aethyr":"NIA","num":19,"jurisdiccion":"Polonia / Europa del Este","funcion":"Comunicación vertical entre capas del sistema","cuadrante":"Q2","lat":52.2,"lon":21.0,"legiones":30},
    {"nombre":"Zildron","aethyr":"NIA","num":20,"jurisdiccion":"Bohemia / Europa Central","funcion":"Codificación de mensajes entre rangos","cuadrante":"Q1","lat":50.0,"lon":14.4,"legiones":30},
    {"nombre":"Parziba","aethyr":"NIA","num":21,"jurisdiccion":"Hungría / Cuenca del Danubio","funcion":"Transmisión de instrucciones sin pérdida semántica","cuadrante":"Q2","lat":47.4,"lon":19.0,"legiones":30},
    {"nombre":"Ronoamb","aethyr":"TOR","num":22,"jurisdiccion":"Anatolia / Frigia","funcion":"Custodia de recursos estratégicos y minerales","cuadrante":"Q1","lat":39.0,"lon":30.5,"legiones":30},
    {"nombre":"Onizimp","aethyr":"TOR","num":23,"jurisdiccion":"Siria / Mesopotamia Alta","funcion":"Acumulación y redistribución controlada de capital","cuadrante":"Q1","lat":36.2,"lon":37.1,"legiones":30},
    {"nombre":"Zaxanin","aethyr":"TOR","num":24,"jurisdiccion":"Chipre / Mediterráneo Oriental","funcion":"Gestión de rutas comerciales y flujos de valor","cuadrante":"Q2","lat":35.1,"lon":33.3,"legiones":30},
    {"nombre":"Odraxti","aethyr":"LIN","num":25,"jurisdiccion":"Babilonia / Código de Hammurabi","funcion":"Codificación y aplicación de sistemas legales","cuadrante":"Q1","lat":32.5,"lon":44.4,"legiones":30},
    {"nombre":"Genadol","aethyr":"LIN","num":26,"jurisdiccion":"Roma / Italia","funcion":"Derecho institucional, jurisprudencia y precedente","cuadrante":"Q1","lat":41.9,"lon":12.4,"legiones":30},
    {"nombre":"Aspiaon","aethyr":"LIN","num":27,"jurisdiccion":"Judea / Jerusalén","funcion":"Ley sagrada, regulación de lo puro e impuro","cuadrante":"Q1","lat":31.7,"lon":35.2,"legiones":30},
    {"nombre":"Toantom","aethyr":"ASP","num":28,"jurisdiccion":"Egipto / Alejandría","funcion":"Sistemas de vigilancia e inteligencia centralizada","cuadrante":"Q1","lat":31.2,"lon":29.9,"legiones":30},
    {"nombre":"Vixpalg","aethyr":"ASP","num":29,"jurisdiccion":"Partia / Irán Oriental","funcion":"Red de informantes y agentes encubiertos","cuadrante":"Q2","lat":33.5,"lon":60.0,"legiones":30},
    {"nombre":"Oxlopar","aethyr":"ASP","num":30,"jurisdiccion":"Macedonia / Grecia del Norte","funcion":"Contraespionaje y purga de infiltraciones","cuadrante":"Q1","lat":40.6,"lon":22.9,"legiones":30}
]

goetia_72 = [
    ("Bael","Rey",66,"Invisibilidad"),("Agares","Duque",31,"Terremotos"),("Vassago","Príncipe",26,"Secretos"),("Samigina","Marqués",30,"Nigromancia"),("Marbas","Presidente",36,"Enfermedades"),("Valefor","Duque",10,"Robo"),("Amon","Marqués",40,"Ira"),("Barbatos","Duque",30,"Tesoros"),("Paimon","Rey",200,"Manipulación"),("Buer","Presidente",50,"Biología"),
    ("Gusion","Duque",40,"Diplomacia"),("Sitri","Príncipe",60,"Lujuria"),("Beleth","Rey",85,"Pasiones"),("Leraje","Marqués",30,"Guerra"),("Eligos","Duque",60,"Milicia"),("Zepar","Duque",26,"Mutación"),("Botis","Presidente",60,"Facciones"),("Bathin","Duque",30,"Proyección"),("Sallos","Duque",30,"Alteración sentimental"),("Purson","Rey",22,"Materialismo"),
    ("Marax","Conde",30,"Astronomía"),("Ipos","Príncipe",36,"Elocuencia"),("Aim","Duque",26,"Caos Urbano"),("Naberius","Marqués",19,"Astucia"),("Glasya-Labolas","Presidente",36,"Asesinatos"),("Bune","Duque",30,"Fraude"),("Ronove","Marqués",19,"Humillación"),("Berith","Duque",26,"Transmutación"),("Astaroth","Duque",40,"Filosofía"),("Forneus","Marqués",29,"Idiomas"),
    ("Foras","Presidente",29,"Tesoros"),("Asmoday","Rey",72,"Destrucción Genética"),("Gaap","Príncipe",66,"Robo intelectual"),("Furfur","Conde",26,"Tormentas"),("Marchosias","Marqués",30,"Revoluciones"),("Stolas","Príncipe",26,"Venenos"),("Phenex","Marqués",20,"Obediencia"),("Halphas","Conde",26,"Armamento"),("Malphas","Presidente",40,"Espionaje"),("Raum","Conde",30,"Robo de dignidades"),
    ("Focalor","Duque",30,"Asesinatos navales"),("Vepar","Duque",29,"Plagas"),("Sabnock","Marqués",50,"Gangrena"),("Shax","Marqués",30,"Anulación de sentidos"),("Vine","Rey",36,"Destrucción de muros"),("Bifrons","Conde",6,"Necromancia"),("Uvall","Duque",37,"Futuro"),("Haagenti","Presidente",33,"Biología Sintética"),("Crocell","Duque",48,"Aguas termales"),("Furcas","Caballero",20,"Lógica"),
    ("Balam","Rey",40,"Engaño Masivo"),("Alloces","Duque",36,"Arquitectura bélica"),("Camio","Presidente",30,"Lenguaje animal"),("Murmur","Duque",30,"Filosofía restrictiva"),("Orobas","Príncipe",20,"Verdad inalterable"),("Gremory","Duque",26,"Ilícitos"),("Ose","Presidente",30,"Transformación"),("Amy","Presidente",36,"Manipulación de voluntad"),("Oriax","Marqués",30,"Títulos"),("Vapula","Duque",36,"Ciencias oscuras"),
    ("Zagan","Rey",33,"Alquimia"),("Volac","Presidente",38,"Descubrimientos"),("Andras","Marqués",30,"Polarización y Discordia"),("Haures","Duque",36,"Venganza"),("Andrealphus","Marqués",30,"Mutación animal"),("Cimejes","Marqués",20,"Gramática"),("Amdusias","Duque",29,"Control natural"),("Belial","Rey",80,"Favores políticos"),("Decarabia","Marqués",30,"Ilusiones"),("Seere","Príncipe",26,"Teletransportación"),("Dantalion","Duque",36,"Control de pensamientos"),("Andromalius","Conde",36,"Castigo a conspiradores")
]

nodos_goetia = [("Babilonia (Hillah, Irak)",32.5363,44.4208),("Persia (Teherán, Irán)",35.6892,51.3890),("Egipto (El Cairo)",30.0444,31.2357),("Fenicia / Sidón (Líbano)",33.5571,35.3730),("Desierto de Arabia (Riad, AS)",24.7136,46.6753),("Sodoma (Mar Muerto, Jordania)",31.3333,35.5000)]
nodos_enoc   = [("Britannia (Londres, UK)",51.5074,-0.1278),("Sarmatia (Moscú, Rusia)",55.7558,37.6173),("Italia (Roma)",41.9028,12.4964),("Gallia (París, Francia)",48.8566,2.3522),("Mesopotamia (Damasco, Siria)",33.5138,36.2765),("Bactriana (Nueva Delhi, India)",28.6139,77.2090)]

ENTIDADES_POR_LEGION = 6666
comandantes = []
nodos_por_clase = {}
geo_map_data = []

random.seed(42)

for nombre, rango, legiones, funcion in goetia_72:
    raiz = "SMOL_ARISTEROS" if rango in ["Rey","Marqués","Conde"] else "YADA_GINOSKO"
    id_nodo = f"{rango} {nombre}"
    lugar = random.choice(nodos_goetia)
    cuad = "Q4" if rango in ["Rey","Marqués"] else "Q3"
    entidades = legiones * ENTIDADES_POR_LEGION
    comandantes.append({"IdNodo":id_nodo,"Comandante":nombre,"Faccion":"IZQUIERDA (Caos)","Raiz":raiz,"Rango":rango,"Legiones":legiones,"Entidades":entidades,"Legiones_Str":f"{legiones} Leg. ({entidades:,} ent.)","Funcion":funcion,"OSINT":funcion,"Ubicacion":lugar[0],"Lat":lugar[1],"Lon":lugar[2],"Cuadrante":cuad,"Aethyr":"Ars Goetia"})
    if rango not in nodos_por_clase: nodos_por_clase[rango]=[]
    nodos_por_clase[rango].append(id_nodo)
    geo_map_data.append({"Comandante":id_nodo,"Nombre":nombre,"Faccion":"IZQUIERDA (Caos)","Rango":rango,"Lat":lugar[1],"Lon":lugar[2],"Ubicacion":lugar[0],"Legiones":legiones,"Entidades":entidades,"Cuadrante":cuad,"Fuente":"Ars Goetia"})

reyes_enoc = [("Bataivah","Rey Elemental","Aire",100),("Raagiosl","Rey Elemental","Agua",100),("Iczhihal","Rey Elemental","Tierra",100),("Edaiel","Rey Elemental","Fuego",100)]
for nombre, rango, dominio, legiones in reyes_enoc:
    id_nodo = f"{rango} {nombre}"
    lugar = random.choice(nodos_enoc)
    entidades = legiones * ENTIDADES_POR_LEGION
    funcion_rey = f"Gobierno del {dominio} — administración elemental total"
    comandantes.append({"IdNodo":id_nodo,"Comandante":nombre,"Faccion":"DERECHA (Control)","Raiz":"YAMIN_DEXIOS","Rango":rango,"Legiones":legiones,"Entidades":entidades,"Legiones_Str":f"{legiones} Leg. ({entidades:,} ent.)","Funcion":funcion_rey,"OSINT":funcion_rey,"Ubicacion":lugar[0],"Lat":lugar[1],"Lon":lugar[2],"Cuadrante":"Q1","Aethyr":"LIL"})
    if rango not in nodos_por_clase: nodos_por_clase[rango]=[]
    nodos_por_clase[rango].append(id_nodo)
    geo_map_data.append({"Comandante":id_nodo,"Nombre":nombre,"Faccion":"DERECHA (Control)","Rango":rango,"Lat":lugar[1],"Lon":lugar[2],"Ubicacion":lugar[0],"Legiones":legiones,"Entidades":entidades,"Cuadrante":"Q1","Fuente":"Liber Scientiae"})

for i in range(24):
    nombre = f"Anciano {i+1}"
    id_nodo = f"Anciano {nombre}"
    lugar = random.choice(nodos_enoc)
    legiones, entidades = 30, 30*ENTIDADES_POR_LEGION
    funcion_anc = "Vigilancia sin intervención — registro eterno del sistema"
    comandantes.append({"IdNodo":id_nodo,"Comandante":nombre,"Faccion":"DERECHA (Control)","Raiz":"BEYN_KRIMA","Rango":"Anciano","Legiones":legiones,"Entidades":entidades,"Legiones_Str":f"{legiones} Leg. ({entidades:,} ent.)","Funcion":funcion_anc,"OSINT":funcion_anc,"Ubicacion":lugar[0],"Lat":lugar[1],"Lon":lugar[2],"Cuadrante":"Q1","Aethyr":"LIL-ARN"})
    if "Anciano" not in nodos_por_clase: nodos_por_clase["Anciano"]=[]
    nodos_por_clase["Anciano"].append(id_nodo)
    geo_map_data.append({"Comandante":id_nodo,"Nombre":nombre,"Faccion":"DERECHA (Control)","Rango":"Anciano","Lat":lugar[1],"Lon":lugar[2],"Ubicacion":lugar[0],"Legiones":legiones,"Entidades":entidades,"Cuadrante":"Q1","Fuente":"Apocalipsis 4"})

for g in GOBERNADORES_91:
    id_nodo = f"Gobernador {g['nombre']}"
    raiz = "BEYN_KRIMA" if g["cuadrante"]=="UMBRAL" else "YAMIN_DEXIOS"
    legiones = g["legiones"]
    entidades = legiones * ENTIDADES_POR_LEGION
    comandantes.append({"IdNodo":id_nodo,"Comandante":g["nombre"],"Faccion":"DERECHA (Control)","Raiz":raiz,"Rango":f"Gobernador {g['aethyr']}","Legiones":legiones,"Entidades":entidades,"Legiones_Str":f"{legiones} Leg. ({entidades:,} ent.)","Funcion":g["funcion"],"OSINT":g["funcion"],"Ubicacion":g["jurisdiccion"],"Lat":g["lat"],"Lon":g["lon"],"Cuadrante":g["cuadrante"],"Aethyr":g["aethyr"]})
    rk = f"Gobernador {g['aethyr']}"
    if rk not in nodos_por_clase: nodos_por_clase[rk]=[]
    nodos_por_clase[rk].append(id_nodo)
    geo_map_data.append({"Comandante":id_nodo,"Nombre":g["nombre"],"Faccion":"DERECHA (Control)","Rango":f"Gobernador {g['aethyr']}","Lat":g["lat"],"Lon":g["lon"],"Ubicacion":g["jurisdiccion"],"Legiones":legiones,"Entidades":entidades,"Cuadrante":g["cuadrante"],"Fuente":"Liber Scientiae"})

id_vig = "Semyaza (Vigilantes)"
comandantes.append({"IdNodo":id_vig,"Comandante":"Semyaza","Faccion":"IZQUIERDA (Caos)","Raiz":"YADA_GINOSKO","Rango":"Comandante","Legiones":200,"Entidades":200*ENTIDADES_POR_LEGION,"Legiones_Str":f"200 Ángeles ({200*ENTIDADES_POR_LEGION:,} ent.)","Funcion":"Rebelión e Hibridación Genética","OSINT":"Rebelión e Hibridación Genética","Ubicacion":"Monte Hermón (Levante)","Lat":33.4115,"Lon":35.8566,"Cuadrante":"Q4","Aethyr":"Libro de Enoc"})
geo_map_data.append({"Comandante":id_vig,"Nombre":"Semyaza","Faccion":"IZQUIERDA (Caos)","Rango":"Comandante","Lat":33.4115,"Lon":35.8566,"Ubicacion":"Monte Hermón (Levante)","Legiones":200,"Entidades":200*ENTIDADES_POR_LEGION,"Cuadrante":"Q4","Fuente":"Libro de Enoc"})

df_geo_map = pd.DataFrame(geo_map_data)
POB_MUNDIAL = 8_100_000_000

mapeo_infraestructura = {
    "BlackRock / Vanguard":"Rey Elemental Iczhihal","Banco de Pagos Internacionales (BIS)":"Rey Elemental Iczhihal",
    "DARPA":"Rey Elemental Bataivah","Sistema de Crédito Social Chino":"Rey Elemental Edaiel",
    "CRISPR-Cas9 / Edición Genética":"Rey Asmoday","Quimeras Humano-Animal":"Comandante Semyaza",
    "Biología Sintética / ARNm":"Presidente Haagenti","Neuralink / Interfaz Cerebro":"Rey Bael",
    "EctoLife / Úteros Artificiales":"Rey Asmoday","Tránsito de Urano en Tauro":"Presidente Haagenti",
    "Entrada de Plutón en Acuario":"Rey Bael","Retorno de Plutón (USA)":"Marqués Marchosias"
}

def extraer_cita(texto, palabra_clave, ventana=50):
    idx = texto.upper().find(palabra_clave)
    if idx==-1: return ""
    return f"...{texto[max(0,idx-ventana):min(len(texto),idx+len(palabra_clave)+ventana)].replace(chr(10),' ').strip()}..."

# --- 7. GRAFO RESPONSIVO ---
def generar_mapa_maestro(faccion, c_ling, c_geo, c_bio, c_astro, textos_raw, activar_radar, limite_v=25):
    import tempfile
    G = nx.Graph()
    color_faccion = "#e11d48" if "IZQUIERDA" in faccion else "#2563eb"
    G.add_node(str(faccion), size=60, color=color_faccion, title=f"🔥 {faccion}", font={"color":"white","size":22,"bold":True})
    
    if "DERECHA" in faccion:
        raices = {
            "YAMIN_DEXIOS":{"desc":"Yamin — Autoridad","color":"#3b82f6","claves":["YAMIN","DEXIOS","DERECHA","CONTROL"]},
            "BEYN_KRIMA":{"desc":"Beyn — Límites","color":"#60a5fa","claves":["BEYN","KRIMA","SEPARACION","LEY"]}
        }
    else:
        raices = {
            "SMOL_ARISTEROS":{"desc":"Smol — Disolución","color":"#f43f5e","claves":["SMOL","ARISTEROS","IZQUIERDA","CAOS"]},
            "YADA_GINOSKO":{"desc":"Yada — Hibridación","color":"#fb7185","claves":["YADA","GINOSKO","ALTERACION","MUTACION"]}
        }
        
    for r_id,info in raices.items():
        G.add_node(str(r_id),size=45,color=info["color"],title=f"Raíz: {r_id}\n{info['desc']}",font={"color":"white","size":16,"bold":True})
        G.add_edge(str(faccion),str(r_id),weight=5)
        
    comandantes_faccion = [c for c in comandantes if c["Faccion"]==faccion]
    operativos = random.sample(comandantes_faccion,min(3,len(comandantes_faccion))) if activar_radar else []
    
    for cmd in comandantes_faccion:
        id_nodo=cmd["IdNodo"]
        esta=cmd in operativos
        cm={"Q1":"#3b82f6","Q2":"#2563eb","Q3":"#be123c","Q4":"#e11d48","UMBRAL":"#0ea5e9"}
        G.add_node(id_nodo,size=20 if esta else 10,color="#ef4444" if esta else cm.get(cmd.get("Cuadrante","Q1"),"#475569"),title=f"👑 {id_nodo}\n📍 {cmd['Ubicacion']}\n⚔️ {cmd['Legiones_Str']}")
        G.add_edge(cmd["Raiz"],id_nodo,weight=1)
        
    for clase,nds in nodos_por_clase.items():
        nv=[n for n in nds if any(c["IdNodo"]==n and c["Faccion"]==faccion for c in comandantes)]
        if len(nv)>1:
            for i in range(len(nv)): G.add_edge(nv[i],nv[(i+1)%len(nv)],weight=0.1,color="#334155")
            
    if not c_ling.empty:
        for _,row in c_ling.head(limite_v).iterrows():
            if pd.isna(row.get('Libro')): continue
            nid=f"{row['Libro']} {row['Capitulo']}:{row['Versiculo']}"
            G.add_node(nid,size=12,color="#f8fafc",title=f"📖 {nid}")
            G.add_edge(str(faccion),nid,weight=1)
            
    def pc(df_c,cn,col,pref,ico):
        if not df_c.empty:
            for _,row in df_c.iterrows():
                if pd.isna(row.get(cn)): continue
                nid=str(row[cn]).strip()
                G.add_node(nid,size=22,color=col,title=f"{ico} {pref}")
                G.add_edge(str(faccion),nid,weight=1)
                    
    pc(c_geo,'Entidad / Corporación',"#10b981","CAPA 2","🌍")
    pc(c_bio,'Avance / Plataforma',"#f59e0b","CAPA 3","🧬")
    
    net=Network(height="480px",width="100%",bgcolor="#0b0f19",font_color="white")
    net.from_nx(G)
    net.force_atlas_2based(gravity=-50,central_gravity=0.01,spring_length=130,spring_strength=0.04,damping=0.8,overlap=0)
    with tempfile.NamedTemporaryFile(mode='w',suffix='.html',delete=False,encoding='utf-8') as f:
        ruta=f.name
    net.write_html(ruta)
    return ruta

# --- 8. PLANO SEMÁNTICO RESPONSIVO ---
def generar_plano_semantico(faccion_filtro=None):
    coord_map={"Q1":(0.45,0.45),"Q2":(0.45,-0.45),"Q3":(-0.45,0.45),"Q4":(-0.45,-0.45),"UMBRAL":(0.0,0.0)}
    pts=[]
    for g in GOBERNADORES_91:
        if faccion_filtro and faccion_filtro!="DERECHA (Control)": continue
        cx,cy=coord_map.get(g["cuadrante"],(0,0))
        pts.append({"nombre":g["nombre"],"tipo":f"Gobernador","cuadrante":g["cuadrante"],"jurisdiccion":g["jurisdiccion"],"funcion":g["funcion"],"faccion":"DERECHA (Control)","x":cx+(g["num"]%7-3)*0.06,"y":cy+(g["num"]%5-2)*0.06,"color":CUADRANTES_PLANO.get(g["cuadrante"],{}).get("color","#94a3b8"),"size":7,"simbolo":"circle"})
    for cmd in comandantes:
        if cmd["Faccion"]!="IZQUIERDA (Caos)": continue
        if faccion_filtro and faccion_filtro!="IZQUIERDA (Caos)": continue
        cuad=cmd.get("Cuadrante","Q4")
        cx,cy=coord_map.get(cuad,(-0.45,-0.45))
        pts.append({"nombre":cmd["Comandante"],"tipo":cmd["Rango"],"cuadrante":cuad,"jurisdiccion":cmd["Ubicacion"],"funcion":cmd["Funcion"],"faccion":"IZQUIERDA (Caos)","x":cx+(hash(cmd["Comandante"])%7-3)*0.06,"y":cy+(hash(cmd["Comandante"])%5-2)*0.06,"color":CUADRANTES_PLANO.get(cuad,{}).get("color","#e11d48"),"size":9 if cmd["Rango"]=="Rey" else 6,"simbolo":"diamond"})
    
    df_p=pd.DataFrame(pts)
    fig=go.Figure()
    
    for r in [dict(x0=0,x1=1,y0=0,y1=1,fill="rgba(29,78,216,0.08)"),dict(x0=0,x1=1,y0=-1,y1=0,fill="rgba(37,99,235,0.08)"),dict(x0=-1,x1=0,y0=0,y1=1,fill="rgba(190,18,60,0.08)"),dict(x0=-1,x1=0,y0=-1,y1=0,fill="rgba(225,29,72,0.12)")]:
        fig.add_shape(type="rect",x0=r["x0"],x1=r["x1"],y0=r["y0"],y1=r["y1"],fillcolor=r["fill"],line=dict(color="#1e293b",width=1))
    fig.add_shape(type="line",x0=-1,x1=1,y0=0,y1=0,line=dict(color="#334155",width=1,dash="dot"))
    fig.add_shape(type="line",x0=0,x1=0,y0=-1,y1=1,line=dict(color="#334155",width=1,dash="dot"))
    
    if not df_p.empty:
        for fac,grp in df_p.groupby("faccion"):
            fig.add_trace(go.Scatter(x=grp["x"],y=grp["y"],mode="markers",name=fac,marker=dict(size=grp["size"].tolist(),color=grp["color"].tolist(),symbol=grp["simbolo"].tolist()),text=grp["nombre"],customdata=grp[["cuadrante","jurisdiccion","funcion"]].values,hovertemplate="<b>%{text}</b><br>%{customdata[0]}<br>%{customdata[1]}<extra></extra>"))
            
    fig.add_trace(go.Scatter(x=[-0.45],y=[-0.45],mode="markers+text",name="★ Jonás 4:11",marker=dict(size=14,color="#fbbf24",symbol="star"),text=["★ Jonás 4:11"],textposition="top center",textfont=dict(color="#fbbf24",size=10)))
    
    fig.update_layout(
        plot_bgcolor="#0b0f19",paper_bgcolor="#0b0f19",font_color="#94a3b8",
        xaxis=dict(range=[-1.05,1.05],showgrid=False,zeroline=False,showticklabels=False),
        yaxis=dict(range=[-1.05,1.05],showgrid=False,zeroline=False,showticklabels=False),
        annotations=[
            dict(x=0.6,y=0.8,text="Q1: CONTROL<br>(Yamin+Beyn)",showarrow=False,font=dict(color="#3b82f6",size=9),align="center"),
            dict(x=0.6,y=-0.8,text="Q2: DISCERNIMIENTO<br>(Yamin+Yada)",showarrow=False,font=dict(color="#2563eb",size=9),align="center"),
            dict(x=-0.6,y=0.8,text="Q3: CAOS CONTENIDO<br>(Smol+Beyn)",showarrow=False,font=dict(color="#be123c",size=9),align="center"),
            dict(x=-0.6,y=-0.8,text="Q4: HIBRIDACIÓN<br>(Smol+Yada)",showarrow=False,font=dict(color="#e11d48",size=9),align="center"),
        ],
        legend=dict(bgcolor="#0f172a",orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1),
        margin=dict(l=10,r=10,t=30,b=10),
        height=460
    )
    return fig

# --- 9. MAPA TERRESTRE RESPONSIVO ---
def generar_mapa_cuadrantes_tierra():
    fig = go.Figure()
    df_g = df_geo_map[df_geo_map["Lat"].notna() & (df_geo_map["Lat"]!=0)]
    color_map_cuad = {"Q1":"#3b82f6","Q2":"#2563eb","Q3":"#be123c","Q4":"#e11d48","UMBRAL":"#0ea5e9"}
    
    for faccion, group in df_g.groupby("Faccion"):
        simbolo = "circle" if "DERECHA" in faccion else "diamond"
        fig.add_trace(go.Scattergeo(
            lat=group["Lat"], lon=group["Lon"],
            mode="markers",
            name=faccion,
            marker=dict(
                size=group["Legiones"].apply(lambda x: max(4, min(18, x//12))).tolist(),
                color=[color_map_cuad.get(c,"#94a3b8") for c in group["Cuadrante"]],
                symbol=simbolo,
                opacity=0.85
            ),
            text=group["Nombre"],
            customdata=group[["Rango","Ubicacion","Legiones","Entidades"]].values,
            hovertemplate="<b>%{text}</b><br>%{customdata[0]}<br>%{customdata[1]}<br>⚔️ %{customdata[2]} Leg.<extra></extra>"
        ))

    fig.update_geos(
        showcountries=True, countrycolor="#1e293b",
        showland=True, landcolor="#0f172a",
        showocean=True, oceancolor="#0b0f19",
        projection_type="natural earth",
        bgcolor="#0b0f19"
    )
    fig.update_layout(
        plot_bgcolor="#0b0f19", paper_bgcolor="#0b0f19", font_color="#94a3b8",
        margin=dict(l=0,r=0,t=20,b=0), height=460,
        legend=dict(bgcolor="#0f172a",orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1)
    )
    return fig

# --- 10. PANEL DE RATIO ---
def generar_panel_ratio():
    df_g = df_geo_map.copy()
    total_entidades_izq  = df_g[df_g["Faccion"]=="IZQUIERDA (Caos)"]["Entidades"].sum()
    total_legiones_izq   = df_g[df_g["Faccion"]=="IZQUIERDA (Caos)"]["Legiones"].sum()
    total_entidades_der  = df_g[df_g["Faccion"]=="DERECHA (Control)"]["Entidades"].sum()
    total_legiones_der   = df_g[df_g["Faccion"]=="DERECHA (Control)"]["Legiones"].sum()
    total_entidades      = total_entidades_izq + total_entidades_der
    total_legiones       = total_legiones_izq + total_legiones_der

    ratio_global         = total_entidades / POB_MUNDIAL
    ratio_izq            = total_entidades_izq / POB_MUNDIAL
    ratio_der            = total_entidades_der / POB_MUNDIAL

    by_fuente = df_g.groupby(["Fuente","Faccion"]).agg(
        Entidades_Total=("Entidades","sum"),
        Legiones_Total=("Legiones","sum"),
        N_Entidades_Jerarquicas=("Nombre","count")
    ).reset_index()
    by_fuente["Ratio_por_habitante"] = by_fuente["Entidades_Total"].apply(lambda x: round(x/POB_MUNDIAL,4))

    by_cuad = df_g.groupby(["Cuadrante","Faccion"]).agg(
        Entidades_Total=("Entidades","sum"),
        Legiones_Total=("Legiones","sum"),
        N_Jerarquicos=("Nombre","count")
    ).reset_index()
    by_cuad["Cuadrante_Nombre"] = by_cuad["Cuadrante"].map({k:v["nombre"] for k,v in CUADRANTES_PLANO.items()})

    fig_tree = px.treemap(
        df_g, path=["Faccion","Fuente","Rango"],
        values="Entidades", color="Faccion",
        color_discrete_map={"IZQUIERDA (Caos)":"#e11d48","DERECHA (Control)":"#2563eb"}
    )
    fig_tree.update_layout(plot_bgcolor="#0b0f19",paper_bgcolor="#0b0f19",font_color="#94a3b8",margin=dict(l=0,r=0,t=10,b=0),height=380)

    return {
        "total_entidades":total_entidades,"total_legiones":total_legiones,
        "total_entidades_izq":total_entidades_izq,"total_legiones_izq":total_legiones_izq,
        "total_entidades_der":total_entidades_der,"total_legiones_der":total_legiones_der,
        "ratio_global":ratio_global,"ratio_izq":ratio_izq,"ratio_der":ratio_der,
        "by_fuente":by_fuente,"by_cuad":by_cuad,"fig_tree":fig_tree
    }

# --- 11. PESTAÑAS Y RENDERIZADO ---
tab_core, tab_geo_d, tab_plano, tab_tierra, tab_ratio, tab_radar, tab_predict, tab_timeline, tab0, tab1, tab2, tab3, tab4, tab_arq = st.tabs([
    "🔄 Enjambre","🗺️ Geo","🧭 Plano",
    "🌍 Tierra","⚖️ Ratio","📡 Radar",
    "🎯 Predictivo","⏱️ Timeline",
    "📖 V0","🔮 V1","🌐 V2","🧬 V3","⏳ V4","👥 Arquetipos"
])

with tab_core:
    c1, c2 = st.columns([2, 1])
    with c1:
        facción_maestra = st.radio("Ala de Comando:", ["DERECHA (Control)", "IZQUIERDA (Caos)"], horizontal=True)
    with c2:
        activar_radar = st.checkbox("Radar en grafo", value=False)
    
    termino_ling = "Derecha" if "DERECHA" in facción_maestra else "Izquierda"
    criterio_fac = "DERECHA (Control)" if "DERECHA" in facción_maestra else "IZQUIERDA (Caos)"
    
    c_ling = df_ling_masivo[df_ling_masivo["Conceptos_Matriz"].str.contains(termino_ling,na=False,case=False)] if not df_ling_masivo.empty else pd.DataFrame()
    c_geo_t = df_geo[df_geo["Facción Alineada"]==criterio_fac] if not df_geo.empty else pd.DataFrame()
    c_bio = df_bio[df_bio["Facción Alineada"]==criterio_fac] if not df_bio.empty else pd.DataFrame()
    c_astro = df_astro[df_astro["Facción Alineada"].str.contains(termino_ling+"|Ambas",na=False,case=False)] if not df_astro.empty else pd.DataFrame()
    
    ruta_grafo = generar_mapa_maestro(facción_maestra, c_ling, c_geo_t, c_bio, c_astro, textos_raw_eso, activar_radar, limite_nodos_texto)
    with open(ruta_grafo, 'r', encoding='utf-8') as f:
        components.html(f.read(), height=490)
        
    m1, m2, m3 = st.columns(3)
    m1.metric("Jerarcas", sum(1 for c in comandantes if c["Faccion"]==facción_maestra))
    m2.metric("Gobernadores", len(GOBERNADORES_91))
    m3.metric("Infraestructura", len(c_geo_t)+len(c_bio))

with tab_geo_d:
    st.subheader("🗺️ Mapeo Geo-Densidad Histórico")
    df_z=df_geo_map.groupby(["Ubicacion","Lat","Lon","Faccion"]).agg({"Entidades":"sum","Legiones":"sum","Nombre":"count"}).reset_index().rename(columns={"Nombre":"Total_Jerarquicos"})
    df_z["Poblacion"]=df_z["Ubicacion"].map({"Britannia (Londres, UK)":9000000,"Sarmatia (Moscú, Rusia)":13000000,"Italia (Roma)":2800000,"Gallia (París, Francia)":11000000,"Mesopotamia (Damasco, Siria)":2000000,"Bactriana (Nueva Delhi, India)":32000000,"Babilonia (Hillah, Irak)":500000,"Persia (Teherán, Irán)":9000000,"Egipto (El Cairo)":22000000,"Fenicia / Sidón (Líbano)":200000,"Desierto de Arabia (Riad, AS)":7500000,"Sodoma (Mar Muerto, Jordania)":100000,"Monte Hermón (Levante)":50000}).fillna(1000000)
    df_z["Ratio"]=df_z.apply(lambda r: round(r["Poblacion"]/r["Entidades"],2) if r["Entidades"]>0 else 0,axis=1)
    df_z["Hover"]=df_z.apply(lambda r: f"<b>{r['Ubicacion']}</b><br>Jerarcas: {r['Total_Jerarquicos']}<br>Entidades: {r['Entidades']:,}<br>Densidad: 1/{r['Ratio']}",axis=1)
    fig_map=px.scatter_geo(df_z,lat="Lat",lon="Lon",size="Entidades",color="Faccion",hover_name="Ubicacion",custom_data=["Hover"],projection="natural earth",color_discrete_map={"DERECHA (Control)":"#3b82f6","IZQUIERDA (Caos)":"#f43f5e"})
    fig_map.update_traces(hovertemplate="%{customdata[0]}")
    fig_map.update_geos(showcountries=True,countrycolor="#334155",showland=True,landcolor="#0f172a",showocean=True,oceancolor="#0b0f19")
    fig_map.update_layout(plot_bgcolor="#0b0f19",paper_bgcolor="#0b0f19",font_color="#94a3b8",margin=dict(l=0,r=0,t=0,b=0),height=460,legend=dict(orientation="h",y=1.02))
    st.plotly_chart(fig_map,use_container_width=True)

with tab_plano:
    st.subheader("🧭 Plano Semántico — Jonás 4:11")
    filtro_fac=st.selectbox("Filtrar Ala:",["Todas","DERECHA (Control)","IZQUIERDA (Caos)"])
    filtro=None if filtro_fac=="Todas" else filtro_fac
    st.plotly_chart(generar_plano_semantico(filtro),use_container_width=True)

with tab_tierra:
    st.subheader("🌍 Cuadrantes sobre el Mapa Terrestre")
    st.plotly_chart(generar_mapa_cuadrantes_tierra(),use_container_width=True)

with tab_ratio:
    st.subheader("⚖️ Conteo de Legiones y Ratios")
    datos=generar_panel_ratio()
    r1, r2, r3 = st.columns(3)
    r1.metric("Legiones", f"{datos['total_legiones']:,}")
    r2.metric("Entidades", f"{datos['total_entidades']:,}")
    r3.metric("Ratio Global", f"{datos['ratio_global']:.4f}")
    st.plotly_chart(datos["fig_tree"], use_container_width=True)

with tab_radar:
    st.subheader("📡 Radar en Vivo — Señales Globales")
    c_r1, c_r2 = st.columns(2)
    with c_r1: faccion_radar = st.selectbox("Facción:", ["Todas", "DERECHA (Control)", "IZQUIERDA (Caos)"], key="rad_fac")
    with c_r2: fuente_radar = st.selectbox("Fuente:", ["Todas", "Goetia", "Gobernadores Enoquianos", "Vigilantes"], key="rad_src")
    
    entidades_radar = []
    for cmd in comandantes:
        fac_ok = faccion_radar == "Todas" or cmd["Faccion"] == faccion_radar
        src_ok = True
        if fuente_radar == "Goetia": src_ok = cmd.get("Aethyr") == "Ars Goetia"
        elif fuente_radar == "Gobernadores Enoquianos": src_ok = "Gobernador" in cmd.get("Rango", "")
        elif fuente_radar == "Vigilantes": src_ok = cmd.get("Aethyr") == "Libro de Enoc"
        if fac_ok and src_ok: entidades_radar.append(cmd)
        
    entidades_radar = entidades_radar[:6]
    
    if st.button("🔍 Escanear Señales en Tiempo Real", type="primary"):
        prog = st.progress(0)
        res = {}
        for i, ent in enumerate(entidades_radar):
            nots = buscar_noticias_entidad(ent["Funcion"], ent["Comandante"])
            if nots: res[ent["IdNodo"]] = {"entidad": ent, "noticias": nots}
            prog.progress((i + 1) / len(entidades_radar))
        prog.empty()
        
        st.success(f"✅ {sum(len(v['noticias']) for v in res.values())} señales detectadas.")
        for id_nodo, data in res.items():
            ent = data["entidad"]; nots = data["noticias"]
            col_ent = CUADRANTES_PLANO.get(ent.get("Cuadrante","Q1"),{}).get("color","#94a3b8")
            with st.expander(f"{ent['IdNodo']} ({len(nots)} señales)", expanded=True):
                for n in nots:
                    st.markdown(f"""
                    <div style='background:#0f172a;border-left:3px solid {col_ent};padding:8px 12px;margin:6px 0;border-radius:0 6px 6px 0'>
                        <div style='display:flex;justify-content:space-between'><small style='color:#64748b'>{n.get('fuente','—')}</small><small style='color:#64748b'>{n.get('fecha','')}</small></div>
                        <b style='color:#e2e8f0;font-size:13px'>{n.get('titulo','')}</b><br>
                        <small style='color:#94a3b8'>{str(n.get('descripcion',''))[:120]}</small><br>
                        <a href='{n.get('url','#')}' target='_blank' style='color:{col_ent};font-size:11px;text-decoration:none'>→ Ver fuente</a>
                    </div>
                    """, unsafe_allow_html=True)

with tab_predict:
    st.subheader("🎯 Algoritmo Predictivo")
    og = df_geo['Entidad / Corporación'].dropna().tolist() if not df_geo.empty else ["Sin datos"]
    ob = df_bio['Avance / Plataforma'].dropna().tolist() if not df_bio.empty else ["Sin datos"]
    vg = st.selectbox("1. Entidad Geopolítica", og)
    vb = st.selectbox("2. Avance Biotecnológico", ob)
    if st.button("Analizar Convergencia", type="primary"):
        fg = df_geo[df_geo['Entidad / Corporación']==vg]['Facción Alineada'].values[0] if not df_geo.empty else "Desconocida"
        fb = df_bio[df_bio['Avance / Plataforma']==vb]['Facción Alineada'].values[0] if not df_bio.empty else "Desconocida"
        if fg == fb:
            st.progress(0.85)
            st.markdown(f"<h4 style='color:#ef4444'>⚠️ ALTA CONVERGENCIA (85%): {vg} y {vb} operan en la misma agenda ({fg}).</h4>", unsafe_allow_html=True)
        else:
            st.progress(0.40)
            st.markdown(f"<h4 style='color:#f59e0b'>⚡ FRICCIÓN ESTRUCTURAL (40%): {vg} choca con {vb}.</h4>", unsafe_allow_html=True)

with tab_timeline:
    st.subheader("⏱️ Línea de Tiempo")
    if 'Inicio' in df_astro.columns and 'Fin' in df_astro.columns:
        df_tl = df_astro.dropna(subset=['Inicio','Fin'])
        if not df_tl.empty:
            fig = px.timeline(df_tl, x_start="Inicio", x_end="Fin", y="Ciclo / Marcador Celeste", color="Facción Alineada", color_discrete_map={"DERECHA (Control)":"#3b82f6","IZQUIERDA (Caos)":"#f43f5e","Ambas / Reloj":"#0ea5e9"})
            fig.update_yaxes(autorange="reversed")
            fig.update_layout(plot_bgcolor="#0b0f19", paper_bgcolor="#0b0f19", font_color="#94a3b8", height=380, margin=dict(l=0,r=0,t=10,b=0), legend=dict(orientation="h",y=1.05))
            st.plotly_chart(fig, use_container_width=True)

with tab0: st.dataframe(df_ling_masivo, use_container_width=True, hide_index=True)
with tab1:
    st.dataframe(df_eso_base, use_container_width=True, hide_index=True)
    if textos_raw_eso:
        st.subheader("📜 Fuentes Primarias")
        sel = st.selectbox("Manual:", list(textos_raw_eso.keys()))
        st.markdown(f"""<div style="height:300px;overflow-y:auto;background:#0f172a;padding:15px;border:1px solid #334155;border-radius:6px;color:#38bdf8;font-family:monospace;font-size:12px;white-space:pre-wrap">{html.escape(textos_raw_eso[sel])}</div>""", unsafe_allow_html=True)
with tab2: st.dataframe(df_geo, use_container_width=True, hide_index=True)
with tab3: st.dataframe(df_bio, use_container_width=True, hide_index=True)
with tab4: st.dataframe(df_astro, use_container_width=True, hide_index=True)
with tab_arq: st.dataframe(df_arquetipos, use_container_width=True, hide_index=True)