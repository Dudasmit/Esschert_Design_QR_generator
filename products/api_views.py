# api_views.py
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .serializers import GenerateQRInputSerializer
from .models import Product
from .filters import ProductFilter
from .views import create_and_save_qr_code_eps
import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import base64
from drf_yasg import openapi
from django.views.decorators.csrf import csrf_exempt
import boto3


BUCKET_NAME = os.getenv("BUCKET_NAME")
S3_FOLDER = os.getenv("S3_FOLDER")
AWS_URL = os.getenv("AWS_URL")
s3 = boto3.client("s3")



token_param = openapi.Parameter(
    name='Authorization',
    in_=openapi.IN_HEADER,
    description='Token {your_token}',
    type=openapi.TYPE_STRING
)




class MyEndpoint(APIView):
    def get(self, request):
        return Response({"message": "Hello from the API!"})


    

@csrf_exempt
@swagger_auto_schema(
    #manual_parameters=[token_param],
    method='post',
    request_body=GenerateQRInputSerializer,
    operation_description="Generating QR codes for selected products",
    responses={200: "Successfully", 400: "Request error"}
)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
def generate_qr_api(request):
    serializer = GenerateQRInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    data = serializer.validated_data
    product_ids = data.get("product_ids", [])
    select_all = data.get("select_all", False)
    include_barcode = data.get("include_barcode", False)
    domain = data.get("domain")

    if not product_ids and not select_all:
        return Response({"error": "No products selected"}, status=400)

    if select_all:
        session_filter = request.session.get("last_filter", {})
        product_filter = ProductFilter(session_filter, queryset=Product.objects.all())
        products = product_filter.qs
    else:
        products = Product.objects.filter(name__in=product_ids)

    #os.makedirs(os.path.join(settings.MEDIA_ROOT, S3_FOLDER), exist_ok=True)


    generated_products = []
    for product in products:
        url = f"https://{domain}/01/0"
        result = create_and_save_qr_code_eps(s3,url, product.name, product.barcode, include_barcode, S3_FOLDER)

        if not isinstance(result, dict):
            continue

        product_files = []

        for file_type, file_url in result.items():
            filename = f"{product.name}.{file_type}"
            #local_path = os.path.join(settings.MEDIA_ROOT, S3_FOLDER, filename)

            #try:
                #with open(local_path, "rb") as f:
                    #image_base64 = base64.b64encode(f.read()).decode("utf-8")
            #except Exception as e:
                #image_base64 = None
                #print(f"Не удалось прочитать {local_path}: {e}")

            product_files.append({
                "filename": filename,
                "file_type": file_type,
                "url": file_url,
                #"image_base64": image_base64
            })

        generated_products.append({
            "product": product.name,
            "files": product_files
        })

    return Response({
        "success": True,
        "generated": len(generated_products),
        "files": generated_products
    }, status=200)


file_type_param = openapi.Parameter(
    'file_type',
    openapi.IN_QUERY,
    description="Тип файла QR-кода: png или eps",
    type=openapi.TYPE_STRING,
    enum=['png', 'eps'],
    required=False
)


@csrf_exempt
@swagger_auto_schema(
    method='get',
    manual_parameters=[file_type_param],
    operation_description="Получить список всех сгенерированных QR-кодов из S3.",
    responses={
        200: openapi.Response(
            description="Успешный ответ со списком QR-кодов",
            examples={
                "application/json": {
                    "qr_codes": [
                        {
                            "filename": "product_1.png",
                            "url": "https://example-bucket.s3.amazonaws.com/qrcodes/product_1.png?..."
                        },
                        {
                            "filename": "product_2.png",
                            "url": "https://example-bucket.s3.amazonaws.com/qrcodes/product_2.png?..."
                        }
                    ]
                }
            }
        ),
        401: "Неавторизовано — отсутствует или неверный токен",
        500: "Ошибка при доступе к S3"
    }
)
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_all_generated_qr_codes(request):
    """
    Возвращает список всех сгенерированных QR-кодов, 
    загруженных в S3. Для доступа требуется токен авторизации.
    Можно фильтровать по типу файла: ?file_type=png или ?file_type=eps
    """
    qr_codes = []

    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=S3_FOLDER)
        
        contents = response.get('Contents', [])

        # ✅ фильтрация по расширению файла (если указано в query params)
        file_type = request.query_params.get('file_type')
        if file_type:
            contents = [
                obj for obj in contents
                if obj['Key'].lower().endswith(f'.{file_type.lower()}')
            ]

        
        for obj in contents:
            key = obj['Key']
         
            filename = os.path.basename(key)
            if key.endswith('/'):# or not key.lower().endswith('.png'):
                continue

          
            file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{key}"
            try:
                s3_object = s3.get_object(Bucket=BUCKET_NAME, Key=key)
                image_content = s3_object['Body'].read()
                image_base64 = base64.b64encode(image_content).decode('utf-8')
            except Exception as e:
                image_base64 = None

            qr_codes.append({
                "filename": filename,
                "url": file_url,
                "image_base64": image_base64
            })
    except Exception as e:
        return Response({"error": str(e)}, status=500)

    return Response({"qr_codes": qr_codes}, status=200)
