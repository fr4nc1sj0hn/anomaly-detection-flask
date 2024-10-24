# Anomaly Detection using ADW Part 2 - Flask Application in Azure

Tech Stack:
- Oracle Autonomous Data Warehouse
- Flask
- Plotly.js (for the chart)


Follow the Following Steps

Clone this repository using 

git clone https://github.com/fr4nc1sj0hn/anomaly-detection-flask.git

or you can follow the guide here: 
* Django [https://github.com/Azure-Samples/msdocs-python-django-webapp-quickstart](https://github.com/Azure-Samples/msdocs-python-django-webapp-quickstart)

Once you cloned the repository and you want to have a different repository name, just rename the main folder.

To push your changes to an empty repository,

- git remote remove origin
- git remote add "your-repo"

commit and push your changes
- git add *
- git commit -m "Initial Commit"
- git push origin main


A file /creds/.empty is created so that the folder `creds` is added to the project structure when pushed to GitHub.



Create a Free App Service in Azure

Steps to Create the Free App Service:
1. Log in to Azure Portal
Go to the Azure Portal and log in using your Azure account.
2. Navigate to "App Services"
In the search bar at the top of the portal, type App Services and select it from the dropdown menu.
3. Create a New App Service
In the App Services window, click the + Create Web App button to create a new app service.

4. Configure the Basics
Subscription: Select your Azure subscription.
Resource Group: Select an existing resource group or create a new one by clicking "Create new" and providing a name.
Name: Enter a unique name for your app. T

Publish: Choose Code since you'll be deploying a Python application.
Runtime Stack: Select Python 3.11 from the dropdown.
Region: Choose a region closest to you.

App Service Plan: Click on Create new, name the plan, and choose Free (F1) pricing tier to stay within the free service limit.
5. Review and Create
Click Next: Deployment (skip this if you're not using any specific deployment options like GitHub actions).
Then click Review + Create to review your selections.
Click Create to provision the app service. This will take a few moments.

6. Wait for Deployment to Complete
Once the deployment is complete, you’ll see a notification. Click Go to resource to view your newly created app service.

7. Access Your App
Once deployed, you can access your app via the URL specified in the Overview pane of your App service.

Steps to Create a Storage Account:
1. Log in to Azure Portal
Go to the Azure Portal and sign in with your Azure account.
2. Navigate to "Storage Accounts"
In the search bar at the top of the portal, type Storage Accounts and select it from the dropdown list.
3. Create a New Storage Account
In the Storage Accounts page, click the + Create button to start the creation process.
4. Configure the Storage Account Basics
Subscription: Choose your Azure subscription.
Resource Group: Select an existing resource group or create a new one by clicking "Create new".
Storage Account Name: Enter a globally unique name for the storage account (this name will be part of the URL).
Region: Choose a region where you want to deploy the storage account (closer to your users or application).
Primary Service: Choose Azure Blob Storage or Azure Data Lake Storage Gen 2
Primary Workload: Choose Cloud Native

Performance: Choose Standard

Redundancy: Choose a Locally-redundant storage (LRS)

5. Review and Create
After configuring the basics, click Review + Create to verify your settings.
Once verified, click Create to deploy the storage account.
6. Wait for Deployment
Wait for the deployment to complete, and then click Go to resource to open your new storage account.

Steps to Create a Container:
1. Navigate to "Containers"
In the Storage Account resource page, on the left-hand menu under Data storage, click Containers.
2. Create a New Container
In the Containers page, click + Container to create a new container.
3. Configure the Container
Name: config (anything as long as you adjust it in the code)
Public Access Level: Choose Private (no anonymous access)

4. Create the Container
Click Create to finalize the container setup.


Configuration

App service
Create the following Environment Variables Under Settings > Environment Variables

AZURE_STORAGE_CONNECTION_STRING: Get this from your Storage Account under Security and networking > Access Keys and use any of the provided connection strings.

CONFIG_DIR="creds"
USER: Your Oracle DB OML User Created in part 1 of this series 
PASSWORD: Your Oracle DB OML User Password
DSN: Check your tnsnames.ora and choose any of the available dsn
WALLET_LOCATION="creds"
WALLET_PASSWORD: password of the Wallet you downloaded in the ADW Details page in Part 1
CONFIG_CONTAINER: the container name you created above

Storage Account
Upload the following files in the container you created.
	- ewallet.sso
	- tnsnames.ora

These files can be found on the unzipped wallet in part 1.



Before running the app locally, 

create a `.env` file and specify the following environment variables which matches those you setup in the App Service.

Create a virtual environment
python -m venv .venv #or whatever name you want
.venv\scripts\activate
pip install -r requirements.txt
flask run



AZURE_STORAGE_CONNECTION_STRING: Get this from your Storage Account under Security and networking > Access Keys and use any of the provided connection strings.

CONFIG_DIR="creds"
USER: Your Oracle DB OML User Created in part 1 of this series 
PASSWORD: Your Oracle DB OML User Password
DSN: Check your tnsnames.ora and choose any of the available dsn
WALLET_LOCATION="creds"
WALLET_PASSWORD: password of the Wallet you downloaded in the ADW Details page in Part 1
CONFIG_CONTAINER: the container name you created above



Setup your deployment pipeline

On your App Service go to Deployment > Deployment Center to setup your deployment settings. You can connect your GitHub account and choose the Repository where you pushed the Flask App code.


A workflow file will be automatically generated on your repository.

If you go to actions, you will see that a build-deploy job is initiated. Wait for this to finish and you will be able to browse to your Web App. URL is displayed on the `deploy` step or you can go to Azure portal, browse to your App service and look for the URL.

This will take a while at first as dependencies are being installed. It is also a Free tier with resources being shared to other users.


Once the build and deploy job is done, you can browse your flask app and see the chart via 
<your-app-url>/chart


Code Explanation

The view we created in Part 1 needs to get modified to add a consumption_date column which is incremented by 5 seconds each row. This is modified in part 3 when we have an actual function app that inserts data every 5s.

CREATE OR REPLACE VIEW water_consumption_data_v AS
SELECT a.*, 
       CASE WHEN prob_anomalous > 0.8 THEN 'Anomaly' ELSE 'Normal' END AS Status,
       SYSTIMESTAMP + (ROWNUM - 1) * INTERVAL '5' SECOND AS consumption_date
FROM (
    SELECT 
        ID,
        TIME_OF_DAY, 
        SEASON,
        TEMPERATURE,
        HOUSEHOLD_SIZE,
        DAY_OF_WEEK,
        WATER_CONSUMPTION, 
        prediction_probability(WATER_ANOMALY_AD, '0' USING *) prob_anomalous
    FROM water_consumption_data
    ORDER BY ID
) a;



`app.py`

The rest of the code is self explanatory so let me focus on `water_consumption_data`.
this API can be invoked on this route: `/api/water-consumption-data`

To simulate the arrival of new data, a paging mechanism is implemented and is controlled by the JS code which I am going to touch on next.

In the 3rd Part of this series, I modified this code to display actual data since there is a function app that inserts data at 5s interval so no need to simulate anything.


`templates\chart.html`

This contains the script for rendering the plotly.js chart.

`generateData` issues an AJAX call which returns 100 rows of data controlled by the page number

`updateChart` renders the chart. The y-axis is limited to 1000 units so that the chart looks static and only the data points move.

Finally, `updateChart` is called every 5000 ms.


