import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
from pathlib import Path

ARQUIVO_CSV = 'data/retiradas_unidades_coords.csv'
CENTRO_MAPA = (-23.5504533, -46.6339112)  # São Paulo
ZOOM_INICIAL = 11
SAIDA_HTML = 'mapa_retiradas_heatmap.html'

if not Path(ARQUIVO_CSV).exists():
    raise FileNotFoundError(f"Arquivo não encontrado: {ARQUIVO_CSV}")

with open(ARQUIVO_CSV, 'r', encoding='utf-8') as f:
    primeira = f.readline()
sep = ';' if ';' in primeira else ','

df = pd.read_csv(ARQUIVO_CSV, sep=sep, encoding='utf-8')
df.columns = df.columns.str.strip().str.lower()


possiveis = {
    'id_unidade': ['id_unidade', 'id', 'unidade_id'],
    'nome': ['nome', 'descricao', 'unidade', 'ubs_upa', 'razao_social'],
    'latitude': ['latitude', 'lat'],
    'longitude': ['longitude', 'lon', 'long'],
    'total_retirado': ['total_retirado', 'total', 'retirado', 'qtd_retirada']
}
mapa_cols = {}
for alvo, candidatos in possiveis.items():
    for c in candidatos:
        if c in df.columns:
            mapa_cols[alvo] = c
            break

obrig = ['latitude', 'longitude', 'total_retirado', 'nome']
faltando = [c for c in obrig if c not in mapa_cols]
if faltando:
    raise KeyError(f"Colunas obrigatórias ausentes no CSV: {faltando}\n"
                   f"Colunas encontradas: {df.columns.tolist()}")

# Renomeia para padrão interno
df = df.rename(columns={mapa_cols[k]: k for k in mapa_cols})

for col in ['latitude', 'longitude', 'total_retirado']:
    df[col] = (df[col].astype(str).str.replace(',', '.', regex=False))

df = df.dropna(subset=['latitude', 'longitude', 'total_retirado'])
df['latitude'] = df['latitude'].astype(float)
df['longitude'] = df['longitude'].astype(float)
df['total_retirado'] = df['total_retirado'].astype(float)


df = df[(df['latitude'].between(-34, 6)) & (df['longitude'].between(-74, -28))]

p99 = df['total_retirado'].quantile(0.99)
p99 = p99 if p99 > 0 else (df['total_retirado'].max() or 1.0)

df['peso'] = np.log1p(df['total_retirado']) / np.log1p(p99)
df['peso'] = df['peso'].clip(0, 1)

print(f"[INFO] p99 = {p99:,.0f} | pesos normalizados (log1p) em [0,1]")
m = folium.Map(location=CENTRO_MAPA, zoom_start=ZOOM_INICIAL, tiles='OpenStreetMap')

points = df[['latitude', 'longitude', 'peso']].values.tolist()
HeatMap(points, radius=14, blur=20, max_zoom=13).add_to(m)


media_total = df['total_retirado'].mean()
df_top = df[df['total_retirado'] >= media_total]

for _, r in df_top.iterrows():
    total_fmt = f"{int(r['total_retirado']):,}".replace(",", ".")
    folium.CircleMarker(
        location=(r['latitude'], r['longitude']),
        radius=1.2,          # bem pequeno
        weight=0,
        fill=True,
        fill_opacity=0.25,   # bem transparente
        color="#1a73e8",     # azul suave
        tooltip=f"{r['nome']}<br>Total retirado: {total_fmt}"
    ).add_to(m)

legend_html = f"""
<div style="
     position: fixed; 
     bottom: 20px; left: 20px; z-index: 9999; 
     background: white; padding: 10px 12px; border-radius: 8px;
     box-shadow: 0 2px 6px rgba(0,0,0,.2); font-size: 12px;">
  <b>Intensidade (heatmap)</b><br>
  Escala logarítmica até p99 = {int(p99):,}.<br>
  Pontos azuis = unidades com retirada ≥ média.
</div>
""".replace(",", ".")
m.get_root().html.add_child(folium.Element(legend_html))


m.save(SAIDA_HTML)
print(f"✅ Mapa gerado: {SAIDA_HTML}")
