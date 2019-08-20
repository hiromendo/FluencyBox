Fluency Box API Setup

Getting Started
This application has been created using : 
1) Python - Flask Framework 
2) MYSSQL Database

We shall use a virtual environment. To install the virtual environment use the below command on the terminal:

Windows : pip install virtualenv
Mac : pip3 install virtualenv

Create a virtual environment - the one used to develop this project is called "env".
To create a virtual environment, run the below command:
virtualenv Env_Name

where Env_Name is the name of your environment
Activate the virtual enviroment by navigating to "Env_Name\Scripts\" then invoking the activate file.
Run the Requirements.txt file located in this folder in the virtual environment to ensure the necessary packages are installed. Run the below command to achieve this (ensure you are in the correct directory - same as the Requirements.txt):

pip install -r Requirements.txt

Prerequisites
To run this application, you'll require Python version 3.x and MYSQL installed on your machine.
This application requires the Flask Framework, SQL Alchemy and the MYSQL package to be installed to be able to run. Other dependancies needed are included in the file.
The above mentioned Requirements.txt file will install the necessary packages.

Setting Up the Database
Create a Database called "fluencyboxdb" in MYSQL.
Import the file called "fluencyboxdb.sql" (located in this folder). 
This will create the table necessary to run this application.
This will also insert sample records.

The MYSQL connection settings are located in the config.py file"
Replace the values for the "SQLALCHEMY_DATABASE_URI" key.
Change the above parameters in the config.py file to match with your host settings.

Running the application
Once the above has been setup, to run the application, navigate to the main folder where "api.py" is located and run the below command:

Windows command : python api.py
Mac command : python3 api.py

This will create the server and you will be able to access the application on http://127.0.0.1:5000/

To get a JWT Token navigate to the /login route (http://127.0.0.1:5000/login) and it will ask for an email and password (authorization). Use the below:
email : sanjay@hotmail.com
password : 12345

You will then receive a token that you will enter in the header for every subsequent request. Header value should be : x-access-token
