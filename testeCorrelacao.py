import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import unidecode
from scipy.stats import pearsonr  # <--- NOVO

# ==========================
# 1. Carregar dados
# ==========================
idh = pd.read_csv(
    "data/idh_subprefeituras.csv",
    encoding="latin1",
    sep=","
)

med = pd.read_csv(
    "data/total_retirado_por_subprefeitura.csv",
    encoding="utf-8",
    sep=","
)

# ==========================
# 2. Normalizar nomes para fazer o merge
# ==========================
def normalize(text):
    return unidecode.unidecode(str(text).upper().strip())

idh["Subprefeitura_norm"] = idh["Subprefeitura"].apply(normalize)
med["Subprefeitura_norm"] = med["subprefeitura"].apply(normalize)

df = pd.merge(idh, med, on="Subprefeitura_norm", how="inner")

print("\n🔎 Primeiras linhas do DataFrame unificado:\n")
print(df.head())

# ==========================
# 3. Criar métricas derivadas
# ==========================
df["retirado_por_unidade"] = df["total_retirado_subpref"] / df["qtd_unidades"]

# ==========================
# 4. Correlações simples
# ==========================
print("\n📌 Correlações simples (Pearson):\n")
print("IDH_2010 x total_retirado_subpref:",
      df["IDH_2010"].corr(df["total_retirado_subpref"]))
print("IDH_2010 x retirado_por_unidade:",
      df["IDH_2010"].corr(df["retirado_por_unidade"]))
print("qtd_unidades x total_retirado_subpref:",
      df["qtd_unidades"].corr(df["total_retirado_subpref"]))
print("IDH_2010 x qtd_unidades:",
      df["IDH_2010"].corr(df["qtd_unidades"]))

# Também com p-valor via scipy (para usar nos gráficos)
r_idh_total, p_idh_total = pearsonr(df["IDH_2010"], df["total_retirado_subpref"])
r_idh_perun, p_idh_perun = pearsonr(df["IDH_2010"], df["retirado_por_unidade"])
r_idh_qtd, p_idh_qtd = pearsonr(df["IDH_2010"], df["qtd_unidades"])

# ==========================
# 5. Regressão 1 – TOTAL ~ IDH_2010 + qtd_unidades
# ==========================
X1 = df[["IDH_2010", "qtd_unidades"]]
y_total = df["total_retirado_subpref"]

X1 = sm.add_constant(X1)
model1 = sm.OLS(y_total, X1).fit()

print("\n📊 Regressão 1 — Total retirado ~ IDH_2010 + qtd_unidades\n")
print(model1.summary())

# ==========================
# 6. Regressão 2 – retirado_por_unidade ~ IDH_2010
# ==========================
X2 = df[["IDH_2010"]]
y_per_unid = df["retirado_por_unidade"]

X2 = sm.add_constant(X2)
model2 = sm.OLS(y_per_unid, X2).fit()

print("\n📊 Regressão 2 — Retirado por unidade ~ IDH_2010\n")
print(model2.summary())

# Função auxiliar para escrever caixinha com estatísticas no gráfico
def add_stats_box(ax, title, r, p, n):
    textstr = (
        f"{title}\n"
        f"r = {r:.2f}\n"
        f"R² ≈ {r**2:.2f}\n"
        f"p = {p:.3g}\n"
        f"N = {n}"
    )
    ax.text(
        0.02, 0.98, textstr,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment='top',
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8)
    )

N = len(df)

# ==========================
# 7. Gráfico 1 – IDH x Total de medicamentos
# ==========================
plt.figure(figsize=(10, 6))
ax = sns.regplot(data=df, x="IDH_2010", y="total_retirado_subpref")
plt.title("IDH 2010 x Total de Medicamentos Retirados")
plt.xlabel("IDH 2010")
plt.ylabel("Total de Medicamentos Retirados")
plt.grid(True, alpha=0.3)

# adicionar estatísticas no gráfico
add_stats_box(ax, "Correlação IDH x Total", r_idh_total, p_idh_total, N)

plt.tight_layout()
plt.show()
plt.close()

# ==========================
# 8. Gráfico 2 – IDH x Retirado por unidade
# ==========================
plt.figure(figsize=(10, 6))
ax = sns.regplot(data=df, x="IDH_2010", y="retirado_por_unidade")
plt.title("IDH 2010 x Retirada de Medicamentos por Unidade")
plt.xlabel("IDH 2010")
plt.ylabel("Medicamentos Retirados por Unidade")
plt.grid(True, alpha=0.3)

add_stats_box(ax, "Correlação IDH x Retirado/unidade", r_idh_perun, p_idh_perun, N)

plt.tight_layout()
plt.show()
plt.close()

# ==========================
# 9. Gráfico 3 – Bolhas (tamanho = nº de unidades)
# ==========================
plt.figure(figsize=(10, 6))

max_unid = df["qtd_unidades"].max()
sizes = 50 + 450 * (df["qtd_unidades"] / max_unid)

plt.scatter(
    df["IDH_2010"],
    df["total_retirado_subpref"],
    s=sizes,
    alpha=0.7
)

plt.title("IDH 2010 x Total de Medicamentos (tamanho da bolha = nº de unidades)")
plt.xlabel("IDH 2010")
plt.ylabel("Total de Medicamentos Retirados")
plt.grid(True, alpha=0.3)

# aqui usamos a mesma correlação IDH x Total (r_idh_total)
ax = plt.gca()
add_stats_box(ax, "IDH x Total (bolhas)", r_idh_total, p_idh_total, N)

plt.tight_layout()
plt.show()
plt.close()

# ==========================
# 10. Gráfico 4 – IDH x Número de unidades
# ==========================
plt.figure(figsize=(10, 6))
ax = sns.regplot(data=df, x="IDH_2010", y="qtd_unidades")
plt.title("IDH 2010 x Número de Unidades de Saúde")
plt.xlabel("IDH 2010")
plt.ylabel("Quantidade de Unidades")
plt.grid(True, alpha=0.3)

add_stats_box(ax, "Correlação IDH x Nº de unidades", r_idh_qtd, p_idh_qtd, N)

plt.tight_layout()
plt.show()
plt.close()
