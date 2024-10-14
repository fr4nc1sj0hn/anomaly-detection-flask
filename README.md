# Anomaly Detection using ADW Part 2 - Flask Application in Azure

## Table of Contents
- [Tech Stack](#tech-stack)
- [Repository Setup](#repository-setup)
- [Azure App Service Setup](#azure-app-service-setup)
- [Azure Storage Account Setup](#azure-storage-account-setup)
- [Configuration](#configuration)
- [Running the App Locally](#running-the-app-locally)
- [Deployment Pipeline Setup](#deployment-pipeline-setup)
- [Code Explanation](#code-explanation)

## Tech Stack
- Oracle Autonomous Data Warehouse
- Flask
- Plotly.js (for charts)

## Repository Setup
Clone the repository using:

```bash
git clone https://github.com/fr4nc1sj0hn/anomaly-detection-flask.git
```

Or follow the guide for Django apps:
Django App Guide

To rename the main folder, simply rename the directory after cloning.

To push your changes to a new repository:

```bash
git remote remove origin
git remote add <your-repo-url>
git add *
git commit -m "Initial Commit"
git push origin main
```
Note: A /creds/.empty file is included to ensure the folder structure remains intact when pushed to GitHub.

## Azure App Service Setup

- Log in to Azure Portal. Search for and navigate to App Services.
- Click + Create Web App to create a new app service.
- Fill in the basic details:
  
  **Subscription**: Choose your subscription.
  
  **Resource Group**: Select or create a resource group.
  
  **Name**: Enter a unique app name.
  
  **Publish**: Choose Code.
  
  **Runtime** Stack: Select Python 3.11.
  
  **Region**: Choose a nearby region.
  
  **App Service Plan**: Create a new one with Free (F1) tier.
  
- Review and create the app service.
- After deployment, access your app via the provided URL in the Overview pane.

## Azure Storage Account Setup

- Navigate to Storage Accounts in the Azure Portal.
- Click + Create.
- Fill in the details:
  
  **Subscription**: Select your subscription.
  
  **Resource Group**: Select or create a group.
  
  **Storage Account Name**: Provide a globally unique name.
  
  **Region**: Choose a region.
  
  **Primary Service**: Select Azure Blob Storage or Azure Data Lake Storage Gen 2.
  
  **Performance**: Choose Standard.
  
  **Redundancy**: Choose Locally-redundant storage (LRS).
  
- Review and create the storage account.
- After deployment, create a container:
  
  - Navigate to "Containers"
  - In the Storage Account resource page, on the left-hand menu under Data storage, click Containers.
  - Create a New Container
  - In the Containers page, click + Container to create a new container.
  - Configure the Container
    
      **Name**: config (anything as long as you adjust it in the code)
    
      **Public Access Level**: Choose Private (no anonymous access)

## Configuration
### App Service
Create the following environment variables under Settings > Environment Variables:

`AZURE_STORAGE_CONNECTION_STRING`: Get it from Storage Account > Access Keys.

`CONFIG_DIR`="creds"

`USER`: Your Oracle DB OML User (created in part 1).

`PASSWORD`: Your Oracle DB OML User password.

`DSN`: Choose a DSN from your tnsnames.ora.

`WALLET_LOCATION`="creds"

`WALLET_PASSWORD`: Password from your wallet (downloaded in ADW Details in part 1).

`CONFIG_CONTAINER`: Name of the container you created above.

### Storage Account
Upload the following files in the container you created:

`ewallet.sso`

`tnsnames.ora`

These files can be found in the unzipped wallet from part 1.

## Running the App Locally
Before running the app, create a `.env` file and specify the same environment variables from the app service configuration.

To run the app:

- Create a virtual environment:
```bash
python -m venv .venv
.venv\scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the Flask app:
```bash
flask run
```

## Deployment Pipeline Setup
Set up your deployment pipeline in Azure:

- Navigate to App Service > Deployment > Deployment Center.
- Connect your GitHub account and choose the repository. A workflow file will be automatically generated in your repository.

  If you go to actions, you will see that a build-deploy job is initiated. Wait for this to finish and you will be able to browse to your Web App. URL is displayed on the `deploy` step or you can go to Azure portal, browse to your App service and look for the URL.
  This will take a while at first as dependencies are being installed. It is also a Free tier with resources being shared to other users.

- Once the build-deploy job is done, your Flask app will be accessible via <your-app-url>/chart.

## Code Explanation

In Part 1, modify the view to include a consumption_date column incremented by 5 seconds for each row:

```sql
Copy code
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
```

`app.py`

The rest of the code is self explanatory so let me focus on `water_consumption_data`.
this API can be invoked on this route: `/api/water-consumption-data`

To simulate the arrival of new data, a paging mechanism is implemented and is controlled by the JS code which I am going to touch on next. On the 3rd Part of this series, I modified this code to display actual data since there is a function app that inserts data at 5s interval so no need to simulate anything.


`templates/chart.html`

This contains the script for rendering the plotly.js chart.

`generateData` issues an AJAX call which returns 100 rows of data controlled by the page number

`updateChart` renders the chart. The y-axis is limited to 1000 units so that the chart looks static and only the data points move.

Finally, `updateChart` is called every 5000 ms.

In part 3, actual data will be inserted every 5 seconds, so no simulation will be required.
