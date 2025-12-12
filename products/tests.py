from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Product
from unittest.mock import patch, MagicMock
import base64

class GenerateQRAPITestCase(APITestCase):
    def setUp(self):
        self.url = reverse('generate_qr_api')
        
        self.qr_list_url = reverse('get_all_generated_qr_codes')
        # создаём тестовые продукты
        self.product1 = Product.objects.create(
            name="34100030", barcode="8713968316602", created_at="2024-01-01",
            group="Test", show_on_site=True, external_id="85053"
        )
        self.product2 = Product.objects.create(
            name="34100031", barcode="8713968316619", created_at="2024-01-01",
            group="Test", show_on_site=True, external_id="85063"
        )
        # создаём тестового пользователя и токен
        from django.contrib.auth.models import User
        from rest_framework.authtoken.models import Token

        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)

        # добавляем токен в клиент
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_generate_qr_for_selected_products(self):
        payload = {
            "product_ids": [self.product1.id, self.product2.id],
            "select_all": False,
            "include_barcode": True,
            "domain": "tikhonovskyi.com"  # 👈 добавлено
        }
        response = self.client.post(self.url, payload, format='json')
        data = response.json()
        print("DEBUG:", data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["generated"], 2)
        self.assertTrue(data["success"])    


    def test_generate_qr_missing_domain(self):
        payload = {
            "product_ids": [self.product1.id],
            "select_all": False,
            "include_barcode": True
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, 400)
        #self.assertIn("error", response.json())
        self.assertIn("domain", response.json())

    def test_generate_qr_nothing_selected(self):
        payload = {
            "product_ids": [],
            "select_all": False,
            "include_barcode": False,
            "domain": ""
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, 400)
        
        
     # === Новые тесты для get_all_generated_qr_codes ===
    @patch('products.api_views.s3')  # замените 'your_app.api_views' на реальный путь к функции
    def test_get_all_generated_qr_codes(self, mock_s3):
        # Подготавливаем фиктивные объекты S3
        mock_s3.list_objects_v2.return_value = {
            'Contents': [
                {'Key': 'qrcodes/34100030.png'},
                {'Key': 'qrcodes/34100031.eps'},
                {'Key': 'qrcodes/'},  # папка
            ]
        }

        # Подготовка объекта get_object
        def get_object_side_effect(Bucket, Key):
            mock_obj = MagicMock()
            mock_obj['Body'].read.return_value = b'testcontent'
            return mock_obj

        mock_s3.get_object.side_effect = get_object_side_effect

        # Тест без фильтра
        response = self.client.get(self.qr_list_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['qr_codes']), 2)  # png и eps
        for item in data['qr_codes']:
            self.assertIn('filename', item)
            self.assertIn('url', item)
            self.assertTrue(base64.b64decode(item['image_base64']))

        # Тест фильтрации по png
        response = self.client.get(self.qr_list_url, {'file_type': 'png'})
        data = response.json()
        self.assertEqual(len(data['qr_codes']), 1)
        self.assertTrue(data['qr_codes'][0]['filename'].endswith('.png'))

        # Тест фильтрации по eps
        response = self.client.get(self.qr_list_url, {'file_type': 'eps'})
        data = response.json()
        self.assertEqual(len(data['qr_codes']), 1)
        self.assertTrue(data['qr_codes'][0]['filename'].endswith('.eps'))
