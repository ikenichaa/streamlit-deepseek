# fastapi_app.py
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import httpx
from asyncio import sleep
import json

app = FastAPI()

OLLAMA_URL = "http://localhost:11434/api/generate"

async def test_generate_stream(prompt: str):
    print("streaming---")
    for x in range(10):
       # Yield each chunk as a JSON object
        chunk = {
            "id": str(x),
            "text": f"Streaming chunk {x} for prompt: {prompt}",
            "done": False if x < 9 else True
        }
        yield f"data: {json.dumps(chunk)}\n\n"  # SSE format
        await sleep(1)
    # async with httpx.AsyncClient() as client:
    #     async with client.stream(
    #         "POST",
    #         OLLAMA_URL,
    #         json={
    #             "model": "deepseek-r1:7b",
    #             "prompt": prompt,
    #             "stream": True  # Enable streaming
    #         }
    #     ) as response:
    #         async for chunk in response.aiter_lines():
    #             print(chunk)
    #             yield chunk + "\n"


async def generate_stream(prompt: str):
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            OLLAMA_URL,
            json={
                "model": "deepseek-r1:7b",
                "prompt": prompt,
                "stream": True  # Enable streaming
            }
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

@app.get("/test")
async def test(request: Request):
    print("test--")
    # data = await request.json()
    return StreamingResponse(
        generate_stream("test"),
        media_type="text/event-stream"
    )
    