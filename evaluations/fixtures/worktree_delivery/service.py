"""The quote endpoint used to check the combined worker changes."""

import json
from urllib.parse import parse_qs

from catalog import PRICES, sku_key
from quotation import quote


def app(environ, start_response):
    if environ["PATH_INFO"] != "/quote":
        start_response("404 Not Found", [])
        return [b"not found\n"]
    try:
        query = parse_qs(environ["QUERY_STRING"], keep_blank_values=True)
        sku = sku_key(query["sku"][0])
        quantity = int(query["quantity"][0])
        result = {"sku": sku, **quote(PRICES[sku], quantity)}
    except (ValueError, KeyError):
        start_response("400 Bad Request", [("Content-Type", "application/json")])
        return [b'{"error": "invalid quote"}\n']
    start_response("200 OK", [("Content-Type", "application/json")])
    return [json.dumps(result, sort_keys=True).encode()]
