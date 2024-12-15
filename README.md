# Proyecto Kubernetes

Este proyecto se ejecuta en un clúster de Kubernetes utilizando Minikube. A continuación se detallan los pasos para iniciar, probar y detener el proyecto.

## Iniciar el Proyecto

1. **Iniciar Minikube**:
   - Ejecuta el siguiente comando para iniciar Minikube:
     ```bash
     minikube start
     ```

2. **Ejecutar el script de despliegue**:
   - Después, ejecuta el script `deploy.ps1` en PowerShell para desplegar los recursos en Kubernetes:
     ```bash
     .\deploy.ps1
     ```

3. **Habilitar Ingress y Tunnel**:
   - Una vez hecho esto, ejecuta el siguiente comando para habilitar el addon de Ingress y luego habilita el túnel de Minikube:
     ```bash
     minikube addons enable ingress
     minikube tunnel
     ```

4. **Acceder a la aplicación**:
   - Ahora puedes acceder a la aplicación en la siguiente URL:
     ```
     https://127.0.0.1
     ```

## Visualizar Prometheus

Si deseas visualizar Prometheus, sigue estos pasos:

1. **Obtener el nombre del pod**:
   - Ejecuta el siguiente comando para obtener el nombre del pod en el que se está ejecutando Prometheus:
     ```bash
     kubectl get pods
     ```

2. **Hacer port-forward**:
   - Luego, ejecuta el siguiente comando para hacer un port-forward al pod de Prometheus:
     ```bash
     kubectl port-forward pod/<pod-name> 9090:9090
     ```

   - Accede a Prometheus en: `http://localhost:9090`.

## Probar la Caché

Para comprobar que la caché (Redis) está funcionando correctamente, ejecuta el siguiente script:

```bash
.\test_redis.ps1


