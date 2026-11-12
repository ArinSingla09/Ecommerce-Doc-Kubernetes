# ShopSphere — AI E-Commerce Microservices

A runnable starter e-commerce platform with a React storefront, six FastAPI microservices,
a local rule-based shopping assistant, Docker Compose for local development, and AKS manifests.

## Services
- `products`: product catalogue and inventory
- `search`: typo-tolerant search and filters (RapidFuzz)
- `cart`: in-memory shopping carts (demo; replace with Redis/PostgreSQL for production)
- `orders`: demo order creation (in-memory)
- `recommendations`: content/category/popularity recommendations
- `chat`: local intent-based shopping assistant; no external AI API
- `frontend`: React/Vite storefront
- `gateway`: Nginx reverse proxy

> This is a functional learning/deployment starter, not a production commerce system. Demo carts/orders are in-memory and reset when pods restart. Authentication, payment processing, durable transactions, rate limiting, observability, and secrets rotation should be added before real customer use.

## Requirements
- Docker Desktop or Docker Engine + Compose plugin
- Node.js 20+ only if running the frontend outside Docker
- Azure CLI, kubectl, and an Azure subscription for AKS deployment

## Run locally
```bash
docker compose up --build
```
Open http://localhost:8080. API health:
- http://localhost:8080/api/products/health
- http://localhost:8080/api/search/health
- http://localhost:8080/api/chat/health

Try the chat:
- "Show me headphones under 5000"
- "Recommend a laptop"
- "Compare headphones and speakers"
- "I need a phone for photography"

Search supports `q`, `category`, `min_price`, and `max_price` query parameters.

## Local development without Docker
Each backend service can be run from its directory:
```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```
Set `PRODUCTS_URL=http://localhost:8001` for services that call products, and set the relevant port per service. The Compose setup is the simplest path.

## Build and push to Azure Container Registry
Set variables:
```bash
az login
az account set --subscription "<SUBSCRIPTION_ID>"
az group create -n rg-shopsphere -l centralindia
az acr create -g rg-shopsphere -n <UNIQUE_ACR_NAME> --sku Basic
az acr login -n <UNIQUE_ACR_NAME>
```
Build images (replace `<ACR_LOGIN_SERVER>` with e.g. `myregistry.azurecr.io`):
```bash
for svc in products search cart orders recommendations chat frontend gateway; do
  docker build -t <ACR_LOGIN_SERVER>/shopsphere-$svc:v1 ./$svc
  docker push <ACR_LOGIN_SERVER>/shopsphere-$svc:v1
done
```

## Create AKS and attach ACR
```bash
az aks create -g rg-shopsphere -n aks-shopsphere \
  --node-count 2 --node-vm-size Standard_D2s_v5 \
  --enable-managed-identity --attach-acr <UNIQUE_ACR_NAME> \
  --generate-ssh-keys
az aks get-credentials -g rg-shopsphere -n aks-shopsphere
kubectl get nodes
```
The VM size and region availability vary. Check quota and pricing before creating resources.

## Deploy
1. Edit `k8s/namespace.yaml` only if you want a different namespace.
2. Update every image in `k8s/apps.yaml` to your ACR login server and tag.
3. Apply:
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/apps.yaml
kubectl apply -f k8s/ingress.yaml
kubectl get pods -n shopsphere
kubectl get svc -n shopsphere
```
The included ingress uses the community NGINX Ingress Controller. Install it first:
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace
```
Then retrieve the ingress public IP:
```bash
kubectl get svc -n ingress-nginx
```
Point your DNS A record to that IP and configure TLS before public production use. For a quick test, port-forward:
```bash
kubectl port-forward -n shopsphere svc/gateway 8080:80
```
Open http://localhost:8080.

## Useful AKS commands
```bash
kubectl get all -n shopsphere
kubectl logs -n shopsphere deploy/chat
kubectl describe pod -n shopsphere <POD_NAME>
kubectl rollout status -n shopsphere deploy/frontend
kubectl scale deploy/products -n shopsphere --replicas=3
kubectl delete -f k8s/apps.yaml
```

## Cost and safety notes
- AKS control-plane pricing depends on tier; nodes, disks, load balancers, ACR and outbound traffic can incur charges.
- Delete the resource group when finished if you no longer need the environment:
  `az group delete -n rg-shopsphere --yes --no-wait`
- Never commit real credentials. Use Kubernetes Secrets or preferably Azure Key Vault + Workload Identity for production.
