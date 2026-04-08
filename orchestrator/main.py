from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Any
import os
import httpx
import uuid
import time
import asyncio

app = FastAPI(title="Summaries Orchestrator")

class SummarizeRequest(BaseModel):
    text: str

class WorkerResponse(BaseModel):
    worker_url: str
    status_code: int
    latency_ms: float
    result: Any | None
    error: str | None = None

class OrchestratorResponse(BaseModel):
    correlation_id: str
    worker_responses: List[WorkerResponse]
    aggregated_summary: str

WORKER_URLS = [
    url.strip()
    for url in os.getenv("WORKER_URLS", "").split(",")
    if url.strip()
]

API_KEY = os.getenv("API_KEY", "")

if not WORKER_URLS:
    raise RuntimeError("WORKER_URLS env var is required")

@app.get("/health")
async def health():
    return {"status": "ok", "workers": len(WORKER_URLS)}

@app.post("/summarize", response_model=OrchestratorResponse)
async def summarize(request: SummarizeRequest):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API_KEY not configured")

    correlation_id = str(uuid.uuid4())
    payload = {"text": request.text}

    async def call_worker(worker_url: str) -> WorkerResponse:
        url = worker_url.rstrip("/") + "/invoke"
        headers = {
            "x-api-key": API_KEY,
            "x-correlation-id": correlation_id,
        }
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(url, json=payload, headers=headers)
            latency_ms = (time.perf_counter() - start) * 1000
            if resp.status_code == 200:
                return WorkerResponse(
                    worker_url=worker_url,
                    status_code=resp.status_code,
                    latency_ms=latency_ms,
                    result=resp.json(),
                )
            else:
                return WorkerResponse(
                    worker_url=worker_url,
                    status_code=resp.status_code,
                    latency_ms=latency_ms,
                    result=None,
                    error=resp.text,
                )
        except Exception as e:
            latency_ms = (time.perf_counter() - start) * 1000
            return WorkerResponse(
                worker_url=worker_url,
                status_code=500,
                latency_ms=latency_ms,
                result=None,
                error=str(e),
            )

    results: List[WorkerResponse] = await asyncio.gather(
        *[call_worker(u) for u in WORKER_URLS]
    )

    summaries: List[str] = []
    for r in results:
        if r.result and isinstance(r.result, dict):
            summary = r.result.get("summary") or r.result.get("result") or str(r.result)
            summaries.append(f"[{r.worker_url}] {summary}")

    aggregated = "\n\n".join(summaries) if summaries else "No successful worker responses."

    return OrchestratorResponse(
        correlation_id=correlation_id,
        worker_responses=results,
        aggregated_summary=aggregated,
    )