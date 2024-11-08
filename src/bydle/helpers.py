from typing import Any, Optional
from urllib.parse import urlencode, urljoin

import requests

BASE_URL = "https://bdl.stat.gov.pl/api/v1/"


def get_data_from_api(
    endpoint: str,
    query_items: Optional[list[tuple[str, str]]] = None,
    *args: str,
) -> Any:
    base: str = BASE_URL
    fmt: str = "json"
    query: list[tuple[str, str]] = [("format", fmt)]
    url: str = f"{urljoin(base, endpoint)}?{urlencode(query)}"
    if query_items:
        for item in query_items:
            query.append(item)
        url = f"{urljoin(base, endpoint)}?{urlencode(query)}"
    for arg in args:
        url += f"&{arg}"
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        raise ValueError(url, r.status_code, "Something went wrong")


if __name__ == "__main__":
    import json

    query: list[tuple[str, str]] = [("subject-id", "P3472"), ("page-size", "20")]
    response = get_data_from_api("variables", query, "page=5")
    print(json.dumps(response, indent=2))
