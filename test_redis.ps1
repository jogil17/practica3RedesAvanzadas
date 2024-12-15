param (
    [string]$podName  # Nombre del pod de Redis
)

# Validar que se ha proporcionado el nombre del pod
if (-not $podName) {
    Write-Host "Error: El nombre del pod es necesario." -ForegroundColor Red
    exit
}

# Comando para ejecutar redis-cli dentro del pod
$redisCommand = "redis-cli"

# Comprobar si redis-cli está disponible en el contenedor
$checkRedisCommand = kubectl exec -it $podName -- /bin/bash -c "command -v redis-cli"
if ($checkRedisCommand -eq "") {
    Write-Host "Error: redis-cli no está disponible en el contenedor." -ForegroundColor Red
    exit
}

# Conectar al pod y ejecutar los comandos Redis
Write-Host "Conectando a Redis en el pod $podName..." -ForegroundColor Cyan

# Conexión y prueba PING
$pingResult = kubectl exec -it $podName -- /bin/bash -c "$redisCommand PING"
if ($pingResult -eq "PONG") {
    Write-Host "Conexión a Redis exitosa en el pod $podName!" -ForegroundColor Green
} else {
    Write-Host "Error: No se pudo conectar a Redis. Resultado: $pingResult" -ForegroundColor Red
    exit
}

# Establecer un valor con SET
Write-Host "Estableciendo valor en Redis..." -ForegroundColor Cyan
$setResult = kubectl exec -it $podName -- /bin/bash -c "$redisCommand SET mykey 'Hello, Redis!'"
if ($setResult -eq "OK") {
    Write-Host "Valor 'Hello, Redis!' guardado correctamente en 'mykey'." -ForegroundColor Green
} else {
    Write-Host "Error al guardar el valor en Redis. Resultado: $setResult" -ForegroundColor Red
}

# Recuperar el valor con GET
Write-Host "Recuperando valor de Redis..." -ForegroundColor Cyan
$getResult = kubectl exec -it $podName -- /bin/bash -c "$redisCommand GET mykey"
if ($getResult -ne "(nil)") {
    Write-Host "Valor recuperado de 'mykey': $getResult" -ForegroundColor Green
} else {
    Write-Host "Error al recuperar el valor de Redis. Resultado: $getResult" -ForegroundColor Red
}

# Eliminar la clave con DEL
Write-Host "Eliminando 'mykey' de Redis..." -ForegroundColor Cyan
$delResult = kubectl exec -it $podName -- /bin/bash -c "$redisCommand DEL mykey"


Write-Host "Pruebas de Redis completadas con éxito en el pod $podName." -ForegroundColor Green
