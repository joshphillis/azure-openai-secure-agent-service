import os
import uuid
import logging
from typing import Optional
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from openai import AzureOpenAI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    force=True,
)
logger = logging.getLogger("summaries-worker")

class InvokeRequest(BaseModel):
    text: str

API_KEY = os.getenv("API_KEY")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version="2024-12-01-preview",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
)

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/invoke")
async def invoke(
    request: InvokeRequest,
    x_api_key: Optional[str] = Header(default=None, alias="x-api-key"),
):
    request_id = str(uuid.uuid4())
    logger.info(f"{request_id} - ENTERED /invoke handler")

    if x_api_key != API_KEY:
        logger.warning(f"{request_id} - Unauthorized request, x_api_key={x_api_key!r}")
        raise HTTPException(status_code=401, detail="Invalid API key")

    logger.info(f"{request_id} - Summary requested, length={len(request.text)}")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You summarize text."},
                {"role": "user", "content": request.text}
            ]
        )

        summary = response.choices[0].message.content

        logger.info(f"{request_id} - Summary completed")
        return {"result": summary, "request_id": request_id}

    except Exception as e:
        import traceback, sys
        logger.error(f"{request_id} - Exception: {e}")
        logger.error(traceback.format_exc())
        sys.stdout.flush()
        sys.stderr.flush()
        raise HTTPException(status_code=500, detail="Internal worker error")