## This is Distributed Systems Project: BookVerse

### Dev Setup

service map:

8001 - book_catalog  
8002 - auth  
8003 - book_pub_buy  
8004 - book_review_recommend  
8005 - chatbot  

- run `pip install -r requirements.txt`
- run `docker compose up -d` inside book_catalog  
- run `python db_setup.py`  
- run `uvicorn api:app --host 0.0.0.0 --port 8001 --reload` inside book_catalog
- run `uvicorn api:app --host 0.0.0.0 --port 8002 --reload` inside auth
- run `uvicorn api:app --host 0.0.0.0 --port 8003 --reload` inside book_pub_buy
- run `uvicorn api:app --host 0.0.0.0 --port 8004 --reload` inside book_review_recommend
- run `uvicorn api:app --host 0.0.0.0 --port 8005 --reload` inside chatbot


### Prod Setup

use k8s_deployment for production deployment