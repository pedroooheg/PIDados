import math
import pandas as pd
import numpy as np
import folium
from branca.colormap import linear

# ==========================
# CONFIG
# ==========================
CSV_UNIDADES = 'data/retiradas_unidades_coords.csv'  
SAIDA_AGREGADO = 'data/total_retirado_por_subprefeitura.csv'
SAIDA_UBS_COM_SUB = 'data/unidades_com_subprefeitura.csv'
SAIDA_MAPA = 'mapa_retiradas_por_subprefeitura.html'

CENTRO_MAPA = (-23.5504533, -46.6339112)
ZOOM_INICIAL = 11

# ==========================
# LISTA DE SUBPREFEITURAS
# ==========================
SUBPREFEITURAS_NOMES = [
    "ARICANDUVA/CARRAO/FORMOSA",
    "BUTANTA",
    "CAMPO LIMPO",
    "CAPELA DO SOCORRO",
    "CASA VERDE/CACHOEIRINHA",
    "CIDADE ADEMAR",
    "CIDADE TIRADENTES",
    "ERMELINO MATARAZZO",
    "FREGUESIA DO Ó/BRASILANDIA",
    "GUAIANASES",
    "IPIRANGA",
    "ITAIM PAULISTA",
    "ITAQUERA",
    "JABAQUARA",
    "JACANA/TREMEMBE",
    "LAPA",
    "M'BOI MIRIM",
    "MOOCA",
    "PARELHEIROS",
    "PENHA",
    "PERUS/ANHANGUERA",
    "PINHEIROS",
    "PIRITUBA/JAGUARÁ",
    "SANTANA/TUCURUVI",
    "SANTO AMARO",
    "SÃO MATEUS",
    "SÃO MIGUEL PAULISTA",
    "SAPOPEMBA",
    "SÉ",
    "VILA GUILHERME/VILA MARIA",
    "VILA MARIANA",
    "VILA PRUDENTE",
]

# ==========================
# COORDENADAS DAS SUBPREFEITURAS
# ==========================
SUBPREFEITURAS_COORDS = [
    (-23.550430052216736, -46.548130291731596),
    (-23.588296096015526, -46.738057832211524),
    (-23.642683208940728, -46.73572483036189),
    (-23.720364719421255, -46.70179456104367),
    (-23.51183182164657,  -46.66643130337813),
    (-23.667415349982917, -46.674452445703004),
    (-23.583051720000892, -46.41631900152808),
    (-23.507546748924362, -46.47939628433965),
    (-23.47654108642168,  -46.665147061049694),
    (-23.54332354103735,  -46.41557085530023),
    (-23.587309767601738, -46.60304795919856),
    (-23.49331634883583,  -46.41708274570736),
    (-23.5302126850067,   -46.45865418064269),
    (-23.64775521581886,  -46.6399396634496),
    (-23.468032720724985, -46.58223723036629),
    (-23.522097228178144, -46.69539851502312),
    (-23.66734998206765,  -46.728466489880475),
    (-23.551001980939386, -46.59838612056709),
    (-23.81526645666646,  -46.735606009797074),
    (-23.518511626890536, -46.52101281687136),
    (-23.407068285415424, -46.75309421687395),
    (-23.56312289083323,  -46.70320171317356),
    (-23.48849965931681,  -46.72733521687191),
    (-23.481274592421936, -46.60366369228914),
    (-23.651223287435396, -46.707038761045496),
    (-23.59953750034677,  -46.46874487269204),
    (-23.500360216626017, -46.45127800337821),
    (-23.600357569614758, -46.512645359198444),
    (-23.5479893124978,   -46.634684288035125),
    (-23.52155166879476,  -46.60413813221306),
    (-23.598291372734437, -46.64944998618565),
    (-23.58259946041313,  -46.56132291871817),
]

# ==========================
# FUNÇÕES AUXILIARES
# ==========================
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    f1, f2 = math.radians(lat1), math.radians(lat2)
    dlat = f2 - f1
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(f1)*math.cos(f2)*math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def carregar_unidades(caminho_csv: str) -> pd.DataFrame:
    with open(caminho_csv, 'r', encoding='utf-8') as f:
        primeira = f.readline()
    sep = ';' if ';' in primeira else ','

    df = pd.read_csv(caminho_csv, sep=sep, encoding='utf-8')
    df.columns = df.columns.str.strip().str.lower()

    required = {'id_unidade', 'nome', 'latitude', 'longitude', 'total_retirado'}
    if not required.issubset(df.columns):
        raise KeyError(f"CSV deve conter colunas: {sorted(required)}")

    # converter lat, lon, total
    for col in ['latitude', 'longitude', 'total_retirado']:
        df[col] = df[col].astype(str).str.replace(',', '.').astype(float)

    return df

def montar_df_subprefeituras():
    return pd.DataFrame([
        {"nome": nome, "latitude": lat, "longitude": lon}
        for nome, (lat, lon) in zip(SUBPREFEITURAS_NOMES, SUBPREFEITURAS_COORDS)
    ])

def vincular_por_proximidade(df_unidades, df_sub):
    dists = np.zeros((len(df_unidades), len(df_sub)))

    for j, sp in df_sub.iterrows():
        dists[:, j] = [
            haversine_km(df_unidades.loc[i, 'latitude'], df_unidades.loc[i, 'longitude'],
                         sp['latitude'], sp['longitude'])
            for i in range(len(df_unidades))
        ]

    idx_min = dists.argmin(axis=1)

    df_unidades['subprefeitura'] = [df_sub.loc[j, 'nome'] for j in idx_min]
    df_unidades['dist_km'] = [dists[i, idx_min[i]] for i in range(len(df_unidades))]

    return df_unidades

# ==========================
# MAPA + CSV
# ==========================
def gerar_mapa_e_csv(df_u_sub, df_sub):

    # agregação por subprefeitura
    agreg = df_u_sub.groupby('subprefeitura', as_index=False).agg(
        total_retirado_subpref=('total_retirado', 'sum'),
        qtd_unidades=('id_unidade', 'nunique')
    )

    # juntar coordenadas
    df_plot = agreg.merge(df_sub, left_on='subprefeitura', right_on='nome', how='left')

    df_plot[['subprefeitura', 'total_retirado_subpref', 'qtd_unidades',
             'latitude', 'longitude']].to_csv(SAIDA_AGREGADO, index=False, encoding='utf-8')

    # ===== MAPA =====
    m = folium.Map(location=CENTRO_MAPA, zoom_start=ZOOM_INICIAL)

    min_total = df_plot['total_retirado_subpref'].min()
    max_total = df_plot['total_retirado_subpref'].max()

    colormap = linear.YlOrRd_09.scale(min_total, max_total)
    colormap.caption = "Total de medicamentos retirados"
    colormap.add_to(m)

    for _, r in df_plot.iterrows():
        radius = 10 + 25 * (r['total_retirado_subpref'] - min_total) / (max_total - min_total)
        folium.CircleMarker(
            location=(r['latitude'], r['longitude']),
            radius=radius,
            color=colormap(r['total_retirado_subpref']),
            fill=True,
            fill_color=colormap(r['total_retirado_subpref']),
            fill_opacity=0.8,
            tooltip=f"{r['subprefeitura']} — Total: {int(r['total_retirado_subpref']):,}".replace(",", ".")
        ).add_to(m)

    m.save(SAIDA_MAPA)
    print(f"✔ Mapa salvo em: {SAIDA_MAPA}")
    print(f"✔ CSV agregado salvo em: {SAIDA_AGREGADO}")

# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    df_unidades = carregar_unidades(CSV_UNIDADES)
    df_sub = montar_df_subprefeituras()

    # vincular UBS → Subprefeitura
    df_join = vincular_por_proximidade(df_unidades, df_sub)

    # salvar UBS com subprefeitura (NOVO)
    df_join.to_csv(SAIDA_UBS_COM_SUB, index=False, encoding="utf-8")
    print(f"✔ Arquivo salvo: {SAIDA_UBS_COM_SUB}")

    # gerar mapa + csv agregado
    gerar_mapa_e_csv(df_join, df_sub)
