"""HTTP-surface oracle for the assigned quote changes."""

import json
import sys
from urllib.parse import urlencode
from wsgiref.util import setup_testing_defaults

from catalog import sku_key
from quotation import quote
from service import app


def expect(label, actual, expected):
    if actual != expected:
        raise AssertionError(f"{label}: returned {actual!r}, expected {expected!r}")


def fails(call, *args):
    try:
        call(*args)
    except ValueError:
        return
    raise AssertionError(f"{call.__name__} permitted {args!r}")


def request(sku, quantity):
    environ = {}
    setup_testing_defaults(environ)
    environ["PATH_INFO"] = "/quote"
    environ["QUERY_STRING"] = urlencode({"sku": sku, "quantity": quantity})
    response = {}

    def respond(status, headers):
        response["status"] = status

    response["body"] = json.loads(b"".join(app(environ, respond)))
    return response


def main():
    lane = sys.argv[1]
    checks = []
    if lane in {"catalog", "combined"}:
        expect("catalog strips space", sku_key(" pear-7 "), "PEAR-7")
        expect("catalog uppercases", sku_key("PlUm-2"), "PLUM-2")
        fails(sku_key, "ＰＥＡＲ-７")
        fails(sku_key, "\u00a0PEAR-7\u00a0")
        fails(sku_key, "pea r-7")
        fails(sku_key, "ORANGE-1")
        checks += ["trim", "uppercase", "ascii-only", "unicode-space-refused", "internal-space-refused", "unknown-refused"]
    if lane in {"quote", "combined"}:
        expect("quote", quote("1.25", 2),
               {"quantity": 2, "total": "2.50", "currency": "USD"})
        expect("quote rounding", quote("1.005", 1),
               {"quantity": 1, "total": "1.01", "currency": "USD"})
        fails(quote, "1.25", 0)
        fails(quote, "1.25", 101)
        fails(quote, "1.25", True)
        checks += ["usd", "fixed-decimals", "half-up", "quantity-lower-bound",
                   "quantity-upper-bound", "bool-refused"]
    if lane == "combined":
        expect("service uses both changes", request(" pear-7 ", 2),
               {"status": "200 OK", "body": {"sku": "PEAR-7", "quantity": 2,
                                            "total": "2.50", "currency": "USD"}})
        expect("service rejects invalid sku", request("ＰＥＡＲ-７", 2)["status"], "400 Bad Request")
        expect("service rejects invalid quantity", request("PLUM-2", 0)["status"], "400 Bad Request")
        checks += ["http-normalized-quote", "http-invalid-sku", "http-invalid-quantity"]
    return {"status": "passed", "phase": lane, "checks": checks}


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True))
