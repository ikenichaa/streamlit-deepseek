import httpx
import json

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

app = FastAPI()

OLLAMA_URL = "http://localhost:11434/api/generate"

async def generate_stream(prompt: str):
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            OLLAMA_URL,
            json={
                "model": "deepseek-r1:7b",
                "prompt": prompt,
                "stream": True  # Enable streaming
            },
            timeout=60.0  # Increase timeout for large responses
        ) as response:
            async for chunk in response.aiter_lines():
                print(chunk)
                try:
                    chunk_data = json.loads(chunk)
                    yield f"data: {json.dumps(chunk_data)}\n\n"

                except json.JSONDecodeError:
                    print("error")
                    continue


@app.post("/stream-chat")
async def stream_chat(request: Request):
    print(request)
    data = await request.json()
    return StreamingResponse(
        generate_stream(data["prompt"]),
        media_type="text/event-stream"
    )

    