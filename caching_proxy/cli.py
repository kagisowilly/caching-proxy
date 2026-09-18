import argparse
import uvicorn

from caching_proxy import config, cache_backend


def main():
    parser = argparse.ArgumentParser(prog="caching-proxy")
    parser.add_argument("--port", type=int, help="Port to run the proxy server on")
    parser.add_argument("--origin", type=str, help="Origin server URL to forward requests to")
    parser.add_argument("--clear-cache", action="store_true", help="Clear the cache and exit")

    args = parser.parse_args()

    if args.clear_cache:
        cache_backend.clear()
        print("Cache cleared.")
        return

    if not args.port or not args.origin:
        parser.error("--port and --origin are required unless using --clear-cache")

    config.ORIGIN = args.origin

    uvicorn.run("caching_proxy.app:app", host="0.0.0.0", port=args.port)