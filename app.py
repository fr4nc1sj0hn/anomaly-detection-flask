import os
from azure.storage.blob import BlobServiceClient

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, jsonify)
from dotenv import load_dotenv
import oracledb

app = Flask(__name__)


load_dotenv()

# Define base directories and file paths
base_dir = os.path.dirname(os.path.abspath(__file__))
config_dir = os.path.join(base_dir, os.environ.get("CONFIG_DIR"))
wallet_location = os.path.join(base_dir, os.environ.get("WALLET_LOCATION"))

# Local directory for storing downloaded files
creds_dir = os.path.join(base_dir, 'creds')

# Ensure creds directory exists
if not os.path.exists(creds_dir):
    os.makedirs(creds_dir)

# Define the paths for 'ewallet.pem' and 'tnsnames.ora'
pem_path = os.path.join(creds_dir, 'ewallet.pem')
tns_path = os.path.join(creds_dir, 'tnsnames.ora')

def download_wallet_files():
    try:
        # Initialize the BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_STORAGE_CONNECTION_STRING"))
        
        files_to_download = [
            {"blob": "ewallet.pem", "local": pem_path},
            {"blob": "tnsnames.ora", "local": tns_path}
        ]
        
        # Container name in Azure Blob Storage
        container_name = os.getenv("CONFIG_CONTAINER")

        # Loop through and download each file
        for file_info in files_to_download:
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_info["blob"])
            

            # Download the file and save it locally
            with open(file_info["local"], "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
                
            print(f"Downloaded {file_info['blob']} to {file_info['local']}")
    
    except Exception as e:
        print(f"Error downloading files from Azure Blob Storage: {str(e)}")

def get_db_connection():
    try:
        # Download wallet files from Azure Blob Storage

        # Establish the Oracle DB connection
        connection = oracledb.connect(
            config_dir=config_dir,
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            dsn=os.getenv("DSN"),
            wallet_location=wallet_location,
            wallet_password=os.getenv("WALLET_PASSWORD")
        )
        return connection
    except oracledb.DatabaseError as e:
        # Log error and provide feedback
        error, = e.args
        print(f"Error connecting to the database: {error.message}")
        return None

download_wallet_files()

@app.route('/api/water-consumption-data', methods=['GET'])
def water_consumption_data():
    try:
        # Get the page number from the query parameters (default to 0 for the first page)
        page = int(request.args.get('page', 0))
        offset = page  # Set offset to the page number

        # Connect to the database
        connection = get_db_connection()

        cursor = connection.cursor()

        sql = f"""
        SELECT CONSUMPTION_DATE, WATER_CONSUMPTION, STATUS 
        FROM water_consumption_data_v
        ORDER BY CONSUMPTION_DATE ASC
        OFFSET {offset} ROWS FETCH NEXT 100 ROWS ONLY
        """

        cursor.execute(sql)
        rows = cursor.fetchall()

        data = {
            'xValues': [row[0].isoformat() for row in rows],  # Using CONSUMPTION_DATE column
            'yValues': [row[1] for row in rows],
            'statuses': [row[2] for row in rows]  # Adding STATUS column
        }

        return jsonify(data)

    except oracledb.DatabaseError as e:
        error, = e.args
        return jsonify({'error': str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')


@app.route('/chart')
def chart():
   print('Request for index page received')
   return render_template('chart.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()
