import httpx
from fastapi import Request
from fastapi.responses import Response

from caching_proxy import config, cache_backend
from caching_proxy.utils import filter_headers


async def handle_request(request: Request, path: str) -> Response:
    method = request.method
    query = str(request.url.query)
    body = await request.body()

    key = cache_backend.make_key(method, path, query, body)
    cached = cache_backend.get(key)

    if cached is not None:
        headers = dict(cached["headers"])
        headers["X-Cache"] = "HIT"
        return Response(
            content=cached["content"],
            status_code=cached["status_code"],
            headers=headers,
        )

    origin_url = f"{config.ORIGIN.rstrip('/')}/{path}"

    async with httpx.AsyncClient() as client:
        origin_response = await client.request(
            method,
            origin_url,
            params=request.query_params,
            headers=filter_headers(dict(request.headers)),
            content=body,
            follow_redirects=True,
        )

    response_headers = filter_headers(dict(origin_response.headers))

    cache_backend.set(key, {
        "status_code": origin_response.status_code,
        "headers": response_headers,
        "content": origin_response.content,
    })

    response_headers["X-Cache"] = "MISS"
    return Response(
        content=origin_response.content,
        status_code=origin_response.status_code,
        headers=response_headers,
    )