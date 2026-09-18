# caching-proxy

A CLI tool that starts a caching proxy server: it forwards requests to a
target origin server, caches the responses, and serves repeat requests
from cache instead of hitting the origin again.

Built with FastAPI + httpx, with a pluggable cache backend (disk via
`diskcache`, or Redis for shared/multi-instance caching).

Project brief: https://roadmap.sh/projects/caching-server

## Requirements

- Python 3.9+
- (Optional) Docker, if you want to run the Redis backend locally instead
  of the disk backend

## 1. Clone and enter the project

```bash
git clone <your-repo-url> caching-proxy
cd caching-proxy
```

## 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate      # venv\Scripts\activate on Windows
```

## 3. Install the project (editable mode)

```bash
pip install -e .
```

This registers the `caching-proxy` command on your PATH (inside the venv)
and installs all dependencies (`fastapi`, `uvicorn`, `httpx`, `diskcache`,
and `redis` if you're using the Redis backend).

## 4. (Optional) Start Redis, if using the Redis backend

Skip this step if you're using the default disk-based cache.

```bash
docker compose up -d
```

This starts a local Redis instance on `localhost:6379`.

## 5. Run the proxy

**Disk cache (default, no setup required):**

```bash
caching-proxy --port 3000 --origin http://dummyjson.com
```

**Redis cache:**

```bash
caching-proxy --port 3000 --origin http://dummyjson.com --cache-backend redis --redis-url redis://localhost:6379
```

The server will start on the given port and log its startup via Uvicorn.
Leave it running in this terminal.

## 6. Try it out

In a second terminal:

```bash
curl -i http://localhost:3000/products
```

First request → forwarded to the origin, header `X-Cache: MISS`.
Run the exact same request again → served from cache, header `X-Cache: HIT`.

## 7. Clear the cache

```bash
caching-proxy --clear-cache
```

Exits immediately; does not start a server. Works for whichever backend
you last configured.

## Project structure

```
caching_proxy/
├── cli.py              # entrypoint: --port, --origin, --clear-cache, --cache-backend
├── config.py            # runtime state (origin, cache backend choice, TTL)
├── app.py                # FastAPI app, catch-all route
├── proxy.py              # forwards requests, applies caching + X-Cache header
├── http_caching.py       # Cache-Control / ETag parsing and TTL decisions
├── cache_backend/
│   ├── base.py            # shared get/set/clear interface
│   ├── disk_backend.py    # diskcache-backed implementation
│   └── redis_backend.py   # Redis-backed implementation
└── utils.py               # header filtering (hop-by-hop headers, Host, etc.)
```

## Notes

- The disk cache lives in `.cache/` inside wherever the command is run
  from, and is not committed to git (see `.gitignore`).
- `--clear-cache` empties the currently configured backend; it does not
  touch the other backend's stored data.
