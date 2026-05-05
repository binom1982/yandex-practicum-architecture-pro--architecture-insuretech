# Динамическое масштабирование контейнеров

## Часть 1. Динамическая маршрутизация на основании показателей утилизации памяти

### 1. Подготовка кластера

```bash
minikube start
minikube addons enable metrics-server # включаем metrics-server для сбора метрик, которые будет читать HPA
```

```bash

```

Запуск на Windows с Docker

> `metrics-server` не может подключиться к kubelet из-за проблем с сертификатами в Minikube + Docker на Windows.

```bash
# 1. Тянем конкретный тег (latest часто битый)
docker pull bitnamilegacy/metrics-server:0.7.1

# 2. Если скачался — грузим в Minikube и патчим
minikube image load bitnamilegacy/metrics-server:0.7.1
kubectl patch deployment metrics-server -n kube-system --type='json' -p='[
  {"op":"replace","path":"/spec/template/spec/containers/0/image","value":"bitnamilegacy/metrics-server:0.7.1"},
  {"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"},
  {"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-preferred-address-types=InternalIP,Hostname"}
]'
# 2. Примените манифест
kubectl apply -f metrics-server-local.yaml

# 4. Перезапускаем и ждём
kubectl rollout restart deployment metrics-server -n kube-system
sleep 30
kubectl get pods -n kube-system | grep metrics-server
kubectl top pods


Проблема в недостаточных RBAC-правах у metrics-server. Сервис не может создать subjectaccessreviews для авторизации запросов к kubelet.

# 1. Добавляем недостающее правило для authorization.k8s.io
kubectl patch clusterrole system:metrics-server --type='json' -p='[
  {"op":"add","path":"/rules/-","value":{
    "apiGroups":["authorization.k8s.io"],
    "resources":["subjectaccessreviews"],
    "verbs":["create"]
  }}
]'

# 2. Перезапускаем metrics-server
kubectl rollout restart deployment metrics-server -n kube-system

# 3. Ждём и проверяем
sleep 30
kubectl top pods
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
