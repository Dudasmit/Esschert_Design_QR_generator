from django.core.management.base import BaseCommand
import requests
import json
from products.models import Product
from datetime import date
from urllib.parse import quote
import os

class Command(BaseCommand):
    help = "Загрузка товаров из inRiver"
    
    
    def get_inriver_header(self):
        headers_inRiver = dict(Accept='application/json')
        headers_inRiver['Content-type'] = 'application/json'
        headers_inRiver['X-inRiver-APIKey'] = os.getenv("IN_RIVER_API_KEY")
        return headers_inRiver
    
    def get_inriver_url(self):
        return 'https://api-prod1a-euw.productmarketingcloud.com'

    def handle(self, *args, **kwargs):
        json_request =  {
            "systemCriteria": [ ],
            "dataCriteria": [ {
                "fieldTypeId": "ItemIndicationWebshop",
                "value": "1",
                "operator": "Equal"
                }
                             ]
            }
        response = requests.post('{}/api/v1.0.0/query'.format(self.get_inriver_url()),
                                 headers= self.get_inriver_header(), data= json.dumps(json_request))
        if response.status_code == 200:
            products = response.json()['entityIds']

        for iditem in products:
            resp_get_linkEntityId = requests.get('{}/api/v1.0.0/entities/{}/fieldvalues'.format(self.get_inriver_url(),int(iditem)),headers= self.get_inriver_header())
            if resp_get_linkEntityId.text != '[]' and resp_get_linkEntityId.status_code == 200:
                json_data = resp_get_linkEntityId.json()
                ItemGTIN = next((item["value"] for item in json_data if item["fieldTypeId"] == "ItemGTIN"), None)
                if ItemGTIN is not  None:
                    barcode = ItemGTIN
                else:
                    ItemGTIN = next((item["value"] for item in json_data if item["fieldTypeId"] == "BundleGTIN"), None)
                
            Product.objects.update_or_create(
                barcode = barcode,
                defaults={
                    'name': next((item_["value"] for item_ in json_data if item_["fieldTypeId"] == "ItemCode"), None),
                    'created_at': date.today(),
                    #'group': item['group'],
                    'show_on_site': True,
                    'external_id' : int(iditem),
                }
            )
            
