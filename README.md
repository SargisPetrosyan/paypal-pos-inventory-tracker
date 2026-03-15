# Inventory Tracker Deployment Guide

## Build Docker Image

```bash
docker build --platform=linux/amd64 -t <your-image-name> .
```

## Tag Docker Image

```bash
docker tag <your-image-name> <your-dockerhub-username>/<your-repository-name>:latest
```

## Push Docker Image

```bash
docker push <your-dockerhub-username>/<your-repository-name>:latest
```

## Deploy to Azure Container Instance

```bash
az container create --resource-group <your-resource-group> --file deploy-secure-aci.yaml
```

## Delete Azure Container Instance

To delete your deployed container instance, run:

```bash
az container delete --name <your-container-name> --resource-group <your-resource-group> --yes
```

## Attach to Azure Container Instance Logs

To view logs and attach to your running container instance, run:

```bash
        az containerapp create -n my-containerapp -g MyResourceGroup \
            --environment MyContainerappEnv \
            --yaml "path/to/yaml/file.yml"
```

---

**Note:**
- Replace all placeholders (e.g., `<your-image-name>`, `<your-dockerhub-username>`, `<your-repository-name>`, `<your-resource-group>`) with your actual project names.
- Make sure your Azure resource group and Docker Hub repository match these names.

docker build --platform linux/amd64 -t sargispetrosyan/paypal-inventory-tracker .


az containerapp show -n paypal-container -g paypal -o yaml > app.yaml

az containerapp update --name paypal-container --resource-group paypal  \
    --yaml app.yaml
