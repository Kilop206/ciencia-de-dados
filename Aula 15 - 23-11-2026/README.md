# Aula 15 — Manutenção Preditiva e Telemetria Industrial

Documentação técnica dos artefatos em `Aula 15 - 23-11-2026`, baseada no código, notebooks, modelos, CSVs, banco SQLite e no desafio prático em PDF.

## Visão geral

O projeto demonstra um fluxo de manutenção preditiva: dados de sensores industriais alimentam dois modelos scikit-learn; um simulador grava telemetria continuamente em SQLite; e um painel Streamlit consulta as leituras recentes, calcula previsões e exibe KPIs, alertas, gráficos e tabela.

```text
CSV histórico → preparação (notebook) → treino e métricas → modelos .pkl
                                                            ↓
simulator.py → telemetria_fabril.db → app.py (Streamlit) → painel
```

## Componentes

| Arquivo | Papel |
|---|---|
| `app.py` | Painel Streamlit, carregamento dos modelos, consulta SQLite, inferência e visualizações Plotly. |
| `simulator.py` | Gera leituras sintéticas para cinco máquinas e as insere a cada 2 segundos no banco. |
| `preprocessing.ipynb` | Exploração e limpeza do CSV original: duplicatas, valores ausentes e limites inválidos. |
| `train_models.ipynb` | Treina e avalia regressão linear para energia e Random Forest para status de falha; salva os modelos. |
| `telemetria_parque_fabril_5000.csv` | Base bruta de 5.000 registros. |
| `dados_fabrica_limpos.csv` | Base preparada de 5.000 registros e 12 colunas usada no treino. |
| `telemetria_fabril.db` | Banco SQLite com tabela `leituras_sensores`; o arquivo versionado contém 600 leituras iniciais. |
| `modelo_regressao_energia.pkl` | Modelo LinearRegression para estimar `consumo_energia_kwh`. |
| `modelo_arvore_falha.pkl` | RandomForestRegressor para estimar o rótulo binário `status_falha`. |
| `Desafio Prático de Manutenção Preditiva 23-11-2026.pdf` | Enunciado acadêmico do desafio associado. |

## Arquitetura técnica

### Dados e atributos

A base tem 5.000 linhas e inclui identificador e timestamp, máquina, turno, cinco medições operacionais, consumo de energia, desgaste de ferramenta e rótulo `status_falha`. A distribuição observada do alvo é 4.441 registros normais (0) e 559 com falha (1), aproximadamente 11,18% positivos.

Os dois modelos usam as mesmas cinco entradas, nesta ordem:

1. `temperatura_operacao_c` — °C
2. `vibracao_mms` — mm/s
3. `corrente_eletrica_a` — A
4. `rotacao_rpm` — RPM
5. `pressao_hidraulica_bar` — bar

O pré-processamento do notebook substitui nulos e valores fora de limites definidos pela mediana e remove duplicatas por `id_registro`. O pipeline do notebook usa `train_test_split(test_size=0.2, random_state=42)`, portanto a avaliação reportada é em uma partição de teste de 20%.

### Modelos e métricas registradas

| Tarefa | Estimador | Métricas no notebook |
|---|---|---|
| Previsão de consumo de energia | `LinearRegression` | R² = **0,8327** (83,27%); MAE = **1,7447 kWh** |
| Classificação operacional de falha | `RandomForestRegressor(random_state=42)`, arredondado para 0/1 | Acurácia = **0,9670** (96,70%); F1 = **0,8290** |

Matriz de confusão gravada no notebook, com linhas = classe real e colunas = classe prevista:

```text
             previsto 0   previsto 1
real 0          887           3
real 1           30          80
```

A acurácia alta deve ser lida junto ao F1 e à matriz: há desbalanceamento no alvo e 30 falsos negativos nessa avaliação. O notebook implementa um regressor para o rótulo binário e arredonda suas saídas; para uma aplicação operacional, a avaliação deve incluir validação independente, métricas por classe e revisão do desenho do modelo antes de uso em decisões reais.

### Painel e atualização

- `app.py` abre o banco em modo somente leitura e seleciona até 300 registros mais recentes (padrão: 150).
- A inferência produz consumo previsto e status de falha; o alerta considera a última leitura de cada máquina.
- O painel permite filtrar máquina e ajustar atualização (1–10 s, padrão 2 s) e histórico (50–300).
- Exibe temperatura, vibração, corrente, consumo previsto, gráficos temporais de consumo/temperatura/vibração e tabela das leituras com previsões.
- O simulador grava leituras das cinco máquinas a cada 2 s; cada máquina tem 15% de chance por ciclo de receber um pico sintético de sobrecarga térmica/vibracional.
- O SQLite usa WAL para permitir leitura do painel e escrita do simulador em paralelo.

## Requisitos

Python 3.10+ recomendado. Dependências identificadas pelos imports dos arquivos:

```text
pandas
joblib
plotly
streamlit
scikit-learn
```

Os notebooks também usam `seaborn` e `matplotlib`. `sqlite3`, `time`, `pathlib`, `random` e `datetime` fazem parte da biblioteca padrão. Não há arquivo `requirements.txt` na pasta da aula.

## Execução local

Abra um terminal dentro de `Aula 15 - 23-11-2026`.

### 1. Criar ambiente e instalar dependências

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pandas joblib plotly streamlit scikit-learn seaborn matplotlib
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pandas joblib plotly streamlit scikit-learn seaborn matplotlib
```

### 2. Iniciar o simulador

Em um terminal, na pasta da aula:

```bash
python simulator.py
```

O simulador cria a tabela se necessário e acrescenta cinco leituras a cada dois segundos. Interrompa com `Ctrl+C`.

### 3. Iniciar o painel

Em outro terminal, também na pasta da aula:

```bash
streamlit run app.py
```

Abra o endereço local informado pelo Streamlit (normalmente `http://localhost:8501`). Para visualizar dados atualizados, mantenha o simulador rodando.

### 4. Regerar os modelos (opcional)

`train_models.ipynb` lê `dados_fabrica_limpos.csv` e salva os dois arquivos `.pkl` no diretório de trabalho atual. Abra e execute o notebook a partir da pasta da aula. O caminho absoluto gravado nas células do notebook aponta para outro computador; substitua a leitura por caminho relativo, por exemplo:

```python
from pathlib import Path
BASE_DIR = Path.cwd()
df = pd.read_csv(BASE_DIR / "dados_fabrica_limpos.csv")
```

Também ajuste os caminhos absolutos do `preprocessing.ipynb` para ler `telemetria_parque_fabril_5000.csv` e salvar `dados_fabrica_limpos.csv` na pasta local. Os modelos `.pkl` já estão versionados, então não é necessário treinar para abrir o painel.

## Esquema SQLite

Tabela `leituras_sensores`:

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | INTEGER PK | Sequência automática |
| `timestamp` | TEXT | Data e hora da leitura |
| `id_maquina` | TEXT | Identificador do equipamento |
| `turno` | TEXT | Manhã, Tarde ou Noite |
| `temperatura_operacao_c` | REAL | Temperatura em °C |
| `vibracao_mms` | REAL | Vibração em mm/s |
| `corrente_eletrica_a` | REAL | Corrente em A |
| `rotacao_rpm` | REAL | Rotação em RPM |
| `pressao_hidraulica_bar` | REAL | Pressão em bar |

O simulador não grava `status_falha` nem consumo na tabela; esses valores exibidos pelo painel são inferências dos modelos.

## Limitações conhecidas

- A simulação é sintética e não valida comportamento em sensores ou equipamentos reais.
- O painel chama `time.sleep()` e `st.rerun()` no fim de cada execução; o intervalo do slider controla a frequência de atualização.
- A classe positiva é minoritária e os falsos negativos merecem atenção especial.
- O notebook contém caminhos absolutos de uma máquina específica; use caminhos relativos para reproduzir.
- A saída contínua e o comportamento do alerta não substituem inspeção técnica nem validação industrial.
- Os `.pkl` carregados via `joblib` devem ser tratados como artefatos confiáveis do repositório; não carregue pickles de origem desconhecida.

## Reprodutibilidade

As métricas desta documentação foram transcritas das saídas salvas em `train_models.ipynb`, não recalculadas durante a escrita. A matriz e os valores correspondem à execução registrada no próprio notebook. Mudanças nos dados, versões das bibliotecas, divisão treino/teste ou treinamento podem alterar os resultados.
