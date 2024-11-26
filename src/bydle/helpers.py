import os
from typing import Any, Optional
from urllib.parse import urlencode, urljoin

import pandas as pd
import requests

from bydle.models import SubjectDetails, UnitDetails, VariableData

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


def collect_frames(
    variable_data, unit: UnitDetails, subject: SubjectDetails
) -> list[pd.DataFrame]:
    variables: list = []
    for _, result in enumerate(variable_data["results"]):
        variable = VariableData(id=result["id"], values=result["values"])
        variables.append(variable)
    collected_frames: list[pd.DataFrame] = []
    for _, variable in enumerate(variables):
        df = pd.DataFrame.from_dict(
            variable.get_data_for_variable(unit=unit, subject=subject)
        )
        collected_frames.append(df)
    return collected_frames


def write_frames_as_csv(
    subject_id: str, collected_frames: list[pd.DataFrame], target_dir: str
) -> None:
    df = pd.concat(collected_frames, ignore_index=True)
    ## attrId pf 0 signals no data - filter out such rows
    df = df[df["attrId"] != 0]
    output_path = os.path.join(target_dir, f"{subject_id}.csv")
    df.drop(columns=["attrId"]).to_csv(output_path, index=False)


if __name__ == "__main__":
    import json

    query: list[tuple[str, str]] = [("subject-id", "P3472"), ("page-size", "20")]
    response = get_data_from_api("variables", query, "page=5")
    print(json.dumps(response, indent=2))
