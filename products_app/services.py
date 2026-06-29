import os
import requests

domain = os.environ.get('QUERY_PRODUCTS_DOMAIN', 'http://localhost:8001')


def get_products_from_fastapi(request):
    min_price = request.query_params.get('min_price')
    max_price = request.query_params.get('max_price')

    params = {
        "page": int(request.query_params.get('page', 1)),
        "lang": request.query_params.get('lang', 'en'),
        "page_size": int(request.query_params.get('limit', 20)),
        "cat": request.query_params.get('category'),
        "q": request.query_params.get('search'),
        "start_price": float(min_price) if min_price else None,
        "end_price": float(max_price) if max_price else None,
        "discount": request.query_params.get('discount'),
        "sort": request.query_params.get('sort'),
    }

    url = f"{domain}/items"

    try:
        response = requests.get(url, params=params, timeout=10)
        return response.json()
    except Exception as e:
        print(f"FastAPI Product Service Error: {e}")
        return {
            "items": {
                "page": "1",
                "real_total_results": 0,
                "total_results": 0,
                "page_size": 2,
                "page_count": 1,
                "item": []
            }
        }


def get_products_details_from_fastapi(product_id: str, request=None):
    url = f"{domain}/items/{product_id}/"

    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        print(f"FastAPI Product Service Error: {e}")
        return {
            "item": {
                "num_iid": "",
                "title": "",
                "desc_short": "",
                "price": "",
                "total_price": "",
                "suggestive_price": "",
                "orginal_price": "",
                "nick": "",
                "num": "",
                "min_num": "",
                "detail_url": "",
                "pic_url": "",
                "brand": "",
                "brandId": "",
                "rootCatId": "",
                "cid": "",
                "desc": "",
                "item_imgs": "",
                "url": "",
                "item_weight": "",
                "location": "",
                "post_fee": "",
                "express_fee": "",
                "ems_fee": "",
                "shipping_to": "",
                "video": "",
                "sample_id": "",
                "props_name": "",
                "prop_imgs": "",
                "prop_img": "",
                "properties": "",
                "property_alias": "",
                "props": "",
                "name": "",
                "value": "",
                "total_sold": "",
                "scale": "",
                "sellUnit": "",
                "skus": "",
                "sku": "",
                "sales": "",
                "properties_name": "",
                "quantity": "",
                "sku_id": "",
                "spec_id": "",
                "seller_id": "",
                "shop_id": "",
                "props_list": "",
                "0:0": "",
                "0:1": "",
                "0:2": "",
                "0:3": "",
                "0:4": "",
                "0:5": "",
                "0:6": "",
                "0:7": "",
                "priceRange": "",
                "priceRangeOriginal": ""
            }
        }


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
        print(f"FastAPI Product Service Error: {e}")
        return {"products": [], "total": 0}