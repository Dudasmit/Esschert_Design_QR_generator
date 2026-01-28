# Functionality




This solution allows you to generate QR codes in accordance with the GS1 standard.

It also redirects customers to your product page when they scan the QR code.

There are two types of QR codes:
- PNG
- EPS



The solution has an API.
You can see the description at yourdomain/swagger.

Before you begin, import products from inriver using the product collection filter.

You must define the list of product collections in the collections.txt file, 

then import the list into the ItemCollection table using the python manage.py load_collections command.

Alternatively, add the necessary collections manually in the admin section.


## Deployment

sudo apt update

sudo apt install git -y

Download the project from GitHub:
git clone https://github.com/Dudasmit/Esschert_Design_QR_generator.git

Open the project folder:
cd Esschert_Design_QR_generator

Rename the file with variables:
mv .env_example .env

sudo apt install -y nano

Edit the file, сhange all variables:
nano .env



Collect the container:


docker compose build --no-cache
docker compose up -d

Check if the container is working: 
docker ps

If something went wrong, check the container logs:
docker logs qr_code_genaretor


To deploy the solution, you can use the qrdeploy.sh automatic installation file.
chmod +x ./entrypoint.sh
chmod +x qrdeploy.sh
sudo ./qrdeploy.sh

### If there is an error connecting to MySQL - “Cannot connect to MySQL with provided credentials”:

MySQL must listen to all interfaces:

sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

change:

bind-address = 0.0.0.0

Log in to MySQL locally:

sudo mysql -u root -p


Then check the user you are using in .env:

SELECT user, host FROM mysql.user;


If the user exists, check that they can connect from the desired host (localhost or % for all):

GRANT ALL PRIVILEGES ON your_database.* TO 'your_user'@'%' IDENTIFIED BY 'your_password'; FLUSH PRIVILEGES;


your_database, your_user, your_password — substitute your values from .env.

Restart MySQL:

sudo systemctl restart mysql









