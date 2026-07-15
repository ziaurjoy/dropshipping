from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from django.core.cache import cache
from products_app.models import SettingExchangeRate

class RedisCachingTests(TestCase):
    def setUp(self):
        # Clear cache before each test
        cache.clear()
        
        # Create required BDT exchange rate SettingExchangeRate
        SettingExchangeRate.objects.get_or_create(
            code='BDT',
            defaults={
                'name': 'Bangladeshi Taka',
                'symbol': '৳',
                'is_active': True,
                'rate': 16.5
            }
        )

    def tearDown(self):
        cache.clear()

    @patch('products_app.views.get_products_from_fastapi')
    def test_product_list_caching(self, mock_get_products):
        # Define mock return data
        mock_data = {
            "items": {
                "page": "1",
                "real_total_results": 1,
                "total_results": 1,
                "page_size": 20,
                "page_count": 1,
                "item": [
                    {
                        "num_iid": "123456",
                        "title": "Test Product",
                        "price": "10.0"
                    }
                ]
            }
        }
        mock_get_products.return_value = mock_data

        client1 = Client()
        url = reverse('product-from-1688-list')

        # First request (should hit FastAPI and cache)
        response1 = client1.get(url, {'search': 'test'})
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(mock_get_products.call_count, 1)

        # Second request (should hit Cache, not FastAPI)
        response2 = client1.get(url, {'search': 'test'})
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(mock_get_products.call_count, 1)  # call_count remains 1

        # Request with different params (should hit FastAPI)
        response3 = client1.get(url, {'search': 'another'})
        self.assertEqual(response3.status_code, 200)
        self.assertEqual(mock_get_products.call_count, 2)

        # Request from another client session (should hit FastAPI due to session isolation)
        client2 = Client()
        response4 = client2.get(url, {'search': 'test'})
        self.assertEqual(response4.status_code, 200)
        self.assertEqual(mock_get_products.call_count, 3)

    @patch('products_app.views.get_products_details_from_fastapi')
    def test_product_detail_caching(self, mock_get_details):
        mock_data = {
            "item": {
                "num_iid": "123456",
                "title": "Test Product Detail",
                "price": "10.0"
            }
        }
        mock_get_details.return_value = mock_data

        client = Client()
        url = reverse('product-from-1688-detail', kwargs={'pk': '123456'})

        # First request (should hit FastAPI and cache)
        response1 = client.get(url)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(mock_get_details.call_count, 1)

        # Second request (should hit Cache, not FastAPI)
        response2 = client.get(url)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(mock_get_details.call_count, 1)
