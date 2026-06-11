#Faz o upload da base de dados para análise.
from google.colab import files
import zipfile
import json
import pandas as pd
from pathlib import Path

# Upload do arquivo ZIP
uploaded = files.upload()

zip_name = list(uploaded.keys())[0]

# Extrair
with zipfile.ZipFile(zip_name, 'r') as zip_ref:
    zip_ref.extractall("spotify_data")

print("Arquivos extraídos.")

#Localiza os arquivos de históricos contidos no zip.
from pathlib import Path

base = Path("spotify_data")

json_files = list(base.rglob("*.json"))

print(f"Encontrados {len(json_files)} arquivos JSON")

#Carrega todos os registros.
dados = []

for arquivo in json_files:
    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            conteudo = json.load(f)

            if isinstance(conteudo, list):
                dados.extend(conteudo)

    except Exception as e:
        print(f"Erro em {arquivo}: {e}")

df = pd.DataFrame(dados)

print(df.shape)
df.head()

#Mostra as colunas disponíveis.
print(df.columns.tolist())

#Filtra a busca para exibir os podcasts.
podcasts = df[
    df["spotify_episode_uri"].notna()
].copy()

print(f"Episódios encontrados: {len(podcasts)}")

#Como é um arquivo pessoal, removi os resultados do canal SleepTube.
podcasts = podcasts[
    ~podcasts["episode_show_name"]
        .str.contains("SleepTube", case=False, na=False)
]

#Lista todos os podcasts ouvidos.
lista_podcasts = (
    podcasts["episode_show_name"]
    .dropna()
    .sort_values()
    .unique()
)

for podcast in lista_podcasts:
    print(podcast)

#Tempo ouvido por podcast.
tempo_podcast = (
    podcasts
    .groupby("episode_show_name")["ms_played"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

tempo_podcast["horas"] = (
    tempo_podcast["ms_played"]
    / 1000
    / 60
    / 60
)

tempo_podcast.head(20)

#Podcasts mais ouvidos
import matplotlib.pyplot as plt

top10 = tempo_podcast.head(10)

plt.figure(figsize=(10,6))
plt.barh(
    top10["episode_show_name"],
    top10["horas"]
)
plt.xlabel("Horas")
plt.ylabel("Podcast")
plt.title("Podcasts mais ouvidos")
plt.gca().invert_yaxis()
plt.show()

#Episódios mais ouvidos.
episodios_top = (
    podcasts
    .groupby(
        ["episode_show_name", "episode_name"]
    )["ms_played"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

episodios_top["horas"] = (
    episodios_top["ms_played"]
    / 1000
    / 60
    / 60
)

episodios_top.head(20)

#Implementa o NLP para analisar os interesses.
from collections import Counter
import re

texto = " ".join(
    podcasts["episode_name"]
    .dropna()
    .astype(str)
)

palavras = re.findall(
    r"\b[a-zA-ZÀ-ÿ]{4,}\b",
    texto.lower()
)

stopwords = {
    "para","como","sobre",
    "podcast","episodio",
    "parte","mais","uma",
    "com","dos","das"
}

palavras = [
    p for p in palavras
    if p not in stopwords
]

contador = Counter(palavras)

contador.most_common(30)

