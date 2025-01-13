# Deployment Guide

This guide provides detailed instructions for deploying HealthGuard AI to various cloud platforms.

## AWS Deployment

### Prerequisites

1. AWS Account with necessary permissions
2. AWS CLI installed and configured
3. Docker installed locally
4. ECR repository created

### Step-by-Step Deployment

1. **Build Docker Image**

```bash
# Build the image
docker build -t healthguard-ai .

# Tag the image
docker tag healthguard-ai:latest [AWS_ACCOUNT_ID].dkr.ecr.[REGION].amazonaws.com/healthguard-ai:latest
```

2. **Push to ECR**

```bash
# Authenticate Docker to ECR
aws ecr get-login-password --region [REGION] | docker login --username AWS --password-stdin [AWS_ACCOUNT_ID].dkr.ecr.[REGION].amazonaws.com

# Push the image
docker push [AWS_ACCOUNT_ID].dkr.ecr.[REGION].amazonaws.com/healthguard-ai:latest
```

3. **Create ECS Cluster**

```bash
aws ecs create-cluster --cluster-name healthguard-cluster
```

4. **Create Task Definition**

```json
{
    "family": "healthguard-task",
    "networkMode": "awsvpc",
    "containerDefinitions": [
        {
            "name": "healthguard-container",
            "image": "[AWS_ACCOUNT_ID].dkr.ecr.[REGION].amazonaws.com/healthguard-ai:latest",
            "portMappings": [
                {
                    "containerPort": 8501,
                    "protocol": "tcp"
                }
            ],
            "environment": [
                {
                    "name": "OPENAI_API_KEY",
                    "value": "your-api-key"
                }
            ]
        }
    ],
    "requiresCompatibilities": [
        "FARGATE"
    ],
    "cpu": "256",
    "memory": "512"
}
```

5. **Configure Security Group**

```bash
aws ec2 create-security-group \
    --group-name healthguard-sg \
    --description "Security group for HealthGuard AI"

aws ec2 authorize-security-group-ingress \
    --group-id [SECURITY_GROUP_ID] \
    --protocol tcp \
    --port 8501 \
    --cidr 0.0.0.0/0
```

6. **Create ECS Service**

```bash
aws ecs create-service \
    --cluster healthguard-cluster \
    --service-name healthguard-service \
    --task-definition healthguard-task \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[SUBNET_ID],securityGroups=[SECURITY_GROUP_ID],assignPublicIp=ENABLED}"
```

## Azure Deployment

### Prerequisites

1. Azure Account
2. Azure CLI installed
3. Azure Container Registry (ACR) created

### Deployment Steps

1. **Build and Push to ACR**

```bash
# Build the image
docker build -t healthguard-ai .

# Tag for ACR
docker tag healthguard-ai:latest [ACR_NAME].azurecr.io/healthguard-ai:latest

# Push to ACR
az acr login --name [ACR_NAME]
docker push [ACR_NAME].azurecr.io/healthguard-ai:latest
```

2. **Create Azure Container Instance**

```bash
az container create \
    --resource-group [RESOURCE_GROUP] \
    --name healthguard-container \
    --image [ACR_NAME].azurecr.io/healthguard-ai:latest \
    --dns-name-label healthguard-ai \
    --ports 8501
```

## Google Cloud Platform (GCP)

### Prerequisites

1. GCP Account
2. gcloud CLI installed
3. Container Registry enabled

### Deployment Steps

1. **Build and Push to Container Registry**

```bash
# Build the image
docker build -t healthguard-ai .

# Tag for GCR
docker tag healthguard-ai:latest gcr.io/[PROJECT_ID]/healthguard-ai:latest

# Push to GCR
gcloud auth configure-docker
docker push gcr.io/[PROJECT_ID]/healthguard-ai:latest
```

2. **Deploy to Cloud Run**

```bash
gcloud run deploy healthguard-ai \
    --image gcr.io/[PROJECT_ID]/healthguard-ai:latest \
    --platform managed \
    --region [REGION] \
    --allow-unauthenticated
```

## Environment Variables

Ensure these environment variables are set in your cloud platform:

```
OPENAI_API_KEY=your_openai_api_key
```

## Monitoring and Maintenance

1. **Health Checks**
   - Monitor application logs
   - Set up alerts for errors
   - Track resource usage

2. **Scaling**
   - Configure auto-scaling rules
   - Monitor performance metrics
   - Adjust resource allocation

3. **Updates**
   - Implement CI/CD pipeline
   - Regular security updates
   - Version control

## Troubleshooting

1. **Common Issues**
   - Connection timeouts
   - Memory issues
   - API rate limits

2. **Solutions**
   - Check security group settings
   - Verify environment variables
   - Review application logs

## Security Best Practices

1. Use secrets management
2. Implement HTTPS
3. Regular security audits
4. Access control
5. Data encryption

## Backup and Recovery

1. Database backups
2. Configuration backups
3. Disaster recovery plan
4. Rollback procedures
