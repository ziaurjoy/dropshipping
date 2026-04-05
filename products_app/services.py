# apps/products/services.py
import os
import requests
from django.conf import settings
from dotenv import load_dotenv
domain = os.environ.get('QUERY_PRODUCTS_DOMAIN', 'http://localhost:8001')

def get_products_from_fastapi(
    page: int = 0,
    limit: int = 20,
    category: str = None,
    search: str = None,
    request=None
):
    url = f"{domain}/products/"

    app_key = request.headers.get('app-key')
    secret_key = request.headers.get('secret-key')

    headers = {
        "app-key": app_key,
        "secret-key": secret_key,
    }

    params = {"page": page, "limit": limit}
    if category:
        params["category"] = category
    if search:
        params["searching"] = search

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        return response.json()
    except Exception as e:
        # Log error
        print(f"FastAPI Product Service Error: {e}")
        return {"products": [], "total": 0}



def get_products_details_from_fastapi(
    product_id: str,
    request=None
):
    url = f"{domain}/products/{product_id}/"

    app_key = request.headers.get('app-key')
    secret_key = request.headers.get('secret-key')

    headers = {
        "app-key": app_key,
        "secret-key": secret_key,
    }


    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        # Log error
        print(f"FastAPI Product Service Error: {e}")
        return {"products": [], "total": 0}