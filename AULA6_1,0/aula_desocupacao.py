# %% [markdown]
# # Desocupação por sexo (2012 × 2026) e horas de cuidados (2022)
# Instale antes, no terminal:
#
# `python -m pip install pandas matplotlib seaborn xlrd`

# %%
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# %% [markdown]
# ## 1. Abrir as duas Tabelas 5
# - `sep=";"` e `decimal=","` → padrão brasileiro
# - `encoding="utf-8-sig"` → remove o BOM do início do arquivo (senão a 1ª coluna vira "﻿Sigla")

# %%
t2012 = pd.read_csv("Tabela5-sem_emprego_2012.csv", sep=";", decimal=",", encoding="utf-8-sig")
t2026 = pd.read_csv("Tabela5-sem_emprego_2026.csv", sep=";", decimal=",", encoding="utf-8-sig")

# nomes curtos para as colunas de valores
t2012 = t2012.rename(columns={
    "Desocupados - homens (2012 T1)": "homens_2012",
    "Desocupados - mulheres (2012 T1)": "mulheres_2012",
})
t2026 = t2026.rename(columns={
    "Desocupados - homens (2026 T1)": "homens_2026",
    "Desocupados - mulheres (2026 T1)": "mulheres_2026",
})
t2012.head()

# %% [markdown]
# ## 2. Juntar as duas tabelas (merge)

# %%
comp = t2012.merge(t2026, on=["Sigla", "Código", "Estado"], how="inner")
comp["variacao_mulheres"] = comp["mulheres_2026"] - comp["mulheres_2012"]
print(comp.shape)
comp.head()

# %% [markdown]
# ## 3. Comparar ano a ano

# %%
print("Média simples dos 27 estados (mulheres entre os desocupados):")
print(f"  2012 T1: {comp['mulheres_2012'].mean():.1f}%")
print(f"  2026 T1: {comp['mulheres_2026'].mean():.1f}%")

print("\nMaiores altas da participação feminina:")
print(comp.sort_values("variacao_mulheres", ascending=False)[["Estado", "mulheres_2012", "mulheres_2026", "variacao_mulheres"]].head())

print("\nMaiores quedas:")
print(comp.sort_values("variacao_mulheres")[["Estado", "mulheres_2012", "mulheres_2026", "variacao_mulheres"]].head())

# %% [markdown]
# ## 4. Gráfico usando o merge (formato longo + seaborn)

# %%
ordem = comp.sort_values("mulheres_2026", ascending=False)["Estado"]

longo = comp.melt(
    id_vars=["Sigla", "Código", "Estado"],
    value_vars=["mulheres_2012", "mulheres_2026"],
    var_name="Ano",
    value_name="Participacao_mulheres",
)
longo["Ano"] = longo["Ano"].map({"mulheres_2012": "2012 T1", "mulheres_2026": "2026 T1"})

fig, ax = plt.subplots(figsize=(10, 10))
sns.barplot(
    data=longo,
    y="Estado",
    x="Participacao_mulheres",
    hue="Ano",
    order=ordem,
    ax=ax,
)
ax.axvline(50, color="red", linestyle="--", linewidth=1)
ax.set_xlabel("Participação das mulheres entre as pessoas desocupadas (%)")
ax.set_ylabel("")
ax.set_title("Desocupação: participação feminina em 2012 T1 e 2026 T1")
ax.legend(title="Trimestre")
fig.tight_layout()
plt.savefig("desocupacao_mulheres.png", dpi=120)
plt.show()

# %% [markdown]
# ## 5. Tabela 1.1.1 — horas semanais de cuidados e afazeres domésticos (2022)
# A planilha tem título, cabeçalho em 3 linhas e notas no rodapé.
# Lemos sem cabeçalho, pegamos só o bloco de dados e damos nomes às colunas.
# Obs.: a tabela não tem total por sexo, só **sexo × cor ou raça**.

# %%
bruta = pd.read_excel("Tabela_1.1.1.xls", sheet_name="2022", header=None)

cuidados = bruta.iloc[8:41, :8].copy()   # linhas de "Brasil" até "Distrito Federal"
cuidados.columns = [
    "Estado", "horas_total",
    "total_branca", "total_preta_parda",
    "homem_branca", "homem_preta_parda",
    "mulher_branca", "mulher_preta_parda",
]

# %% [markdown]
# ### Ficar só com os estados
# A coluna mistura Brasil, regiões e UFs. Mantemos apenas os nomes que existem na Tabela 5.

# %%
cuidados = cuidados[cuidados["Estado"].isin(comp["Estado"])].reset_index(drop=True)

colunas_horas = cuidados.columns.drop("Estado")
cuidados[colunas_horas] = cuidados[colunas_horas].apply(pd.to_numeric).round(1)

# diferença mulher − homem (em horas por semana), por cor ou raça
cuidados["dif_branca"] = cuidados["mulher_branca"] - cuidados["homem_branca"]
cuidados["dif_preta_parda"] = cuidados["mulher_preta_parda"] - cuidados["homem_preta_parda"]

print(len(cuidados), "estados")
cuidados.head()

# %% [markdown]
# ## 6. Cruzar desocupação com horas de cuidados

# %%
cruzada = comp.merge(cuidados, on="Estado", how="inner")
print(cruzada.shape)

print(cruzada[["mulheres_2026", "horas_total", "mulher_preta_parda", "dif_preta_parda"]].corr().round(2))

# %%
fig, ax = plt.subplots(figsize=(10, 7))
sns.regplot(
    data=cruzada,
    x="mulher_preta_parda",
    y="mulheres_2026",
    ax=ax,
    scatter_kws={"s": 40},
    line_kws={"color": "red", "linewidth": 1},
)
for _, linha in cruzada.iterrows():
    ax.annotate(linha["Sigla"], (linha["mulher_preta_parda"], linha["mulheres_2026"]),
                xytext=(4, 3), textcoords="offset points", fontsize=8)

ax.set_xlabel("Horas semanais em cuidados e afazeres — mulheres pretas ou pardas (2022)")
ax.set_ylabel("Participação das mulheres entre os desocupados (%) — 2026 T1")
ax.set_title("Horas de cuidados × participação feminina na desocupação")
fig.tight_layout()
plt.savefig("cuidados_x_desocupacao.png", dpi=120)
plt.show()
