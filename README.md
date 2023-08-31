# Flask REST API in AWS (future enhancement, flaskenv, security and buckets)

This is a simple Flask-based REST API project that needs to:
1.	Receive historical data from CSV files
2.	Upload these files to the new DB
3.	Be able to insert batch transactions (1 up to 1000 rows) with one request
4.  On Cloud

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Running the API](#running-the-api)
  - [Endpoints](#endpoints)
  - [Endpoints SQL](#endpoints-sql)
- [Thanks for passing by](#thanks-for-passing-by)


## Getting Started

These instructions aim to assist anyone in running and testing the project on cloud. Some minimum charges may occur, it can be done using all free-tyer eligible option on AWS though. If you are not familiar with RDBMS or AWS services, you can still proceed; however, you will likely need to refer to other tutorials, as you will require a running instance of a local database server to observe the API's functionality.

### Prerequisites

You need to have the following software installed:

- Python (>=3.6)
  - will be provided a requirements.txt
- EC 2 Instance
  - Apache2
  - WSGI-MOD
- MySQL MariaDB Server on S3
    - DB structure will be provided considering a MySQL Engine
- MySQL MariaDB CLient on EC2

### Installation

1. Install apache and wsgi on your EC2
```bash
sudo apt-get update
sudo apt-get install apache2
sudo apt-get install libapache2-mod-wsgi-py3
```

2. Clone the repository to your EC2 instance and give it a simple name, move it to path for the apache web server, the default is `/var/www/html/`
```bash
   sudo git clone https://github.com/erick-efc/simple_flask_rest_api_cloud flask-api
   sudo mv ./flask-api /var/www/html/
```
3. Install Python 3 (if not installed yet), PIP and all requirements from requirements.txt:
```bash
sudo apt install python3-pip
sudo pip3 install flask
sudo pip3 install -r requirements.txt
```

4. Confiure apache2 `/etc/apache2/sites-enabled/000-default.conf` file, just above `DocumentRoot /var/www/html` entry insert the following:
```bash
      WSGIDaemonProcess flask-app threads=5
      WSGIScriptAlias / /var/www/html/flask-app/app.wsgi

      <Directory flask-app>
              WSGIProcessGroup flask-app
              WSGIApplicationGroup %{GLOBAL}
              Order deny,allow
              Allow from all
      </Directory>
```


5. Set up the DB (we will a MariaDB on S3, as explained)
- On your dashboard os AWS S3 start a MariaDB instance and connect to your EC2
- Locate the endpoint and port confiration on your dashboard
- open a new terminal in your EC2 and install MariaDB, as a good practise start by adding the MariaDB official apt repo:
``` bash
curl -LsS https://r.mariadb.com/downloads/mariadb_repo_setup | sudo bash
sudo apt-get install mariadb-server mariadb-client -y
```
- secure MariaDB (input your root password (Y for all and create a password for root)
```bash
sudo mysql_secure_installation
```
- connect to MariaDB using the endpoint in your dashboard, also build the DB using the provided empty sql dump file `db_structure.sql`
``` bash
mysql -h your_endpoint -P 3306 -u root -p
source /var/www/html/flask-app/misc/db_structure.sql;
```
- still inside MariaDB CLI, create a new user to interact with you api. To interact with this app without need to change config, you can you use:
``` sql
CREATE USER 'api_user'@'%' IDENTIFIED BY 'your_password';
```
- grant the access to the new user accordingly
``` sql
GRANT SELECT, INSERT, UPDATE, DELETE ON api_db.* TO 'api_user'@'%';
```
- flush
``` sql
FLUSH PRIVILEGES;
```
6. Edit app.py on `/var/www/html/flask-api/`
```python
app.config['MYSQL_HOST'] = 'your-endpoint-here'
```
7. Restart apache:
```bash
sudo service apache2 restart
```

### Endpoints

- `POST /api/upload_hist` Uploads CSV files to `historical_upload` directory, especifically the historic data for the DB, you can also access this CSVs in the `historical_data_bkup`, you need to specify a file with this request eg.:
``` bash
curl -X POST -F "file=@hired_employees.csv" http://your-end-point/api/upload_hist
```
- `POST /api/historical_to_db` Update the DB with historical data uploaded through the previous endpoint, takes no arguments eg.:
``` bash
curl -X POST http://your-end-point/api/historical_to_db
```
- `POST /api/batch_insert` Receives a batch transaction in json format, you must indicate the table name to receive the update. Keep in mind that the DB sctructure has constraints, you cannot update a child with foreigns keys missing from its parents, here is a example of usage of this endpoint: 
``` bash
curl -X POST \
  http://your-end-point/api/batch_insert \
  -H 'Content-Type: multipart/form-data' \
  -F 'table_name=departments' \
  -F 'rows=[
        ["13", "Advanced RnD"],
        ["14", "Nuclear Powerplant"]
    ]'
 ```
 - `POST /api/historical_data_bkup_feed` It retrieves the historical data backup from the server, takes no arguments eg.:
 ``` bash
 curl -X POST -F "file=@hired_employees.csv" http://your-end-point/api/historical_data_bkup_feed
 ```
 - `POST /api/upload` Upload a persistent file to Uploads folder, needs to specify a file eg.:
 ``` bash
  curl -X POST -F "file=@hired_employees.csv" http://your-end-point/api/upload
```
- `POST /api/update_db_csv` It takes a local file to update directly the DB, with non-persistency for the file, needs to specify a file eg.:
``` bash
curl -X POST -F "file=@hired_employees.csv" http://your-end-point/api/update_db_csv
```
- `GET /api/ls_uploads` It retrieves a list of files in the uploads folder eg.:
``` bash
curl -X GET http://your-end-point/api/ls_uploads
```
- `POST /api/del_in_uploads` Deletes specific files in the uploads folder, requires a filename as file eg.:
``` bash
curl -X POST -F "file=hired_employees.csv" http://your-end-point/api/del_in_uploads
```
### Endpoints SQL
- `GET /api/sql/hired_over_mean_2021` Query departments with hired employees above mean of the company in json format. To retrieve it in tabulate format you can run `tabulated_hired_over_mean_2021.py` (just change the endpoint there)
``` bash
python ./utils/tabulated_hired_over_mean_2021.py
```
- `GET /api/sql/tabulated_employee_count_by_quarter` Query departments with hired employees above mean of the company in json format. To retrieve it in tabulate format you can run `tabulated_employee_count_by_quarter.py` (just change the endpoint there)
``` bash
python ./utils/tabulated_employee_count_by_quarter.py
```

# Thanks for passing by!
- Feel free to add me in [Linkedin](https://www.linkedin.com/in/-ec-)
