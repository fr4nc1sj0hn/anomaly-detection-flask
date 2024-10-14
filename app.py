import os

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, jsonify)
from dotenv import load_dotenv
import oracledb

app = Flask(__name__)


load_dotenv()

base_dir = os.path.dirname(os.path.abspath(__file__))
config_dir = os.path.join(base_dir, os.getenv("config_dir"))
wallet_location = os.path.join(base_dir, os.getenv("wallet_location"))
pem_content = os.getenv("pem_content")
tns = os.getenv("tns")

print("base_dir:", base_dir)
print("config_dir:", config_dir)
print("pem_content:", pem_content)
print("wallet_location:", wallet_location)

with open('./creds/ewallet.pem', 'w') as pem_file:
    pem_file.write(pem_content)

with open('./creds/tnsnames.ora', 'w') as pem_file:
    pem_file.write(tns)

# Database connection function
def get_db_connection():
    return oracledb.connect(
         config_dir=  config_dir,
         user=os.getenv("user"),
         password=os.getenv("password"),
         dsn="pocdev_high",
         wallet_location=wallet_location,
         wallet_password=os.getenv("wallet_password")
    )

@app.route('/api/water-consumption-data', methods=['GET'])

def water_consumption_data():
    try:
        # Get the page number from the query parameters (default to 0 for the first page)
        page = int(request.args.get('page', 0))
        offset = page  # Set offset to the page number

        # Connect to the database
        connection = get_db_connection()
        print(connection)
        
        cursor = connection.cursor()

        sql = f"""
        SELECT CONSUMPTION_DATE, WATER_CONSUMPTION, STATUS 
        FROM water_consumption_data_v
        ORDER BY CONSUMPTION_DATE ASC
        OFFSET {offset} ROWS FETCH NEXT 100 ROWS ONLY
        """
        # Query data from the Oracle DB view
        cursor.execute(sql)

        # Fetch data
        rows = cursor.fetchall()

        # Structure the data to send as JSON
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


# Flask route to fetch data from the Oracle DB view
@app.route('/fetch-view-data', methods=['GET'])
def fetch_view_data():
    try:
        # Get database connection
        connection = get_db_connection()
        cursor = connection.cursor()

        # Execute query on the Oracle DB view
        cursor.execute("SELECT * FROM water_consumption_data_v")

        # Fetch all rows from the view
        rows = cursor.fetchall()

        # Get column names
        columns = [col[0] for col in cursor.description]

        # Format rows into list of dictionaries
        data = [dict(zip(columns, row)) for row in rows]

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
