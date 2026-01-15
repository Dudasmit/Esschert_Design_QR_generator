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


## Deployment

git clone https://github.com/Dudasmit/Esschert_Design_QR_generator.git

cd inriver_QR_generator_AWS

Rename the file with variables:
mv .env_example .env

Edit the file, сhange all variables:
nano .env



Collect the container:


docker compose build --no-cache
docker compose up -d

Check if the container is working: 

docker ps


To deploy the solution, you can use the qrdeploy.sh automatic installation file.
chmod +x qrdeploy.sh
sudo ./qrdeploy.sh












