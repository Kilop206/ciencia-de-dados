# Grupo 3 — Streaming de Dados Industriais: API IIoT → Kafka → InfluxDB → Grafana

Projeto prático de **Engenharia de Pipelines de Dados em Tempo Real**, alinhado ao enunciado do trabalho (Grupo 3). O projeto é uma demonstração **simulada e local**, sem sensores reais nem conectividade industrial.

## 1. Stack e arquitetura

```text
[API REST simuladora de máquinas IIoT] -- GET /api/v1/telemetry --> [Publisher Python]
                                                               |
                                                         Kafka (topic)
                                                               |
                                                         [Consumer Python]
                                                               |
                                                       [Validação + ETL]
                                                         /           \
                                             válidos /               \ inválidos
                                        [InfluxDB 2]                  [Kafka DLQ]
                                              |
                                            [Grafana]
```

- **API HTTP IIoT:** FastAPI; publica leituras fictícias de três máquinas por GET.
- **Publisher:** Python `requests` + `confluent-kafka`; busca a API a cada segundo e publica eventos no Kafka.
- **Kafka:** Apache Kafka em modo KRaft de broker único; tópicos `iiot.raw.telemetry` e `iiot.invalid.telemetry` (DLQ).
- **Consumer:** Python `confluent-kafka` + `influxdb-client`; valida JSON, filtra dados inválidos, identifica leituras acima dos limiares, grava no InfluxDB 2.x e só então confirma o offset Kafka.
- **Persistência:** InfluxDB 2.7, bucket `industrial`, retenção padrão de bucket. Volume persistente Docker.
- **Observabilidade:** Grafana provisionado automaticamente com dashboard e fonte de dados Flux (temperatura, vibração, corrente, eventos aceitos, inválidos e anomalias).

**Por que uma API local?** É uma **API real (HTTP/JSON)** que emite dados **simulados de IIoT**. Mantém a apresentação reproduzível sem internet ou credenciais de API de terceiros. O publisher aceita outra API HTTP mediante alteração de `IIOT_API_URL`, desde que retorne `{ "events": [{...}] }` no contrato abaixo.

## 2. Requisitos

- Windows 11, Linux ou macOS, **Docker Engine + Docker Compose v2** funcionando (no Windows: Docker Desktop em modo Linux).
- Opcional: Python 3.10+ no host **somente** para executar `scripts/inject.py`, `scripts/validate_stack.py` e os testes (aplicações são executadas pelo Docker).
- Portas livres no host: `9092`, `8086`, `3000` e `8000`.
- 4 GB ou mais de RAM livre são recomendados para os contêineres durante a demo. Kafka usa JVM.

## 3. Primeiro início (PowerShell)

```powershell
Copy-Item .env.example .env
# Edite .env e altere as credenciais antes de executar em máquina compartilhada.
docker compose up -d --build
docker compose ps
docker compose logs --tail=50 kafka-init publisher consumer
py scripts/validate_stack.py
```

O **primeiro** `docker compose up` pode precisar baixar imagens e dependências Python. Aguarde a inicialização e confira `docker compose ps` / `logs` antes de iniciar a demonstração.

**Endereços:**

| Interface | Endereço | Observações |
|---|---|---|
| API IIoT / Swagger | http://localhost:8000/docs | Experimente GET `/api/v1/telemetry` |
| InfluxDB | http://localhost:8086 | Credenciais de `.env` |
| Grafana | http://localhost:3000 | Credenciais de `.env`; dashboard provisionado em **Dashboards → Industrial** |
| Dashboard direto | http://localhost:3000/d/industrial-grupo3/iiot-industrial-stream | Atualização automática de 5 segundos |
| Kafka externo | localhost:9092 | Para apps Python rodando **no host** |
| Kafka interno | kafka:29092 | Para contêineres na rede Compose |

**Importante:** `localhost` significa a **máquina em que o cliente está rodando**. Dentro do contêiner, `localhost:9092` não identifica o broker Kafka. Por isso o Compose possui dois listeners.

## 4. Demonstração prática

Abra Grafana e mantenha uma segunda janela com logs:

```powershell
docker compose logs -f publisher consumer
```

Execute cada cenário em um **novo terminal PowerShell** na raiz do projeto:

```powershell
py scripts/inject.py overheat    # Temperatura da MAQ-01 = 95 °C -> alerta
py scripts/inject.py vibration   # Vibração da MAQ-01 = 9,2 mm/s -> alerta
py scripts/inject.py invalid     # Temperatura em string -> rejeição/DLQ
py scripts/inject.py duplicate   # Repete última leitura (mesmo ID e timestamp)
```

A chamada `POST` enfileira o cenário e a **próxima leitura** do publisher o incorpora. Cenários não são valores de sensores reais. Alarme didático: temperatura >=80 °C, vibração >=6 mm/s ou corrente >=20 A. Esses limiares são apenas para demonstração, não critérios de segurança industrial.

Mostrar os tópicos e DLQ (Kafka CLI embutido no contêiner):

```powershell
docker compose exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:29092 --list
docker compose exec kafka /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server kafka:29092 --topic iiot.invalid.telemetry --from-beginning --max-messages 1
```

A segunda consulta **aguarda** uma mensagem inválida se ainda não existir; use `py scripts/inject.py invalid` em outro terminal.

### Demonstração da recuperação do consumer

```powershell
docker compose stop consumer
# Enquanto o consumer estiver parado, o publisher continuará publicando mensagens no Kafka.
docker compose start consumer
docker compose logs -f consumer
```

Opcionalmente, em Python no host (após instalar `requirements.txt`):

```powershell
py scripts/kafka_lag.py
```

Essa recuperação utiliza a retenção do Kafka e confirmação manual de offsets. **Não comprova alta disponibilidade**, pois há somente 1 broker Kafka e 1 InfluxDB. Um único broker **não resiste** à perda do broker.

## 5. Contrato de dados da API

`GET /api/v1/telemetry` retorna:

```json
{
  "source": "iiot-simulator",
  "events": [
    {
      "event_id": "UUID-v4-gerado-pela-API",
      "machine_id": "MAQ-01",
      "line_id": "linha-01",
      "timestamp": "2026-10-26T16:40:00+00:00",
      "temperature_c": 63.5,
      "vibration_mm_s": 2.4,
      "current_a": 11.2
    }
  ]
}
```

O ETL valida tipos, obrigatoriedade, intervalo plausível e timezone; acrescenta `alert` (0 ou 1), grava os valores na medição `iiot_telemetry` e o contador de resultados em `pipeline_events`. Mensagens inválidas não entram em `iiot_telemetry`; o payload original é enviado ao tópico DLQ.

O Grafana usa queries Flux apontando para o bucket `industrial`. Se alterar `INFLUXDB_BUCKET`, ajuste também `grafana/dashboards/industrial.json` (campos `from(bucket: "industrial")`).

### Semântica de entrega e duplicatas

O consumer só confirma o offset após a gravação no InfluxDB, usando `enable.auto.commit=false`. Em reinício, um evento pode ser **reprocessado**. No InfluxDB, gravar novamente a **mesma medição/tags/timestamp** substitui campos, o que reduz duplicação visível para esse cenário; isso **não** equivale a exatamente-uma-vez global. `event_id` é mantido no Kafka, mas evitamos indexá-lo como tag de alta cardinalidade no InfluxDB. O contador operacional `pipeline_events` pode contabilizar uma tentativa extra após falha parcial. É uma limitação didática assumida.

## 6. Testes (código sem serviços externos)

```powershell
py -m pip install -r requirements-dev.txt
py -m pytest -q
```

Testes verificam validade do JSON, limites dos sensores, alertas, contrato da API, cenários manuais e presença da configuração do Grafana. **Eles não substituem um teste de integração** com Docker/Kafka/InfluxDB. Para esse, inicie a stack e confira o Grafana, a DLQ e a recuperação do consumer.

## 7. Diagnóstico

```powershell
docker compose config
docker compose ps
docker compose logs --tail=100 kafka
docker compose logs --tail=100 influxdb
docker compose logs --tail=100 grafana
docker compose logs --tail=100 kafka-init
docker compose logs --tail=100 publisher consumer
```

- Kafka sem comunicação: verifique listeners. `kafka:29092` **dentro** do Docker, `localhost:9092` **no host**.
- InfluxDB recusando token: mudar `.env` **após o primeiro setup** não atualiza credenciais persistidas no volume. Recupere o token original ou recrie o volume conscientemente.
- Grafana sem dados: verifique logs do consumer, `INFLUXDB_TOKEN` e bucket. Escolha `Last 15 minutes` e confirme o datasource em **Connections → Data sources**.
- Se usar uma API externa, atualize `IIOT_API_URL` com URL acessível **a partir do contêiner**, mantenha contrato `events` e verifique o timeout HTTP.
- `docker compose down` remove os contêineres mas **preserva volumes**; `docker compose down -v` **apaga os dados** de Kafka, InfluxDB e Grafana — use só se quiser reiniciar do zero.


## Kafka apresenta `unhealthy` no primeiro inicio?

O Compose espera o healthcheck de Kafka antes de iniciar `kafka-init`. Uma falha nesse teste **nao identifica por si so** a causa.

Execute na pasta do projeto (PowerShell):

```powershell
docker compose ps kafka
docker compose logs kafka --tail=150
docker inspect iiot-grupo3-kafka-1 --format '{{json .State.Health.Log}}'
```

Nesta revisao, o healthcheck foi atualizado para consultar `localhost:29092` **dentro do broker**, usar `kafka-topics.sh --list` e conceder mais tempo de inicializacao (`start_period: 90s`). Isso reduz falsos negativos por inicializacao lenta, mas **nao corrige** problemas reais de configuracao, memoria ou volumes.

Aplique a atualizacao do healthcheck **sem apagar o volume do Kafka**:

```powershell
docker compose up -d --no-deps --force-recreate kafka
docker compose ps kafka
# Quando estiver healthy:
docker compose up -d --build
```

Se o Kafka mostrar erros de acesso negado a volume, conflito de cluster ID, OOM ou falha de KRaft, examine o log antes de tentar restaurar o servico. Um volume que pertence a outro cluster pode exigir migracao ou reset deliberado; **nao execute `docker compose down -v` como solucao generica**, pois ele apaga os dados de Kafka, InfluxDB e Grafana.

Para diagnostico rapido automatico, execute `powershell -ExecutionPolicy Bypass -File scripts/diagnosticar_kafka.ps1`.

## 8. Segurança e limites de uso

- **Somente laboratório local**: Kafka sem TLS/autenticação e credenciais de exemplo. As portas estão limitadas a `127.0.0.1` no host.
- Não use nomes/senhas fixas desse projeto em produção. Não comite `.env`.
- Não conectar o simulador à rede de produção / CLPs reais.
- Kafka com um só nó (replication factor=1) **não** é HA. Para um estudo de alta disponibilidade, compare conceitualmente clusters com múltiplos brokers/controladores e armazenamento redundante.

## 9. Fontes de documentação oficiais

- Apache Kafka Docker: https://kafka.apache.org/41/getting-started/docker/
- Confluent Python Kafka Client: https://docs.confluent.io/kafka-clients/python/current/overview.html
- InfluxDB 2 Docker: https://docs.influxdata.com/influxdb/v2/install/
- InfluxDB Python Client: https://docs.influxdata.com/influxdb/cloud/api-guide/client-libraries/python/
- Grafana Provisioning: https://grafana.com/docs/grafana/latest/administration/provisioning/
- Grafana InfluxDB Datasource: https://grafana.com/docs/grafana/latest/datasources/influxdb/

**Roteiro pronto:** `docs/roteiro_7_minutos.md`.


## Interface de inspeção do Kafka (Kafdrop)

O Compose inclui o **Kafdrop**, uma interface web para visualizar brokers,
tópicos, partições, mensagens, consumidores e lag do Kafka.

- Endereço: http://localhost:9000
- Comunicação interna com Kafka: `kafka:29092`
- Inicie somente a interface (com Kafka já saudável): `docker compose up -d kafdrop`
- Verifique o estado: `docker compose ps kafka kafdrop`
- Consulte logs: `docker compose logs -f kafdrop`

Como o Kafdrop depende de `kafka: condition: service_healthy`, ele só será
iniciado após o broker passar no healthcheck. Se Kafka estiver `unhealthy`,
resolva os problemas do serviço Kafka antes.

O Kafdrop é voltado à inspeção de eventos e consumidores do Kafka; o Grafana
continua sendo o painel de observabilidade dos dados armazenados no InfluxDB.
