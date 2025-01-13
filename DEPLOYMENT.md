# Deploying HealthGuard AI

Hey there! 👋 This guide will walk you through deploying HealthGuard AI to your favorite cloud platform. I've tried to make it as straightforward as possible, but if you run into any issues, feel free to open an issue!

## Quick Start with Docker

I've included a Dockerfile to make deployment super easy. Here's how to use it:

```bash
# Build the image
docker build -t healthguard-ai .

# Run it locally
docker run -p 7000:7000 -p 8501:8501 healthguard-ai
```

## Cloud Deployment Options

### AWS (Amazon Web Services)

I personally like using AWS ECS (Elastic Container Service) for this:

1. **Set up AWS CLI**
   ```bash
   aws configure
   ```

2. **Create an ECR repository**
   ```bash
   aws ecr create-repository --repository-name healthguard-ai
   ```

3. **Push your image**
   ```bash
   # Login to ECR
   aws ecr get-login-password --region your-region | docker login --username AWS --password-stdin your-account.dkr.ecr.your-region.amazonaws.com

   # Tag and push
   docker tag healthguard-ai:latest your-account.dkr.ecr.your-region.amazonaws.com/healthguard-ai:latest
   docker push your-account.dkr.ecr.your-region.amazonaws.com/healthguard-ai:latest
   ```

4. **Launch on ECS**
   - Create a cluster (or use an existing one)
   - Create a task definition using your ECR image
   - Launch a service with your desired configuration

### Azure

Azure Container Apps makes this really simple:

1. **Install Azure CLI and login**
   ```bash
   az login
   ```

2. **Create a resource group**
   ```bash
   az group create --name healthguard-group --location eastus
   ```

3. **Create a container registry**
   ```bash
   az acr create --resource-group healthguard-group --name yourregistryname --sku Basic
   az acr login --name yourregistryname
   ```

4. **Push and deploy**
   ```bash
   # Tag and push
   docker tag healthguard-ai:latest yourregistryname.azurecr.io/healthguard-ai:latest
   docker push yourregistryname.azurecr.io/healthguard-ai:latest

   # Deploy to Container Apps
   az containerapp create \
     --name healthguard-ai \
     --resource-group healthguard-group \
     --image yourregistryname.azurecr.io/healthguard-ai:latest
   ```

### Google Cloud Platform (GCP)

Cloud Run is perfect for this kind of application:

1. **Set up gcloud CLI**
   ```bash
   gcloud init
   gcloud auth configure-docker
   ```

2. **Tag and push your image**
   ```bash
   docker tag healthguard-ai:latest gcr.io/your-project/healthguard-ai:latest
   docker push gcr.io/your-project/healthguard-ai:latest
   ```

3. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy healthguard-ai \
     --image gcr.io/your-project/healthguard-ai:latest \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

## Environment Variables

Don't forget to set these in your cloud provider's environment configuration:
- `OPENAI_API_KEY`: Your OpenAI API key
- `PORT`: The port for the FastAPI server (default: 7000)
- `STREAMLIT_PORT`: The port for the Streamlit UI (default: 8501)

## SSL/TLS Configuration

I recommend setting up SSL for production. Each cloud provider has their own way:
- AWS: Use Application Load Balancer with ACM
- Azure: Enable managed certificates in Container Apps
- GCP: Cloud Run handles this automatically

## Monitoring

I've found these monitoring solutions work well:
- AWS: CloudWatch
- Azure: Application Insights
- GCP: Cloud Monitoring

## Need Help?

If you run into any issues:
1. Check the container logs in your cloud provider's console
2. Make sure all environment variables are set correctly
3. Verify network/firewall settings allow the necessary ports
4. Open an issue if you're still stuck!
