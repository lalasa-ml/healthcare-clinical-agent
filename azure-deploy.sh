#!/bin/bash

# Define variables
RESOURCE_GROUP="rg-healthcare-agent"
LOCATION="eastus"
ACR_NAME="acrhealthcareagent"
APP_SERVICE_PLAN="plan-healthcare-agent"
WEB_APP_NAME="app-healthcare-agent-api"

# 1. Create Resource Group
az group create --name $RESOURCE_GROUP --location $LOCATION

# 2. Create Azure Container Registry (ACR)
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true

# 3. Build and Push Docker Image to ACR
az acr build --registry $ACR_NAME --image healthcare-agent:v1 .

# 4. Create App Service Plan (Linux)
az appservice plan create --name $APP_SERVICE_PLAN --resource-group $RESOURCE_GROUP --sku B1 --is-linux

# 5. Create Web App for Containers & Deploy
az webapp create --resource-group $RESOURCE_GROUP \
                 --plan $APP_SERVICE_PLAN \
                 --name $WEB_APP_NAME \
                 --deployment-container-image-name $ACR_NAME.azurecr.io/healthcare-agent:v1