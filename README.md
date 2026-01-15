# Functionality


Before you begin, import products from inriver using the product collection filter.

You must define the list of product collections in the collections.txt file, 

then import the list into the ItemCollection table using the python manage.py load_collections command.

Alternatively, add the necessary collections manually in the admin section.

This solution allows you to generate QR codes in accordance with the GS1 standard.

It also redirects customers to your product page when they scan the QR code.

There are two types of QR codes:
- PNG
- EPS



The solution has an API.
You can see the description at yourdomain/swagger.


## Functionality
To deploy the solution, you can use the qrdeploy.sh automatic installation file.
chmod +x qrdeploy.sh
sudo ./qrdeploy.sh









