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
Steps to Create the Free App Service:
Log in to Azure Portal.
Search for and navigate to App Services.
Click + Create Web App to create a new app service.
Fill in the basic details:
Subscription: Choose your subscription.
Resource Group: Select or create a resource group.
Name: Enter a unique app name.
Publish: Choose Code.
Runtime Stack: Select Python 3.11.
Region: Choose a nearby region.
App Service Plan: Create a new one with Free (F1) tier.
Review and create the app service.
After deployment, access your app via the provided URL in the Overview pane.

## Azure Storage Account Setup
Steps to Create a Storage Account:
Navigate to Storage Accounts in the Azure Portal.
Click + Create.
Fill in the details:
Subscription: Select your subscription.
Resource Group: Select or create a group.
Storage Account Name: Provide a globally unique name.
Region: Choose a region.
Primary Service: Select Azure Blob Storage or Azure Data Lake Storage Gen 2.
Performance: Choose Standard.
Redundancy: Choose Locally-redundant storage (LRS).
Review and create the storage account.
After deployment, create a container:
Name: config (or any name, adjust in code accordingly).
Public Access Level: Choose Private.
Configuration
App Service
Create the following environment variables under Settings > Environment Variables:

AZURE_STORAGE_CONNECTION_STRING: Get it from Storage Account > Access Keys.
CONFIG_DIR="creds"
USER: Your Oracle DB OML User (created in part 1).
PASSWORD: Your Oracle DB OML User password.
DSN: Choose a DSN from your tnsnames.ora.
WALLET_LOCATION="creds"
WALLET_PASSWORD: Password from your wallet (downloaded in ADW Details in part 1).
CONFIG_CONTAINER: Name of the container you created above.
Storage Account
Upload the following files in the container you created:

ewallet.sso
tnsnames.ora
These files can be found in the unzipped wallet from part 1.
