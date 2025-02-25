# Deployment Guide

This document provides a step-by-step guide to deploying the project using Infrastructure as Code (IaC). The entire environment is provisioned using Google Cloud Platform (GCP) and Terraform, ensuring reproducibility and maintainability.

## Prerequisites

Ensure you have the following tools installed:
- Google Cloud SDK (`gcloud`) – CLI for interacting with GCP.
- Terraform – Infrastructure as Code tool for provisioning resources.

## Deployment Steps

### 1️⃣ Set Project ID

```sh
set PROJECT_ID=prj-tg-portfolio-00000
```
This command defines the project ID that will be used in subsequent steps. The project ID should be unique across GCP.

### 2️⃣ Create the GCP Project

```sh
gcloud projects create %PROJECT_ID%
```
This command creates a new project in GCP with the specified `PROJECT_ID`.

### 3️⃣ Retrieve Billing Account ID

```sh
gcloud billing accounts list
```
This lists all billing accounts available in the organization. You need to select a billing account and store it in the `BILLING_ACCOUNT` variable in the next step.

### 4️⃣ Link Billing Account to Project

```sh
set BILLING_ACCOUNT=<YOUR_BILLING_ACCOUNT_ID>

gcloud billing projects link %PROJECT_ID% --billing-account=%BILLING_ACCOUNT%
```
This links the newly created GCP project to a billing account, enabling it to provision resources.

### 5️⃣ Set Active Project

```sh
gcloud config set project %PROJECT_ID%
```
This sets the active project in the GCP CLI to ensure all subsequent commands apply to the correct project.

### 6️⃣ Initialize Terraform

```sh
cd ./streaming_pipeline/infra/terraform

terraform init
```
This initializes Terraform, downloading required providers and setting up the working directory.

### 7️⃣ Deploy API Module

```sh
terraform plan -target=module.apis
terraform apply -target=module.apis -auto-approve
```
These commands deploy only the API module of the infrastructure. The `-target=module.apis` ensures that only this specific module is planned and applied, allowing incremental provisioning.

### 8️⃣ Deploy Full Infrastructure

```sh
terraform plan
terraform apply
```
This deploys the entire infrastructure, including APIs, Cloud Run, Data Lakes, and any other defined modules. The `-auto-approve` flag prevents manual confirmation prompts.

### 9 Deploy Dataflow

```sh
python portfolio\streaming_pipeline\infra\modules\dataflow\dataflow_pubsub_to_gcs.py --runner=DataflowRunner
```
This command deploys the Dataflow job to process the streaming data from Pub/Sub and write it to GCS.

## ✅ Summary
By following these steps, you will:
- Create a GCP project and link it to a billing account.
- Initialize and apply Terraform to provision infrastructure.
- Deploy an API module separately, if needed.

This approach ensures the entire deployment process is automated, making it easy to replicate across different environments. 🚀