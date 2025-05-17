## This is Distributed Systems Project: BookVerse

### Dev Setup

service map:

8001 - auth  
8002 - book_catalog  
8003 - book_pub_buy  
8004 - book_review_recommend    

- run `pip install -r requirements.txt`
- run `docker compose up -d`  
- run `python data_setup.py` inside init_data with with IS_PROD=False
- run `uvicorn api:app --host 0.0.0.0 --port 8001 --reload` inside auth
- run `uvicorn api:app --host 0.0.0.0 --port 8002 --reload` inside book_catalog
- run `uvicorn api:app --host 0.0.0.0 --port 8003 --reload` inside book_pub_buy
- run `uvicorn api:app --host 0.0.0.0 --port 8004 --reload` inside book_review_recommend
- run `npm install` in bookverse_ui
- run `npm start` in bookverse_ui


### Prod Setup

use k8s_deployment for production deployment

- open docker desktop
- Go to Settings > Kubernetes
- Check “Enable Kubernetes”
- Click “Apply & Restart”
- Wait until the Kubernetes status turns "Running"
- `kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.12.2/deploy/static/provider/cloud/deploy.yaml` (only once)
- `kubectl apply -f .`
- check pod status: `kubectl get pods --all-namespaces`
- check services: `kubectl get svc --all-namespaces`
- run `python data_setup.py` inside init_data with IS_PROD=True
- in bookverse_ui/backend_links.js set prod = true
- run `npm install` in bookverse_ui
- run `npm start` in bookverse_ui

clean up resources:  

- `kubectl delete all --all -n ingress-nginx`
- `kubectl delete all --all -n bookverse`