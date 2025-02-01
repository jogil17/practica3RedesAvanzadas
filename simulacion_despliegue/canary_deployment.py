import subprocess
import sys
import time

# Configuración inicial
NEW_IMAGE = "jogil17/mi_app"
DEPLOYMENT_NAME = "app"
NAMESPACE = "default"
REPLICAS = 3
TIMEOUT = 180

# Función para ejecutar comandos
def run_command(command):
    """Ejecuta un comando y maneja errores."""
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error ejecutando el comando: {command}\n{result.stderr.decode()}")
        sys.exit(1)
    return result.stdout.decode().strip()

# Verificar kubectl
try:
    run_command("kubectl version --client")
except subprocess.CalledProcessError:
    print("kubectl no está instalado o configurado correctamente.")
    sys.exit(1)

print("\nInicio del despliegue Canary...")
time.sleep(2)

# Mostrar estado inicial
print("\nEstado inicial de los pods:")
print(run_command(f"kubectl get pods --namespace={NAMESPACE}"))
time.sleep(2)

# Actualizar una réplica a la nueva versión
print(f"\nActualizando el despliegue {DEPLOYMENT_NAME} a la nueva imagen: {NEW_IMAGE}")
run_command(f"kubectl set image deployment/{DEPLOYMENT_NAME} app={NEW_IMAGE} --namespace={NAMESPACE}")
time.sleep(2)

# Escalar temporalmente a 1 réplica
print(f"\nEscalando el despliegue {DEPLOYMENT_NAME} a 1 réplica para pruebas Canary...")
run_command(f"kubectl scale deployment {DEPLOYMENT_NAME} --replicas=1 --namespace={NAMESPACE}")
time.sleep(2)

# Verificar rollout
print(f"\nEsperando que el despliegue esté listo (timeout: {TIMEOUT} segundos)...")
try:
    run_command(f"kubectl rollout status deployment/{DEPLOYMENT_NAME} --namespace={NAMESPACE} --timeout={TIMEOUT}s")
except subprocess.CalledProcessError:
    print("\nEl despliegue no se completó a tiempo. Revirtiendo cambios...")
    run_command(f"kubectl rollout undo deployment/{DEPLOYMENT_NAME} --namespace={NAMESPACE}")
    run_command(f"kubectl scale deployment {DEPLOYMENT_NAME} --replicas={REPLICAS} --namespace={NAMESPACE}")
    sys.exit(1)

# Obtener el pod actualizado
print("\nObteniendo el pod actualizado para pruebas de health check...")
try:
    pod_name = run_command(
        f"kubectl get pods --namespace={NAMESPACE} --selector=app=app "
        f"--field-selector=status.phase=Running -o jsonpath={{.items[0].metadata.name}}"
    ).strip()  # Elimina espacios en blanco
    print(f"Nombre del pod obtenido: {pod_name}")
except Exception as e:
    print(f"\nError obteniendo el pod: {e}. Revirtiendo despliegue...")
    run_command(f"kubectl rollout undo deployment/{DEPLOYMENT_NAME} --namespace={NAMESPACE}")
    run_command(f"kubectl scale deployment {DEPLOYMENT_NAME} --replicas={REPLICAS} --namespace={NAMESPACE}")
    sys.exit(1)

# Realizar health check
print(f"\nRealizando health check en el pod: {pod_name}")
try:
    health_output = run_command(
        f"kubectl exec {pod_name} --namespace={NAMESPACE} -- curl -s http://localhost:5000/health"
    )
    print(f"Health check output: {health_output}")

    if '"status":"healthy"' not in health_output:
        raise ValueError("Health check fallido")
except Exception as e:
    print(f"\nHealth check fallido: {e}. Revirtiendo despliegue...")
    run_command(f"kubectl rollout undo deployment/{DEPLOYMENT_NAME} --namespace={NAMESPACE}")
    run_command(f"kubectl scale deployment {DEPLOYMENT_NAME} --replicas={REPLICAS} --namespace={NAMESPACE}")
    sys.exit(1)


# Escalar a 3 réplicas
print("\nHealth check exitoso. Escalando el despliegue a 3 réplicas...")
run_command(f"kubectl scale deployment {DEPLOYMENT_NAME} --replicas={REPLICAS} --namespace={NAMESPACE}")

# Mostrar estado final
print("\nEstado final de los pods:")
print(run_command(f"kubectl get pods --namespace={NAMESPACE}"))
print("\nDespliegue Canary completado exitosamente.")
