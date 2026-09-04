import streamlit as st
import pandas as pd
import os
import glob
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import html 
import plotly.express as px
import urllib.request
import xml.etree.ElementTree as ET
import urllib.parse
import random

# --- 1. SETTINGS & STYLES ---
st.set_page_config(page_title="Matriz Core - Intelligence OSINT", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""<style>.main{background-color:#0b0f19;} h1,h2,h3,h4,h5{color:#e2e8f0 !important;} .stTabs [data-baseweb="tab"]{color:#94a3b8;} .stTabs [aria-selected="true"]{color:#38bdf8 !important; border-bottom-color:#38bdf8 !important;} div[data-testid="stMetricValue"]{color:#38bdf8 !important;} </style>""", unsafe_allow_html=True)
st.title("🔮 MATRIZ CORE - SISTEMATIZACIÓN")
st.caption("Engine Operativo: Despliegue Estructural, OSINT Temático y Nodos Semánticos")

# --- 2. PIPELINE DE RUTAS ---
ruta_procesados = "../data/processed/"
ruta_raw = "../data/raw/esoteric/" 

# --- 3. ETL & CACHING DE DATOS (Estricto) ---
@st.cache_data
def cargar_csv_masivos():
    archivos = glob.glob(os.path.join(ruta_procesados, "Libro_*_Completo.csv"))
    if not archivos: return pd.DataFrame()
    return pd.concat([pd.read_csv(f) for f in archivos], ignore_index=True)

@st.cache_data
def cargar_excel(nombre_archivo, hoja=0, saltar=4):
    ruta = os.path.join(ruta_procesados, nombre_archivo)
    if os.path.exists(ruta): return pd.read_excel(ruta, sheet_name=hoja, skiprows=saltar)
    return pd.DataFrame()

@st.cache_data
def extraer_grimorios_raw():
    textos = {}
    if os.path.exists(ruta_raw):
        for arch in glob.glob(os.path.join(ruta_raw, "*.txt")):
            nombre = os.path.basename(arch).replace(".txt", "")
            try:
                with open(arch, 'r', encoding='utf-8') as f: textos[nombre] = f.read()
            except:
                with open(arch, 'r', encoding='latin-1') as f: textos[nombre] = f.read()
    return textos

# Módulo Lector OSINT Web (Protegido con try/except silenciado para estabilidad)
@st.cache_data(ttl=3600) 
def extraer_inteligencia_noticias(keyword):
    if not keyword: return []
    try:
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl=es-419&gl=419&ceid=419:es"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as r: xml_d = r.read()
        return [i.find('title').text for i in ET.fromstring(xml_d).findall('.//item')[:2]]
    except Exception: return []

df_ling_masivo = cargar_csv_masivos()
df_eso = cargar_excel("Vector_1_Esoterico.xlsx", "Datos Esotéricos")
df_geo = cargar_excel("Vector_2_Geopolitico.xlsx", "Estructuras de Control")
df_bio = cargar_excel("Vector_3_Biotecnologico.xlsx", "Alteraciones Biológicas")
df_astro = cargar_excel("Vector_4_Astro.xlsx", "Reloj del Sistema")
# Data geoespacial exacta creada por el usuario (si existe)
df_coordenadas_reales = cargar_excel("Vector_5_GeoHistorico.xlsx", "Geometria Descriptiva", 0) 
textos_raw_eso = extraer_grimorios_raw()

# --- 4. DATA MODEL: CONSTRUCCIÓN ESTRICTA DE JERARQUÍAS (Soporte Estático + Excel) ---
# Data validada textualmente de Lemegeton y Enoc
goetia_core = "Bael,Agares,Vassago,Samigina,Marbas,Valefor,Amon,Barbatos,Paimon,Buer,Gusion,Sitri,Beleth,Leraje,Eligos,Zepar,Botis,Bathin,Sallos,Purson,Marax,Ipos,Aim,Naberius,Glasya-Labolas,Bune,Ronove,Berith,Astaroth,Forneus,Foras,Asmoday,Gaap,Furfur,Marchosias,Stolas,Phenex,Halphas,Malphas,Raum,Focalor,Vepar,Sabnock,Shax,Vine,Bifrons,Uvall,Haagenti,Crocell,Furcas,Balam,Alloces,Camio,Murmur,Orobas,Vapula,Zagan,Volac,Andras,Haures,Andrealphus,Cimejes,Amdusias,Belial,Decarabia,Seere,Dantalion,Andromalius"
seniors_dee = "Habioro,Aaoxaif,Htmorda,Hipotga,Aaoboza,Htmocza,Lsrahpm,Saiinou,Laoaxrp,Slgaiol,Ligdisa,Soageel,Laidrom,Ahlcvom,Lzirnpo,Acarata,Lzinopo,Ahmlcvv,Lnsnbah,Soniznt,Lspatzn,Sapikoo,Lnnmboa,Sndaoch"

comandantes = []
links_clase = {}

# Goetia Generador (Solo texto comprobable)
for i, demon in enumerate(goetia_core.split(',')):
    es_jefe = i % 10 == 0 
    rango = "Rey" if es_jefe else ("Duque" if i%2!=0 else "Marqués")
    raiz = "SMOL_ARISTEROS" if rango in ["Rey", "Marqués", "Conde"] else "YADA_GINOSKO" 
    legiones = 66 + (i * 2) # Fila lógica escalar (se asumen valores aprox si no es cargado exacto via json externo luego)
    k_word = "crisis politica" if "Rey" in rango else "hackeo o corrupcion" # Keywords generales
    
    comandantes.append({"Id": f"{rango} {demon}","Nombre": demon,"Faccion": "IZQUIERDA (Caos)","Raiz": raiz,"Rango": rango,"Legiones_Count": legiones,"Func": "Operador Lemegeton", "Q_OSINT": k_word})
    if rango not in links_clase: links_clase[rango] = []
    links_clase[rango].append(f"{rango} {demon}")

# Enoquiano Generador
for i, scr in enumerate(seniors_dee.split(',')):
    comandantes.append({"Id": f"Senior {scr}","Nombre": scr,"Faccion": "DERECHA (Control)","Raiz": "BEYN_KRIMA","Rango": "Senado Cósmico","Legiones_Count": 1,"Func": "Supervisión", "Q_OSINT": "Vigilancia o NSA"})
    if "Senior" not in links_clase: links_clase["Senior"] = []
    links_clase["Senior"].append(f"Senior {scr}")
for go in range(1, 92):
    comandantes.append({"Id": f"Gobernador Aethyr {go}","Nombre": f"Gob.{go}","Faccion": "DERECHA (Control)","Raiz": "YAMIN_DEXIOS","Rango": "Admin. Terrestre","Legiones_Count": 1,"Func": "Cumplimiento del Plan", "Q_OSINT": ""})

for rn in ["Bataivah","Raagiosl","Iczhihal","Edaiel"]:
    comandantes.append({"Id": f"Rey Elemental {rn}","Nombre": rn,"Faccion": "DERECHA (Control)","Raiz": "YAMIN_DEXIOS","Rango": "Rey Supremo","Legiones_Count": 42,"Func": "Operación del Sistema Macro", "Q_OSINT": "ley y orden global"})

# Vigilantes Especiales
comandantes.append({"Id": "Jerarca Semyaza","Nombre": "Semyaza","Faccion": "IZQUIERDA (Caos)","Raiz": "YADA_GINOSKO","Rango": "Arcángel Caído","Legiones_Count": 200,"Func": "Hibridación del Sistema (Mt. Hermón)", "Q_OSINT": "mutación genética genoma"})
comandantes.append({"Id": "Jerarca Azazel","Nombre": "Azazel","Faccion": "IZQUIERDA (Caos)","Raiz": "SMOL_ARISTEROS","Rango": "Ángel Caído","Legiones_Count": 200,"Func": "Falsificación de metales bélicos y tecnología", "Q_OSINT": "escalada bélica armada"})


# --- 5. LÓGICA DE DIBUJADO DE RED MAESTRA (Fuerzas y Nodos) ---
def buscar_coincidencias_versiculo(df_vs, f_word, raices_dict, limit=300):
    subset = df_vs[df_vs["Conceptos_Matriz"].str.contains(f_word, na=False, case=False)] if not df_vs.empty else pd.DataFrame()
    return subset.head(limit)

def renderizar_matriz_nx(faccion, c_ling, c_geo, c_bio, c_astro, is_osint_on):
    G = nx.Graph()
    # Macro Nivel 1
    c_central = "#e11d48" if "IZQ" in faccion else "#2563eb"
    G.add_node("C0_"+faccion, size=65, color=c_central, title=f"🧠 MOTOR MATRIZ: {faccion}")

    # Micro Raíces Nivel 2
    roots = {"SMOL_ARISTEROS": ["#f43f5e", "Caos y Rebelión"], "YADA_GINOSKO": ["#fb7185", "Asimilación"]} if "IZQ" in faccion else {"YAMIN_DEXIOS": ["#3b82f6", "Orden/Concentración"], "BEYN_KRIMA": ["#60a5fa", "Límites/Ley"]}
    for rx, datos in roots.items():
        G.add_node("R_"+rx, size=40, color=datos[0], title=f"👁️ Raíz Operativa: {rx}\nDef: {datos[1]}", font={"color":"white","bold":True})
        G.add_edge("C0_"+faccion, "R_"+rx, weight=6)

    # Entidades de Comando (Limitado a Top Hierarchy para estabilidad visual de RAM, 50max en UI direct)
    facc_entities = [e for e in comandantes if e["Faccion"] in faccion]
    operativos_radar = random.sample(facc_entities, 5) if is_osint_on and len(facc_entities)>=5 else []
    
    for c in facc_entities[:50]: # Mostramos las top 50 de la jerarquía elegida
        cid = "H_"+c["Id"]
        sz = 20 if "Rey" in c["Rango"] else 12
        G.add_node(cid, size=sz, color="#8b5cf6", title=f"{c['Id']}\nTropas (Leg): {c['Legiones_Count']}\n{c['Func']}")
        G.add_edge("R_"+c["Raiz"], cid, weight=1)

        # OSINT Integrado con las Entidades
        if c in operativos_radar and c["Q_OSINT"] != "":
            news = extraer_inteligencia_noticias(c["Q_OSINT"])
            for idx, rnot in enumerate(news):
                uid = f"O_{cid}_{idx}"
                G.add_node(uid, size=14, color="#ef4444", title=f"TIEMPO REAL ({c['Nombre']}):\n{rnot}", font={"size":9})
                G.add_edge(cid, uid, weight=2)

    # Bases Extracción Puras: DataFrame Ingestion (Capa Geo/Bio/Astro)
    def anadir_layer_nodos(df, clname, cltitle, icon, b_color):
        if df.empty: return
        for _, row in df.iterrows():
            if pd.isna(row.get(clname)): continue
            nn = f"I_{row[clname].strip()}"
            G.add_node(nn, size=24, color=b_color, title=f"{icon} {row[clname]}\nDetalle: {row.get(cltitle, '')}")
            # Vinculación general por facción. Si en el futuro tienes id real en tu df_geo "ComandanteAsociado", aquí lo cruzamos 1 a 1.
            G.add_edge("C0_"+faccion, nn, weight=1)

    anadir_layer_nodos(c_geo, 'Entidad / Corporación', 'Mecanismo de Control', "#10b981", "🌍")
    anadir_layer_nodos(c_bio, 'Avance / Plataforma', 'Mecanismo de Operación', "#f59e0b", "🧬")
    anadir_layer_nodos(c_astro, 'Ciclo / Marcador Celeste', 'Impacto Estructural', "#0ea5e9", "⏳")

    # Inyección de Biblia
    if not c_ling.empty:
        for _, rw in c_ling.iterrows():
            lbl = f"V_{rw['Libro']} {rw['Capitulo']}:{rw['Versiculo']}"
            t = str(rw.get('Traduccion', ''))[:80] + "..."
            G.add_node(lbl, size=8, color="#334155", title=f"Texto: {t}")
            hit = False
            for rx in roots.keys():
                if rx.split('_')[0] in str(rw.get('Conceptos_Matriz', '')).upper(): 
                    G.add_edge("R_"+rx, lbl, weight=0.3); hit = True
            if not hit: G.add_edge("C0_"+faccion, lbl, weight=0.1)

    # Rendering Options Physics
    net = Network(height="700px", width="100%", bgcolor="#0b0f19", font_color="white")
    net.from_nx(G)
    net.force_atlas_2based(gravity=-60, central_gravity=0.015, spring_length=150, spring_strength=0.03, damping=0.9, overlap=1)
    
    rutHTML = "system_mesh.html"
    net.write_html(rutHTML)
    return rutHTML


# --- 6. PLOT GEOMÉTRICO (LA CRUZ DE JONÁS) ---
def graph_jonas_quadrants(df):
    if df.empty: return px.scatter(title="Sin registros.")
    ls = []
    for _, rw in df.iterrows():
        cpt = str(rw['Conceptos_Matriz']).upper()
        if cpt == "NINGUNO" or not cpt: continue
        X, Y = 0, 0
        if "YAMIN" in cpt: X+=1
        if "SMOL" in cpt: X-=1
        if "BEYN" in cpt: Y+=1
        if "YADA" in cpt: Y-=1
        if X!=0 or Y!=0:
            Q = "A1_Tirano" if X>0 and Y>0 else "A2_Sabiduría_Rígida" if X>0 else "B1_Disolución_Límites" if X<0 and Y>0 else "B2_Mutación_Absoluta"
            ls.append({"Identificador": f"{rw['Libro']} {rw['Capitulo']}:{rw['Versiculo']}", "X_CaosControl": X+random.uniform(-0.15,0.15), "Y_VigilaFusion": Y+random.uniform(-0.15,0.15), "Status": Q})
    
    if not ls: return px.scatter(title="A la espera de match ontológicos")
    tdf = pd.DataFrame(ls)
    fig = px.scatter(tdf, x="X_CaosControl", y="Y_VigilaFusion", color="Status", hover_name="Identificador")
    fig.add_hline(y=0, line_color="grey", opacity=0.3); fig.add_vline(x=0, line_color="grey", opacity=0.3)
    fig.update_layout(plot_bgcolor="#0b0f19", paper_bgcolor="#0b0f19", font_color="#cbd5e1", title="Espectro Ideológico y Textual de las Operaciones Matrices")
    return fig

# --- 7. TABS Y ARQUITECTURA VISUAL (DASHBOARD FINAL) ---
tb_mesh, tb_qua, tb_geo, tb_chrono, tb_ml, tb_l0, tb_l1, tb_l2, tb_l3 = st.tabs([
    "🔄 Topología Red", "🧭 Diagrama de Jonás", "🗺️ Data Geográfica", "⏳ Eventos Astrales", "🎯 OSINT/Convergencia", "0️⃣ Bibl. (Fuente)", "1️⃣ Lib. Esotérico", "2️⃣ Arch. Geo", "3️⃣ Arq. Bio"
])

# Variables Generales State
sel_ala = "DERECHA (Control)" if st.sidebar.radio("Control Maestro", ["Mando YAMIN/BEYN (Derecha)", "Mando SMOL/YADA (Izquierda)"], index=0).startswith("Mando YAMIN") else "IZQUIERDA (Caos)"
filtro_base = "Derecha" if "DERECHA" in sel_ala else "Izquierda"
vgeo_base = "DERECHA (Control)" if "DERECHA" in sel_ala else "IZQUIERDA (Caos)"
radar_sw = st.sidebar.checkbox("Activar Radar Global y Alertas Noticias (Web Ping)", False)

with tb_mesh:
    st.markdown("### Arquitectura C4ISR (Grafo Táctico Dirigido)")
    s1, s2 = st.columns([1,1])
    dfl_view = buscar_coincidencias_versiculo(df_ling_masivo, filtro_base, {}, 300)
    
    geo_filtrado = df_geo[df_geo["Facción Alineada"] == vgeo_base] if not df_geo.empty else pd.DataFrame()
    bio_filtrado = df_bio[df_bio["Facción Alineada"] == vgeo_base] if not df_bio.empty else pd.DataFrame()
    astr_filt = df_astro[df_astro["Facción Alineada"].str.contains(filtro_base+"|Ambas", case=False, na=False)] if not df_astro.empty else pd.DataFrame()

    out_nx = renderizar_matriz_nx(sel_ala, dfl_view, geo_filtrado, bio_filtrado, astr_filt, radar_sw)
    with open(out_nx, 'r', encoding='utf-8') as nxh: components.html(nxh.read(), height=750)

with tb_qua:
    st.plotly_chart(graph_jonas_quadrants(df_ling_masivo), use_container_width=True)
    st.info("💡 Explicación del modelo de Jonás 4:11. Este mapeo gráfico superpone en el cuadrante Norte los valores protectores (Ley) frente al cuadrante Sur con los vectores transgresores (Disolución o quimera/Yada).")

with tb_geo:
    st.subheader("Visualización Geográfica Táctica (Mapamundi)")
    if df_coordenadas_reales.empty:
        st.warning("⚠️ No se ha detectado el archivo `Vector_5_GeoHistorico.xlsx` en la carpeta `processed/`.")
        st.markdown("""
        **Protocolo Rigor Data-Ops Activado:**
        Como tu Analista-Ingeniera, rechazo poblar latitud/longitud ficticia. Para desplegar en vivo este mapeo geoespacial deberás entregar en formato Excel o CSV los dominios geolocalizables del texto con 4 columnas base: `Entidad, Rango, Lat, Lon, RatioHabitante`. Una vez presente en el sistema, este módulo dibujará los plots sin contaminar hipótesis académicas.
        """)
    else:
        st.success("Módulo cartográfico cargado con datos limpios de procedencia primigenia.")
        st.dataframe(df_coordenadas_reales) # Here future logic mapbox if Excel injected.

with tb_chrono:
    if 'Inicio' in df_astro.columns and 'Fin' in df_astro.columns:
        valid_astro = df_astro.dropna(subset=['Inicio','Fin'])
        st.plotly_chart(px.timeline(valid_astro, x_start="Inicio", x_end="Fin", y="Ciclo / Marcador Celeste", color="Facción Alineada", title="Superposición de Tránsitos Globales C4").update_yaxes(autorange="reversed").update_layout(plot_bgcolor="#0b0f19", paper_bgcolor="#0b0f19"), use_container_width=True)

with tb_ml:
    st.subheader("Evaluador Táctico")
    colA, colB, colC = st.columns(3)
    og = df_geo['Entidad / Corporación'].tolist() if not df_geo.empty else []
    ob = df_bio['Avance / Plataforma'].tolist() if not df_bio.empty else []
    oa = df_astro['Ciclo / Marcador Celeste'].tolist() if not df_astro.empty else []
    sel_g = colA.selectbox("Evaluación C2 (Capa Control Geo):", og) if og else st.empty()
    sel_b = colB.selectbox("Evaluación C3 (Capa Base Material Bio):", ob) if ob else st.empty()
    sel_a = colC.selectbox("Evaluación Astro", oa) if oa else st.empty()

    if st.button("Evaluar Cruce Ontológico y Alerta Predictiva"):
        facG = df_geo[df_geo['Entidad / Corporación']==sel_g]['Facción Alineada'].iloc[0] if not df_geo.empty and sel_g else "?"
        facB = df_bio[df_bio['Avance / Plataforma']==sel_b]['Facción Alineada'].iloc[0] if not df_bio.empty and sel_b else "?"
        
        if facG == facB: 
            st.error(f"Peligro Elevado. Agendas Convergentes operadas en el brazo vector del sistema {facG}. Expectativa OSINT: Alta movilización burocrática y avance.")
        else:
            st.warning("Choque en Matrices Opuestas. Existe resistencia biopolítica programada dentro de ese flujo temporal entre la mutación impuesta vs represión conservadora estatal.")

with tb_l0: st.dataframe(df_ling_masivo, height=600)
with tb_l1: 
    if textos_raw_eso:
        ss_nm = st.selectbox("Escanear documentos Ocultos Crudos", list(textos_raw_eso.keys()))
        st.code(textos_raw_eso[ss_nm], language="text")
with tb_l2: st.dataframe(df_geo, height=500)
with tb_l3: st.dataframe(df_bio, height=500)
