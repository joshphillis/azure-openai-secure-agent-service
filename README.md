\# Azure OpenAI Secure Agent Service



\# 🚀 Azure OpenAI Secure Agent Mesh  

\*A fully containerized, multi‑agent microservice mesh built with FastAPI, Docker, Azure Container Apps, and Azure OpenAI.\*



\---



\# 📘 Overview



This project implements a \*\*secure fan‑out/fan‑in microservice mesh\*\* where:



\- An \*\*orchestrator\*\* receives a request  

\- It distributes work across \*\*five worker agents\*\*  

\- Each worker independently calls \*\*Azure OpenAI\*\*  

\- The orchestrator aggregates results and returns a unified response  



This README is a \*\*complete, end‑to‑end guide\*\* that includes:



\- All required setup  

\- All Azure configuration  

\- All Docker configuration  

\- All VS Code workflow steps  

\- All debugging steps  

\- All operational guidance  

\- All architecture rationale  

\- All security model details  

\- All troubleshooting we performed  

\- A “What I Learned” section  



This is the \*\*authoritative guide\*\* for deploying and operating this system.



\---



\# 📁 Repository Structure



```

azure-openai-secure-agent-service/

├── orchestrator/

│   ├── main.py

│   ├── Dockerfile

│   └── requirements.txt

│

├── worker/

│   ├── main.py

│   ├── Dockerfile

│   └── requirements.txt

│

└── README.md

```



\---



\# 🧠 Architecture



```mermaid

flowchart LR

&#x20;   Client --> Orchestrator

&#x20;   Orchestrator --> W1\[Worker 1]

&#x20;   Orchestrator --> W2\[Worker 2]

&#x20;   Orchestrator --> W3\[Worker 3]

&#x20;   Orchestrator --> W4\[Worker 4]

&#x20;   Orchestrator --> W5\[Worker 5]

&#x20;   W1 --> AOAI\[Azure OpenAI]

&#x20;   W2 --> AOAI

&#x20;   W3 --> AOAI

&#x20;   W4 --> AOAI

&#x20;   W5 --> AOAI

```



\### 🔄 Flow Summary

1\. Client sends request to orchestrator  

2\. Orchestrator fans out to 5 workers  

3\. Each worker calls Azure OpenAI  

4\. Workers return results  

5\. Orchestrator aggregates and responds  



\---



\# 🧰 Prerequisites



\### Local Tools

\- Azure CLI  

\- Docker Desktop  

\- Visual Studio Code  

\- Git  

\- Python 3.10+ (optional)



\### Azure Resources

\- Azure OpenAI  

\- Azure Container Registry  

\- Azure Container Apps  

\- Log Analytics Workspace  



\---



\# 1️⃣ Azure CLI Login \& Subscription Setup



\### Login

```powershell

az login

```



\### Verify account

```powershell

az account show

```



\### Select subscription

```powershell

az account set --subscription "<your-subscription-id>"

```



\### Install required extensions

```powershell

az extension add --name containerapp --upgrade

az extension add --name containerregistry --upgrade

az extension add --name monitor --upgrade

az extension add --name cognitiveservices --upgrade

```



\---



\# 2️⃣ Clone the Repository



```powershell

git clone https://github.com/joshphillis/azure-openai-secure-agent-service.git

cd azure-openai-secure-agent-service

```



\---



\# 🐳 3️⃣ Start Docker Desktop (Required)



Before building or running containers:



1\. Open \*\*Docker Desktop\*\*  

2\. Wait for \*\*Docker Engine is running\*\*  

3\. Verify:



```powershell

docker info

docker context ls

```



If Docker is not running, nothing will build or run.



\---



\# 💻 4️⃣ Open VS Code \& Use the Integrated Terminal



All commands in this README assume:



\*\*Visual Studio Code → Terminal → PowerShell\*\*



\### Steps

1\. Open VS Code  

2\. File → Open Folder → `azure-openai-secure-agent-service/`  

3\. Terminal → New Terminal  

4\. Ensure terminal is \*\*PowerShell\*\*  



\---



\# 5️⃣ Set Required Environment Variables



```powershell

$env:AZURE\_OPENAI\_ENDPOINT="https://<your-endpoint>.openai.azure.com/"

$env:AZURE\_OPENAI\_API\_KEY="<your-azure-openai-key>"

$env:AZURE\_OPENAI\_DEPLOYMENT="<your-model-deployment-name>"



$env:WORKER\_API\_KEY="<shared-worker-api-key>"

$env:ORCHESTRATOR\_API\_KEY="<orchestrator-api-key>"

```



\### Verify variables

```powershell

gci env:AZURE\_OPENAI\_ENDPOINT

gci env:WORKER\_API\_KEY

```



\---



\# 6️⃣ Local Development (Optional)



\## Build Images

```powershell

docker build -t local-orchestrator ./orchestrator

docker build -t local-worker ./worker

```



\## Run Worker

```powershell

docker run -p 8001:8000 `

&#x20; -e AZURE\_OPENAI\_ENDPOINT=$env:AZURE\_OPENAI\_ENDPOINT `

&#x20; -e AZURE\_OPENAI\_API\_KEY=$env:AZURE\_OPENAI\_API\_KEY `

&#x20; -e AZURE\_OPENAI\_DEPLOYMENT=$env:AZURE\_OPENAI\_DEPLOYMENT `

&#x20; -e WORKER\_API\_KEY=$env:WORKER\_API\_KEY `

&#x20; local-worker

```



\## Run Orchestrator

```powershell

docker run -p 8000:8000 `

&#x20; -e ORCHESTRATOR\_API\_KEY=$env:ORCHESTRATOR\_API\_KEY `

&#x20; -e WORKER\_API\_KEY=$env:WORKER\_API\_KEY `

&#x20; -e WORKER\_URLS="http://host.docker.internal:8001" `

&#x20; local-orchestrator

```



\## Test Worker Directly

```powershell

Invoke-WebRequest -Uri "http://localhost:8001/summarize" `

&#x20; -Method POST `

&#x20; -Headers @{ "x-api-key" = $env:WORKER\_API\_KEY } `

&#x20; -Body '{"text": "hello"}'

```



\## Test Orchestrator

Open:



```

http://localhost:8000/docs

```



\---



\# 7️⃣ Create Azure Resource Group



```powershell

az group create `

&#x20; --name agent-mesh-rg `

&#x20; --location eastus

```



\---



\# 8️⃣ Create Azure OpenAI Resource + Deployment



```powershell

az cognitiveservices account create `

&#x20; --name openai-joshua-foundry `

&#x20; --resource-group agent-mesh-rg `

&#x20; --kind OpenAI `

&#x20; --sku S0 `

&#x20; --location eastus `

&#x20; --custom-domain openai-joshua-foundry

```



Then in the Azure Portal:



1\. Open \*\*openai-joshua-foundry\*\*  

2\. Go to \*\*Deployments\*\*  

3\. Deploy \*\*GPT‑4o‑mini\*\*  

4\. Copy: endpoint, API key, deployment name  



\---



\# 9️⃣ Create Azure Container Registry



```powershell

az acr create `

&#x20; --resource-group agent-mesh-rg `

&#x20; --name agentmeshacr `

&#x20; --sku Basic `

&#x20; --location eastus

```



\### Login to ACR

```powershell

az acr login --name agentmeshacr

docker login agentmeshacr.azurecr.io

```



\---



\# 🔟 Build \& Push Images to ACR



\### Orchestrator

```powershell

cd orchestrator

docker build -t agentmeshacr.azurecr.io/summaries-orchestrator:latest .

docker push agentmeshacr.azurecr.io/summaries-orchestrator:latest

cd ..

```



\### Worker

```powershell

cd worker

docker build -t agentmeshacr.azurecr.io/summaries-worker:latest .

docker push agentmeshacr.azurecr.io/summaries-worker:latest

cd ..

```



\---



\# 1️⃣1️⃣ Create Log Analytics + Container Apps Environment



```powershell

$LOG\_WS\_NAME="workspace-agentmeshrgVgQ8"



az monitor log-analytics workspace create `

&#x20; --resource-group agent-mesh-rg `

&#x20; --workspace-name $LOG\_WS\_NAME `

&#x20; --location eastus



$LOG\_WS\_ID=$(az monitor log-analytics workspace show `

&#x20; --resource-group agent-mesh-rg `

&#x20; --workspace-name $LOG\_WS\_NAME `

&#x20; --query id -o tsv)



az containerapp env create `

&#x20; --name agent-mesh-env `

&#x20; --resource-group agent-mesh-rg `

&#x20; --location eastus `

&#x20; --logs-workspace-id $LOG\_WS\_ID

```



\---



\# 1️⃣2️⃣ Deploy Worker Container Apps



\### Deploy 5 Workers

```powershell

foreach ($i in @("", "-2", "-3", "-4", "-5")) {

&#x20; az containerapp create `

&#x20;   --name "summaries-worker$i" `

&#x20;   --resource-group agent-mesh-rg `

&#x20;   --environment agent-mesh-env `

&#x20;   --image agentmeshacr.azurecr.io/summaries-worker:latest `

&#x20;   --target-port 8000 `

&#x20;   --ingress external `

&#x20;   --env-vars `

&#x20;     AZURE\_OPENAI\_ENDPOINT=$env:AZURE\_OPENAI\_ENDPOINT `

&#x20;     AZURE\_OPENAI\_API\_KEY=$env:AZURE\_OPENAI\_API\_KEY `

&#x20;     AZURE\_OPENAI\_DEPLOYMENT=$env:AZURE\_OPENAI\_DEPLOYMENT `

&#x20;     WORKER\_API\_KEY=$env:WORKER\_API\_KEY

}

```



\### Set minReplicas = 1

```powershell

foreach ($i in @("", "-2", "-3", "-4", "-5")) {

&#x20; az containerapp update `

&#x20;   --name "summaries-worker$i" `

&#x20;   --resource-group agent-mesh-rg `

&#x20;   --min-replicas 1

}

```



\### Collect Worker URLs

```powershell

foreach ($i in @("", "-2", "-3", "-4", "-5")) {

&#x20; az containerapp show `

&#x20;   --name "summaries-worker$i" `

&#x20;   --resource-group agent-mesh-rg `

&#x20;   --query properties.configuration.ingress.fqdn -o tsv

}

```



\---



\# 1️⃣3️⃣ Deploy the Orchestrator



Set worker URLs:



```powershell

$env:WORKER\_URLS="https://summaries-worker.<fqdn>,https://summaries-worker-2.<fqdn>,https://summaries-worker-3.<fqdn>,https://summaries-worker-4.<fqdn>,https://summaries-worker-5.<fqdn>"

```



Deploy:



```powershell

az containerapp create `

&#x20; --name summaries-orchestrator `

&#x20; --resource-group agent-mesh-rg `

&#x20; --environment agent-mesh-env `

&#x20; --image agentmeshacr.azurecr.io/summaries-orchestrator:latest `

&#x20; --target-port 8000 `

&#x20; --ingress external `

&#x20; --env-vars `

&#x20;   ORCHESTRATOR\_API\_KEY=$env:ORCHESTRATOR\_API\_KEY `

&#x20;   WORKER\_API\_KEY=$env:WORKER\_API\_KEY `

&#x20;   WORKER\_URLS=$env:WORKER\_URLS

```



\---



\# 1️⃣4️⃣ Test the Mesh



\### Swagger UI

```

https://summaries-orchestrator.<fqdn>/docs

```



\### PowerShell

```powershell

Invoke-WebRequest -Uri "https://summaries-orchestrator.<fqdn>/summarize" `

&#x20; -Method POST `

&#x20; -Headers @{ 

&#x20;     "x-api-key" = $env:ORCHESTRATOR\_API\_KEY

&#x20;     "Content-Type" = "application/json"

&#x20; } `

&#x20; -Body '{"text": "This is a sample document that will be summarized by multiple workers."}'

```



\---



\# 🛠️ Debugging \& Troubleshooting



\## Check logs

```powershell

az containerapp logs show `

&#x20; --name summaries-worker `

&#x20; --resource-group agent-mesh-rg `

&#x20; --follow

```



\## Exec into container

```powershell

az containerapp exec `

&#x20; --name summaries-worker `

&#x20; --resource-group agent-mesh-rg `

&#x20; --command "printenv"

```



\## Common Issues



\### ❌ ACR push fails  

Fix:

```powershell

az acr login --name agentmeshacr

docker login agentmeshacr.azurecr.io

```



\### ❌ Worker returns 401  

Cause: wrong API key  

Fix: ensure orchestrator uses WORKER\_API\_KEY



\### ❌ Orchestrator cannot reach workers  

Fix: ensure workers have \*\*external ingress\*\*



\### ❌ Cold starts  

Fix: set `--min-replicas 1`



\### ❌ Timeout issues  

Fix: orchestrator uses:

```python

httpx.AsyncClient(timeout=60.0)

```



\---



\# 🧭 Operational Guidance



\## Redeploy updated images

```powershell

docker build -t agentmeshacr.azurecr.io/summaries-orchestrator:latest .

docker push agentmeshacr.azurecr.io/summaries-orchestrator:latest



az containerapp update `

&#x20; --name summaries-orchestrator `

&#x20; --resource-group agent-mesh-rg `

&#x20; --image agentmeshacr.azurecr.io/summaries-orchestrator:latest

```



\## Restart a worker

```powershell

az containerapp restart `

&#x20; --name summaries-worker `

&#x20; --resource-group agent-mesh-rg

```



\## Scale workers

```powershell

az containerapp update `

&#x20; --name summaries-worker `

&#x20; --resource-group agent-mesh-rg `

&#x20; --min-replicas 3

```



\---



\# 🧩 Architecture Rationale



\### Why FastAPI?

\- Lightweight  

\- Async‑friendly  

\- Perfect for distributed microservices  



\### Why httpx.AsyncClient?

\- True async  

\- Parallel fan‑out  

\- Timeout control  



\### Why 5 workers?

\- Demonstrates horizontal scaling  

\- Predictable fan‑out pattern  



\### Why Container Apps?

\- Serverless containers  

\- Autoscaling  

\- Simpler than AKS  



\### Why ACR?

\- Private  

\- Secure  

\- Azure‑native  



\---



\# 🔐 Security Model



\### Worker API Key

\- Protects workers from public misuse  

\- Only orchestrator should call workers  



\### Orchestrator API Key

\- Protects orchestrator from public misuse  



\### Azure OpenAI Key

\- Never exposed to clients  

\- Only workers use it  



\### Zero Trust Between Components

\- Workers do not trust clients  

\- Orchestrator does not trust the internet  



\---



\# 🧹 Cleanup



```powershell

az group delete `

&#x20; --name agent-mesh-rg `

&#x20; --yes `

&#x20; --no-wait

```



\---



\# 🧠 What I Learned



\- How to build a distributed microservice mesh  

\- How to deploy containerized workloads to Azure  

\- How to debug Azure Container Apps  

\- How to authenticate Docker to ACR  

\- How to design secure API key boundaries  

\- How to handle fan‑out/fan‑in patterns  

\- How to build reproducible cloud workflows  

\- How to troubleshoot real‑world cloud issues  

\- How to validate connectivity between distributed services  

\- How to operate a production‑ready microservice mesh  

