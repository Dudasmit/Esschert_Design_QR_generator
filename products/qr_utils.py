# products/utils/qr_utils.py

import os
import qrcode
from PIL import Image
from urllib.request import urlopen
from django.conf import settings
from pyzbar.pyzbar import decode
import requests
from io import BytesIO


def extract_qr_data_from_image(name):
    #url =  f"https://esschertdesign-prod.s3.eu-west-1.amazonaws.com/qrcodes/{name}.png?mtime=0"
    url =  f"{os.getenv("AWS_URL")}{name}.png?mtime=0"
    
    if not check_url_exists(url):
        return None

    try:
        #print("Загрузка изображения из URL:", url)
        response = requests.get(url)
        img = Image.open(BytesIO(response.content))
        # Декодируем QR
        decoded_objects = decode(img)
    
        #image = Image.open(image_path)
        #decoded_objects = decode(image)
        if decoded_objects:
            qr_data = decoded_objects[0].data.decode("utf-8")
            #print(f"Декодированные данные из QR: {qr_data}")
            return qr_data
    except Exception as e:
        print(f"Ошибка при декодировании QR: {e}")
    return None

def check_url_exists(url):
    try:
        response = urlopen(url)
        return response.status == 200
    except:
        return False

def remove_transparency(im, bg_color=(255, 255, 255)):
    if im.mode in ('RGBA', 'LA'):
        background = Image.new('RGB', im.size, bg_color)
        background.paste(im, mask=im.split()[3])  # 3 is the alpha channel
        return background
    return im



def create_and_save_qr_code_eps(s3, url, item, GTIN, include_barcode, folder):
    # Формируем URL для QR
    data_url = (os.getenv("QR_REDIRECT_URL") or "") + str(item)
    bucket_name = os.getenv("BUCKET_NAME")

    if not check_url_exists(data_url):
        print("Ссылка не существует:", data_url)

    data = url + str(GTIN)
    
    # Создаем QR-код
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # --- PNG ---
    try:
        png_buffer = BytesIO()
        img.save(png_buffer, format="PNG")
        png_buffer.seek(0)

        s3.upload_fileobj(
            png_buffer,
            bucket_name,
            os.path.join(folder, f"{item}.png"),
            ExtraArgs={'ACL': 'public-read'}
        )
    except Exception as e:
        print("PNG upload error:", e)
        return False

    # --- EPS ---
    try:
        eps_buffer = BytesIO()
        img.save(eps_buffer, format="EPS")
        eps_buffer.seek(0)

        s3.upload_fileobj(
            eps_buffer,
            bucket_name,
            os.path.join(folder, f"{item}.eps"),
            ExtraArgs={'ACL': 'public-read'}
        )
    except Exception as e:
        print("EPS upload error:", e)
        return False

    return {
        "png": f"https://{bucket_name}.s3.amazonaws.com/{folder}{item}.png",
        "eps": f"https://{bucket_name}.s3.amazonaws.com/{folder}{item}.eps"
    }