# Diagnostico do Kafka do Grupo 3 - executar na pasta do projeto.
$ErrorActionPreference = 'Continue'
Write-Host "=== Estado Kafka ==="
docker compose ps kafka
Write-Host "=== Logs Kafka (ultimas 150 linhas) ==="
docker compose logs kafka --tail=150
Write-Host "=== Ultimos resultados de healthcheck ==="
docker inspect iiot-grupo3-kafka-1 --format '{{json .State.Health.Log}}'
Write-Host "=== Estado de todos os servicos ==="
docker compose ps
