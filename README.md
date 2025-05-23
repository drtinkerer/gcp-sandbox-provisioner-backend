# GCP Sandbox Provisioner Backend

A multi-cloud sandbox management API service with primary focus on Google Cloud Platform (GCP). This service automates the provisioning and management of isolated cloud environments (sandboxes) with built-in support for resource management, billing controls, and IAM configurations.

## Features

- **Multi-Cloud Support**
  - Primary support for Google Cloud Platform
  - Extensible architecture for AWS and Azure integration
  - Configurable provider enablement

- **GCP Capabilities**
  - Automated sandbox environment provisioning
  - Resource management and orchestration
  - Billing management and controls
  - IAM and permissions management
  - Asynchronous task processing

## Tech Stack

- FastAPI (Python web framework)
- Uvicorn ASGI server
- Google Cloud SDK integrations:
  - Resource Manager
  - Cloud Tasks
  - Cloud Billing
  - Cloud Run
  - Cloud IAM

## Project Structure
