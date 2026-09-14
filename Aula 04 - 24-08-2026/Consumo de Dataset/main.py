import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

# Configuração de diretórios
DIRETORIO_BASE = Path(__file__).resolve().parent
ARQUIVO_DADOS = DIRETORIO_BASE / 'diamantes.csv'
PASTA_GRAFICOS = DIRETORIO_BASE / 'graficos'
PASTA_GRAFICOS.mkdir(exist_ok=True)

# Dicionários para tradução do conjunto de dados
MAPA_COLUNAS = {
    'carat': 'quilate',
    'cut': 'corte',
    'color': 'cor',
    'clarity': 'claridade',
    'depth': 'profundidade',
    'table': 'tabela',
    'price': 'preco',
    'x': 'x',
    'y': 'y',
    'z': 'z'
}

MAPA_CORTE = {
    'Fair': 'Razoável',
    'Good': 'Bom',
    'Very Good': 'Muito Bom',
    'Premium': 'Premium',
    'Ideal': 'Ideal'
}

# Verifica se o arquivo existe e se possui conteúdo
if not ARQUIVO_DADOS.exists() or ARQUIVO_DADOS.stat().st_size == 0:
    print(f"O arquivo '{ARQUIVO_DADOS.name}' está ausente ou vazio. Baixando dados via Seaborn...")
    df_temp = sns.load_dataset('diamonds')
    df_temp = df_temp.rename(columns=MAPA_COLUNAS)
    df_temp['corte'] = df_temp['corte'].map(MAPA_CORTE).fillna(df_temp['corte'])
    df_temp.to_csv(ARQUIVO_DADOS, index=False)

sns.set_theme(style='whitegrid', font_scale=1.0)
df = pd.read_csv(ARQUIVO_DADOS)

# Estrutura da base de dados
print('Dimensões:', df.shape)
print('\nTipos de dados:\n', df.dtypes)
print('\nValores ausentes:\n', df.isna().sum())
print('\nPrimeiras linhas:\n', df.head())

numericas = ['quilate', 'profundidade', 'tabela', 'preco', 'x', 'y', 'z']
print('\nEstatística descritiva:\n', df[numericas].describe().round(2))

# 1. Histograma do preço
plt.figure(figsize=(10, 6))
sns.histplot(data=df, x='preco', bins=50, kde=True, color='C0')
plt.title('Distribuição dos preços dos diamantes')
plt.xlabel('Preço (US$)')
plt.ylabel('Frequência')
plt.tight_layout()
plt.savefig(PASTA_GRAFICOS / '01_histograma_preco.png', dpi=180)
plt.close()

# 2. Boxplot do preço
plt.figure(figsize=(10, 4))
sns.boxplot(data=df, x='preco', color='C0')
plt.title('Boxplot do preço')
plt.xlabel('Preço (US$)')
plt.tight_layout()
plt.savefig(PASTA_GRAFICOS / '02_boxplot_preco.png', dpi=180)
plt.close()

# 3. Boxplot por qualidade de corte
ordem_corte = ['Razoável', 'Bom', 'Muito Bom', 'Premium', 'Ideal']
plt.figure(figsize=(10, 5))
sns.boxplot(data=df, x='corte', y='preco', order=ordem_corte, color='C0')
plt.title('Preço por qualidade de corte')
plt.xlabel('Corte')
plt.ylabel('Preço (US$)')
plt.tight_layout()
plt.savefig(PASTA_GRAFICOS / '03_boxplot_corte.png', dpi=180)
plt.close()

# 4. Gráfico de dispersão (quilate x preço)
amostra = df.sample(7000, random_state=42)
plt.figure(figsize=(10, 6))
plt.scatter(amostra['quilate'], amostra['preco'], alpha=0.25, s=10)
plt.title('Relação entre peso (quilate) e preço')
plt.xlabel('Peso (quilate)')
plt.ylabel('Preço (US$)')
plt.tight_layout()
plt.savefig(PASTA_GRAFICOS / '04_dispersao_quilate_preco.png', dpi=180)
plt.close()

# 5. Mapa de calor de correlação
correlacao = df[numericas].corr()
plt.figure(figsize=(9, 7))
sns.heatmap(correlacao, annot=True, fmt='.2f', square=True)
plt.title('Mapa de calor — correlação entre variáveis numéricas')
plt.tight_layout()
plt.savefig(PASTA_GRAFICOS / '05_heatmap_correlacao.png', dpi=180)
plt.close()

# 6. Preço médio por corte (apoio visual)
medias = df.groupby('corte')['preco'].mean().reindex(ordem_corte)
plt.figure(figsize=(9, 5))
medias.plot(kind='bar')
plt.title('Preço médio por corte')
plt.xlabel('Corte')
plt.ylabel('Preço médio (US$)')
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(PASTA_GRAFICOS / '06_preco_medio_corte.png', dpi=180)
plt.close()
