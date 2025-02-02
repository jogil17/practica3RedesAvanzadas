# Detener el script si ocurre un error
$ErrorActionPreference = "Stop"

# Función para mostrar progreso
function Show-Progress {
    param ([string]$Message)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "🚀 $Message" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
}

# 1. Construir la imagen Docker
Show-Progress "Paso 1: Construyendo la imagen Docker..."
docker build -t mi_app:latest .
Write-Host "✅ Imagen Docker construida con éxito." -ForegroundColor Green

# 2. Cargar la imagen en Minikube
Show-Progress "Paso 2: Cargando la imagen en Minikube..."
minikube image load mi_app:latest
Write-Host "✅ Imagen cargada en Minikube." -ForegroundColor Green

# 3. Aplicar el bundle de Prometheus Operator
Show-Progress "Paso 3: Aplicando el Prometheus Operator..."
kubectl apply -n monitoring -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/release-0.66/bundle.yaml
Write-Host "✅ Prometheus Operator aplicado con éxito." -ForegroundColor Green

# 4. Aplicar archivos de configuración personalizados
Show-Progress "Paso 4: Aplicando configuraciones personalizadas de Prometheus..."

Write-Host "Aplicando configuraciones de 'namespaces'..." -ForegroundColor Yellow
kubectl apply -f namespaces.yaml
Write-Host "✅ Configuraciones de 'namespaces' aplicadas." -ForegroundColor Green

Write-Host "Aplicando configuraciones de 'prometheus/'..." -ForegroundColor Yellow
kubectl apply -f prometheus/
Write-Host "✅ Configuraciones de 'prometheus/' aplicadas." -ForegroundColor Green

Write-Host "Aplicando configuraciones de 'manifests/'..." -ForegroundColor Yellow
kubectl apply -f manifests/
Write-Host "✅ Configuraciones de 'manifests/' aplicadas." -ForegroundColor Green

Write-Host "Aplicando configuraciones de 'exporter/'..." -ForegroundColor Yellow
kubectl apply -f exporter/
Write-Host "✅ Configuraciones de 'exporter/' aplicadas." -ForegroundColor Green

Write-Host "Aplicando configuraciones de 'grafana/'..." -ForegroundColor Yellow
kubectl apply -f grafana/
Write-Host "✅ Configuraciones de 'grafana/' aplicadas." -ForegroundColor Green

Write-Host "Aplicando configuraciones de 'servicesMonitor/'..." -ForegroundColor Yellow
kubectl apply -f servicesMonitor/
Write-Host "✅ Configuraciones de 'servicesMonitor/' aplicadas." -ForegroundColor Green
