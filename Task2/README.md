# Динамическое масштабирование контейнеров

## Часть 1. Динамическая маршрутизация на основании показателей утилизации памяти

### 1. Подготовка кластера

```bash
minikube delete --all --purge

minikube start --driver=docker
minikube addons enable metrics-server # включаем metrics-server для сбора метрик, которые будет читать HPA
kubectl get pods -n kube-system | findstr metrics-server
kubectl top nodes
```

Запуск через Kubernetes на Docker Desktop

```bash
Переключите контекст kubectl на встроенный кластер Docker Desktop:
kubectl config use-context docker-desktop
#Как включить metrics-server в Docker Desktop:

# 1. Скачайте манифест последней версии
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# 2. Добавьте аргумент --kubelet-insecure-tls (обязательно для Docker Desktop)
kubectl patch deployment metrics-server -n kube-system --type "json" \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

#Проверка

kubectl wait --for=condition=Ready pod -l k8s-app=metrics-server -n kube-system --timeout=120s
kubectl top nodes
kubectl top pods -A



```

### 2. Деплой приложения и HPA

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa-memory.yaml
```

### 3. Получение URL для Locust

```bash
minikube service scaletestapp-service --url
```

### 4. Запуск нагрузки (в соседнем терминале)

```bash
locust --host=<URL_ИЗ_ШАГА_3> # locust --host=http://127.0.0.1:64211


MINIKUBE_IP=$(minikube ip)
locust --host=http://$MINIKUBE_IP:30080
```

* Откройте http://localhost:8089
* Запустить тест.
* Посмотреть результаты в дашборде Kubernetes

```bash
minikube dashboard # После запуска откроется страница в браузере
```

## Часть 2. Динамическая маршрутизация на основании показателей количества запросов в секунду

## 5. Для Части 2: установите Prometheus и prometheus-adapter, затем:

```bash
kubectl apply -f hpa-rps.yaml
```

Запустите Locust повторно для проверки масштабирования по RPS.
