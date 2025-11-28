import math
import json
import time
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from pathlib import Path
from branca.colormap import linear

# ==========================
# CONFIG
# ==========================
CSV_UNIDADES = 'data/retiradas_unidades_coords.csv'  # id_unidade;nome;latitude;longitude;total_retirado (com cabeçalho)
SAIDA_AGREGADO = 'data/total_retirado_por_subprefeitura.csv'
SAIDA_MAPA = 'mapa_retiradas_por_subprefeitura.html'

CENTRO_MAPA = (-23.5504533, -46.6339112)
ZOOM_INICIAL = 11

# ==========================
# LISTA DE SUBPREFEITURAS (NOMES)
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
# COORDENADAS FIXAS
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

assert len(SUBPREFEITURAS_NOMES) == len(SUBPREFEITURAS_COORDS), \
    f"Qtd nomes ({len(SUBPREFEITURAS_NOMES)}) != qtd coords ({len(SUBPREFEITURAS_COORDS)})"

# ==========================
# HELPERS
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
    if not required.issubset(set(df.columns)):
        raise KeyError(f"CSV deve conter colunas: {sorted(required)}. Encontradas: {df.columns.tolist()}")

    for col in ['latitude', 'longitude', 'total_retirado']:
        df[col] = df[col].astype(str).str.replace(',', '.', regex=False).astype(float)

    df = df[(df['latitude'].between(-34, 6)) & (df['longitude'].between(-74, -28))]
    return df


def montar_df_subprefeituras() -> pd.DataFrame:
    rows = []
    for nome, (lat, lon) in zip(SUBPREFEITURAS_NOMES, SUBPREFEITURAS_COORDS):
        rows.append({"nome": nome, "latitude": lat, "longitude": lon})
    return pd.DataFrame(rows)


def vincular_por_proximidade(df_unidades: pd.DataFrame, df_sub: pd.DataFrame) -> pd.DataFrame:
    subs = df_sub.reset_index(drop=True)
    un = df_unidades.reset_index(drop=True)

    dists = np.zeros((len(un), len(subs)), dtype=float)
    for j, sp in subs.iterrows():
        dists[:, j] = [
            haversine_km(un.loc[i, 'latitude'], un.loc[i, 'longitude'], sp['latitude'], sp['longitude'])
            for i in range(len(un))
        ]

    idx_min = dists.argmin(axis=1)
    un['subprefeitura'] = [subs.loc[j, 'nome'] for j in idx_min]
    un['dist_km'] = [dists[i, idx_min[i]] for i in range(len(un))]
    return un


def gerar_mapa_e_csv(df_u_sub: pd.DataFrame, df_sub: pd.DataFrame):
    # agrega: soma total_retirado e conta unidades
    agreg = (
        df_u_sub
        .groupby('subprefeitura', as_index=False)
        .agg(
            total_retirado_subpref=('total_retirado', 'sum'),
            qtd_unidades=('id_unidade', 'nunique')
        )
    )

    # junta com coordenadas fixas
    df_plot = agreg.merge(df_sub, left_on='subprefeitura', right_on='nome', how='left')
    df_plot = df_plot.dropna(subset=['latitude', 'longitude'])

    # salva CSV (para BI, etc.)
    df_plot[['subprefeitura', 'total_retirado_subpref', 'qtd_unidades',
             'latitude', 'longitude']].to_csv(
        SAIDA_AGREGADO, index=False, encoding='utf-8'
    )

    # ==========================
    # MAPA BONITO: BOLHAS COLORIDAS
    # ==========================
    m = folium.Map(location=CENTRO_MAPA, zoom_start=ZOOM_INICIAL, tiles='OpenStreetMap')

    min_total = df_plot['total_retirado_subpref'].min()
    max_total = df_plot['total_retirado_subpref'].max()

    # escala de cores (amarelo -> vermelho)
    colormap = linear.YlOrRd_09.scale(min_total, max_total)
    colormap.caption = 'Total retirado por subprefeitura'
    colormap.add_to(m)

    min_radius = 10
    max_radius = 35

    for _, r in df_plot.iterrows():
        total = r['total_retirado_subpref']
        tot_fmt = f"{int(total):,}".replace(",", ".")
        # normaliza pra definir raio
        raio = min_radius + (max_radius - min_radius) * (total - min_total) / (max_total - min_total)
        color = colormap(total)

        folium.CircleMarker(
            location=(r['latitude'], r['longitude']),
            radius=raio,
            weight=1,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.75,
            tooltip=f"{r['subprefeitura']} | Total: {tot_fmt} | Unidades: {r['qtd_unidades']}",
            popup=folium.Popup(
                f"<b>{r['subprefeitura']}</b><br>"
                f"Total retirado: {tot_fmt}<br>"
                f"Nº de unidades: {r['qtd_unidades']}",
                max_width=320
            )
        ).add_to(m)

    legend_html = """
    <div style="position: fixed; bottom: 20px; left: 20px; z-index: 9999;
                background: white; padding: 10px 12px; border-radius: 8px;
                box-shadow: 0 2px 6px rgba(0,0,0,.2); font-size: 12px;">
      <b>Mapa por Subprefeitura</b><br>
      Cores e tamanhos proporcionais ao total de retiradas.<br>
      Passe o mouse para ver detalhes.
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save(SAIDA_MAPA)
    print(f"✔ CSV agregado salvo em: {SAIDA_AGREGADO}")
    print(f"✔ Mapa salvo em: {SAIDA_MAPA}")


# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    df_unidades = carregar_unidades(CSV_UNIDADES)
    print(f"[INFO] Unidades carregadas: {len(df_unidades)}")

    df_sub = montar_df_subprefeituras()
    print(f"[INFO] Subprefeituras carregadas: {len(df_sub)} (coords fixas)")

    df_join = vincular_por_proximidade(df_unidades, df_sub)
    gerar_mapa_e_csv(df_join, df_sub)
