param (
    [string]$podName        # El nombre del pod que se pasa como parámetro
)

# Verificar si el parámetro se ha pasado correctamente
if (-not $podName) {
    Write-Host "❌ Error: Debes proporcionar el nombre del pod como parámetro." -ForegroundColor Red
    exit
}

# Mostrar el progreso de lo que está haciendo el script
Write-Host "🚀 Conectando al pod '$podName' y ejecutando los comandos..." -ForegroundColor Cyan

# Comando para conectarse a la base de datos PostgreSQL y ejecutar los SQL
$psqlCommand = @"
psql -U dbuser -d app_db_prod -c 'CREATE TABLE prueba ();'
psql -U dbuser -d app_db_prod -c '\dt'
"@

# Ejecutar el comando kubectl exec para conectarse al pod y ejecutar los comandos dentro del contenedor
kubectl exec -it $podName -- /bin/bash -c $psqlCommand

Write-Host "✅ Comandos ejecutados con éxito en el pod '$podName'." -ForegroundColor Green
