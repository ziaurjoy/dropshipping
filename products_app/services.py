# apps/products/services.py
import os
import requests
from django.conf import settings
from dotenv import load_dotenv
domain = os.environ.get('QUERY_PRODUCTS_DOMAIN', 'http://localhost:8001')

# def get_products_from_fastapi(
#     page: int = 0,
#     limit: int = 20,
#     category: str = None,
#     search: str = None,
#     request=None
# ):
#     url = f"{domain}/products/"

#     app_key = request.headers.get('app-key')
#     secret_key = request.headers.get('secret-key')

#     headers = {
#         "app-key": app_key,
#         "secret-key": secret_key,
#     }

#     params = {"page": page, "limit": limit}
#     if category:
#         params["category"] = category
#     if search:
#         params["searching"] = search

#     try:
#         response = requests.get(url, headers=headers, params=params, timeout=10)
#         return response.json()
#     except Exception as e:
#         # Log error
#         print(f"FastAPI Product Service Error: {e}")
#         return {"products": [], "total": 0}


def get_products_from_fastapi(
    page: int = 1,
    limit: int = 20,
    category: str = None,
    search: str = None,
    min_price: float = None,
    max_price: float = None,
    discount: bool = None,
    sort: str = None,
    request=None
):
    url = f"{domain}/products/"

    headers = {
        "app-key":    request.headers.get('app-key'),
        "secret-key": request.headers.get('secret-key'),
    }

    params = {"page": page, "limit": limit}

    if search:
        params["searching"] = search
    if category:
        params["category"] = category
    if min_price is not None:
        params["min_price"] = min_price
    if max_price is not None:
        params["max_price"] = max_price
    if discount is not None:
        params["discount"] = str(discount).lower()   # FastAPI expects "true"/"false"
    if sort:
        params["sort"] = sort

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        # print('FastAPI Product Service Response:', response.json())
        return response.json()
    except Exception as e:
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


def get_category_from_fastapi(request=None):
    url = f"{domain}/categories/"

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