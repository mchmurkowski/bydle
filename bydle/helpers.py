from typing import Any

import requests

BASE_URL = "https://bdl.stat.gov.pl/api/v1/"


def get_data_from_api(endpoint: str, *args: str) -> Any:
    fmt = "?format=json"
    url: str = BASE_URL + endpoint + fmt
    for arg in args:
        url += arg
    r = requests.get(url)
    try:
        match r.status_code:
            case 200:
                return r.json()
            case _:
                raise ValueError(url, r.status_code, "Coś poszło nie tak :-/")
    except SyntaxError:
        if r.status_code == 200:
            return r.json()
        else:
            raise ValueError(url, r.status_code, "Coś poszło nie tak :-/")


if __name__ == "__main__":
    print("Module contains helper functions.")
