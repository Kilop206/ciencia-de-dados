# Demonstração (7 minutos) — Grupo 3

**0:00–0:45 — Arquitetura**. Apresentar API IIoT → Publisher Python → Kafka → Consumer Python → InfluxDB → Grafana. Explicar que a API é simulada e os dados não vêm de uma máquina real.

**0:45–1:45 — API HTTP de sensores**. Acessar http://localhost:8000/docs e executar GET `/api/v1/telemetry`. Mostrar `event_id`, `machine_id`, `timestamp` e unidades.

**1:45–2:45 — Streaming no Kafka**. `docker compose logs -f publisher consumer`, observar eventos publicados e persistidos. Explicar topic, chave da máquina e particionamento.

**2:45–4:00 — Grafana**. Abrir http://localhost:3000/d/industrial-grupo3/iiot-industrial-stream. Mostrar a temperatura e vibração das três máquinas e a frequência de atualização.

**4:00–5:00 — Falha de processo**. `py scripts/inject.py overheat` e `py scripts/inject.py vibration`. Mostrar um pico e a contagem de anomalias. Não confundir evento de alerta com falha técnica da infraestrutura.

**5:00–6:00 — Validação de dados**. `py scripts/inject.py invalid`; ver no log do consumidor a mensagem inválida encaminhada à DLQ Kafka (`iiot.invalid.telemetry`). Mostre que a leitura inválida não entra na série de sensores.

**6:00–7:00 — Resiliência**. Opcional: `docker compose stop consumer`; esperar alguns segundos; `docker compose start consumer`; verificar que Kafka conservou os eventos e consumer retomou. Este é um exemplo de recuperação de serviço, **não** de HA: ainda há um só broker.

## Conferência antes da aula

1. `docker compose up -d --build`
2. `docker compose ps` (todos os serviços esperados em execução)
3. `py scripts/validate_stack.py`
4. Grafana carregado, intervalo 'Last 15 minutes', refresh 5s
5. Log do consumer sem erro
6. Salvar capturas reais do Grafana e logs para o relatório
