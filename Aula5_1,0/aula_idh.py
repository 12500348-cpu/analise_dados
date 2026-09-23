# %% [markdown]
# # IDHM por Unidade da Federação — Tabela4.csv
# Abrir o CSV, limpar, responder perguntas e plotar com matplotlib.

# %%
import pandas as pd
import matplotlib.pyplot as plt

# %% [markdown]
# ## 1. Abrir um CSV com `;` e vírgula decimal
# - `sep=";"` → separador de colunas
# - `decimal=","` → converte "0,402" em 0.402
# - `skiprows=1` → a 1ª linha é só o título da tabela
# - `encoding="latin-1"` → o arquivo tem acentos no padrão do Excel/Windows

# %%
df = pd.read_csv("Tabela4.csv", sep=";", decimal=",", skiprows=1, encoding="latin-1")
df.head()

# %% [markdown]
# ## 2. Limpar colunas e linhas vazias

# %%
df = df.dropna(axis=1, how="all")   # remove colunas totalmente vazias
df = df.dropna(axis=0, how="all")   # remove linhas totalmente vazias
df.columns = df.columns.str.strip() # tira espaços dos nomes das colunas
print(df.shape)
df.info()

# %% [markdown]
# ## 3. Ordenar os estados por maior IDH em 2024

# %%
ranking_2024 = df.sort_values("2024", ascending=False)[["Sigla", "Estado", "2024"]]
ranking_2024.reset_index(drop=True, inplace=True)
ranking_2024.index += 1   # posição começando em 1
print(ranking_2024)

# %% [markdown]
# ## 4. Qual estado teve a maior melhora de IDH entre 1991 e 2024?

# %%
df["Melhora"] = df["2024"] - df["1991"]
melhora = df.sort_values("Melhora", ascending=False)[["Sigla", "Estado", "1991", "2024", "Melhora"]]
print(melhora.head())

maior = melhora.iloc[0]
print(f"\nMaior melhora: {maior['Estado']} (+{maior['Melhora']:.3f}, de {maior['1991']} para {maior['2024']})")

# %% [markdown]
# ## 5. Existe algum estado em que o IDH piorou?
# Comparando 2024 com 1991, e também de um ano para o seguinte.

# %%
pioraram = df[df["Melhora"] < 0]
print("Estados com IDH menor em 2024 do que em 1991:", len(pioraram))

# Quedas ano a ano (ex.: pandemia em 2020–2021)
anos = [c for c in df.columns if str(c).isdigit()]
variacao = df.set_index("Sigla")[anos].diff(axis=1)
quedas_2021 = variacao["2021"][variacao["2021"] < 0]
print(f"Estados com queda de 2020 para 2021: {len(quedas_2021)} de {len(df)}")

# 2023 → 2024
queda_24 = variacao["2024"][variacao["2024"] < 0]
print("Queda de 2023 para 2024:", queda_24.round(3).to_dict())

df = df.drop(columns="Melhora")   # volta a tabela ao formato original

# %% [markdown]
# ## 6. Formato largo → formato longo (`melt`)

# %%
anos = [c for c in df.columns if str(c).isdigit()]
print(anos)

id_vars = [c for c in df.columns if c not in anos]
df_longo = df.melt(
    id_vars=id_vars,
    value_vars=anos,
    var_name="Ano",
    value_name="IDH",
)
df_longo["Ano"] = df_longo["Ano"].astype(int)
df_longo["IDH"] = pd.to_numeric(df_longo["IDH"], errors="coerce")
df_longo.head()

# %% [markdown]
# ## 7. Plotar apenas Minas Gerais

# %%
mg = df_longo[df_longo["Sigla"] == "MG"].sort_values("Ano")

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(mg["Ano"], mg["IDH"], marker="o", linewidth=2, color="tab:blue")
ax.set_title("Evolução do IDH — Minas Gerais (1991–2024)")
ax.set_xlabel("Ano")
ax.set_ylabel("IDH")
ax.grid(alpha=0.3)
fig.tight_layout()
plt.savefig("idh_mg.png", dpi=120)
plt.show()

# %% [markdown]
# ## 8. Evolução do IDH de cada estado

# %%
fig, ax = plt.subplots(figsize=(12, 7))

for sigla, grupo in df_longo.groupby("Sigla"):
    grupo = grupo.sort_values("Ano")
    ax.plot(grupo["Ano"], grupo["IDH"], marker="o", markersize=3, linewidth=1.5, label=sigla)

ax.set_title("Evolução do IDH por estado (1991–2024)")
ax.set_xlabel("Ano")
ax.set_ylabel("IDH")
ax.set_ylim(0.3, 0.9)
ax.legend(ncol=3, bbox_to_anchor=(1.02, 1), loc="upper left", title="UF")
fig.tight_layout()
plt.savefig("idh_estados.png", dpi=120)
plt.show()
