from fastapi import FastAPI, Request

from caching_proxy.proxy import handle_request

app = FastAPI()

@app.api_route("/{path:path}",  methods=["Get", "POST", "PUT", "DELETE", "PATCH"])
async def catch_all(request: Request, path: str):
    return await handle_request(request, path)