import subprocess
import sys
import time
import json
import tempfile

# Configuración inicial
GREEN_IMAGE = "jogil17/mi_app"
DEPLOYMENT_GREEN = "app-green"
DEPLOYMENT_NAME = "app"
NAMESPACE = "default"
SERVICE_NAME = "app-service"
REPLICAS = 3
TIMEOUT = 120

# Función para ejecutar comandos
def run_command(command):
    """Ejecuta un comando y verifica errores."""
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error ejecutando el comando: {command}\n{result.stderr.decode()}")
        sys.exit(1)
    return result.stdout.decode()

# Inicio del despliegue Blue-Green
print("\nIniciando despliegue Blue-Green...")
time.sleep(2)

# Paso 1: Eliminar cualquier despliegue Green existente
print("\nEliminando despliegue Green existente si lo hay...")
run_command(f"kubectl delete deployment {DEPLOYMENT_GREEN} --namespace={NAMESPACE} --ignore-not-found=true")
time.sleep(2)

# Paso 2: Crear despliegue Green
print("\nCreando despliegue Green con la nueva imagen...")
run_command(f"kubectl create deployment {DEPLOYMENT_GREEN} --image={GREEN_IMAGE} --namespace={NAMESPACE}")
time.sleep(5)

# Paso 3: Esperar a que el despliegue Green esté listo
print(f"\nEsperando a que el despliegue {DEPLOYMENT_GREEN} esté listo...")
try:
    run_command(f"kubectl rollout status deployment/{DEPLOYMENT_GREEN} --namespace={NAMESPACE} --timeout={TIMEOUT}s")
except subprocess.CalledProcessError:
    print("El despliegue Green no está listo a tiempo. Revirtiendo...")
    run_command(f"kubectl delete deployment {DEPLOYMENT_GREEN} --namespace={NAMESPACE}")
    sys.exit(1)

# Verificando el health del despliegue Green
print("Verificando el health del despliegue Green...")
time.sleep(2)

# Obtener el nombre del pod Green
try:
    green_pod_name = run_command(
        f"kubectl get pods --namespace={NAMESPACE} --selector=app={DEPLOYMENT_GREEN} "
        f"--field-selector=status.phase=Running -o jsonpath='{{.items[0].metadata.name}}'"
    ).strip()
except Exception as e:
    print(f"Error obteniendo el nombre del pod: {e}")
    sys.exit(1)

if not green_pod_name:
    print("Error: No se encontró un pod en ejecución para el despliegue Green.")
    run_command(f"kubectl delete deployment {DEPLOYMENT_GREEN} --namespace={NAMESPACE}")
    sys.exit(1)

print(f"Nombre del pod Green encontrado: {green_pod_name}")

# Realizando health check real
print(f"\nRealizando health check en el pod: {green_pod_name}")

# Limpia el nombre del pod y elimina comillas
cleaned_pod_name = green_pod_name.strip().replace("'", "").replace('"', "")

try:
    health_output = run_command(
        f"kubectl exec {cleaned_pod_name} --namespace={NAMESPACE} -- curl -s http://localhost:5000/health"
    ).strip()  # Elimina espacios adicionales
    print(f"Health check output: {health_output}")

    # Convertir a minúsculas para evitar errores de comparación
    if '"status":"healthy"' not in health_output.replace(" ", "").lower():
        raise Exception("Health check fallido")
except Exception as e:
    print(f"\nHealth check fallido: {e}. Revirtiendo...")
    run_command(f"kubectl delete deployment {DEPLOYMENT_GREEN} --namespace={NAMESPACE}")
    sys.exit(1)

print("\nHealth check exitoso. Actualizando el servicio para apuntar al despliegue Green...")

# Paso 4: Escalar despliegue Green
print(f"\nEscalando despliegue {DEPLOYMENT_GREEN} a {REPLICAS} réplicas...")
run_command(f"kubectl scale deployment {DEPLOYMENT_GREEN} --replicas={REPLICAS} --namespace={NAMESPACE}")
time.sleep(5)

# Paso 5: Actualizar el servicio para apuntar al despliegue Green
print("\nActualizando el servicio para apuntar al despliegue Green...")

patch_data = {
    "spec": {
        "selector": {
            "app": DEPLOYMENT_GREEN
        }
    }
}

with tempfile.NamedTemporaryFile('w', delete=False, suffix=".json") as temp_file:
    json.dump(patch_data, temp_file)
    temp_file_path = temp_file.name

try:
    command = f"kubectl patch service {SERVICE_NAME} --namespace={NAMESPACE} --patch-file {temp_file_path}"
    print(f"Ejecutando comando: {command}")
    run_command(command)
finally:
    import os
    os.unlink(temp_file_path)

# Paso 6: Eliminar el despliegue anterior (Blue o original)
print("\nEliminando despliegue original...")
run_command(f"kubectl delete deployment {DEPLOYMENT_NAME} --namespace={NAMESPACE}")

# Paso 7: Mostrar el estado final
print("\nMostrando estado final de los pods...")
time.sleep(5)
print(run_command(f"kubectl get pods --namespace={NAMESPACE}"))

print("\nDespliegue Blue-Green completado con éxito.")
