import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk
from tkinter.messagebox import showerror
from typing import Any

import pandas as pd
import requests

BASE_URL = "https://bdl.stat.gov.pl/api/v1/"


def get_data_from_api(endpoint: str, *args: str) -> Any:
    fmt = "?format=json"
    url: str = BASE_URL + endpoint + fmt
    for arg in args:
        url += arg
    r = requests.get(url)
    match r.status_code:
        case 200:
            return r.json()
        case _:
            raise ValueError(url, r.status_code, "Coś poszło nie tak :-/")


@dataclass
class UnitDetails:
    id: str
    name: str
    level: int


@dataclass
class SubjectDetails:
    id: str
    name: str
    dimensions: list
    variables: list

    def get_variable_dimensions(self, variable_id: int) -> dict:
        dimension_names: list = self.dimensions
        collected_dimensions: list[dict] = []
        for variable in self.variables:
            dimensions: list = []
            for k in variable:
                if k.startswith("n"):
                    dimensions.append(variable[k])
            variable_dimensions = dict(list(zip(self.dimensions, dimensions)))
            collected_dimensions.append(
                {"id": variable["id"], "dimensions": variable_dimensions}
            )
        for variable in collected_dimensions:
            if variable["id"] == variable_id:
                return variable["dimensions"]

    def construct_variable_query(self) -> str:
        variable_ids: list = []
        for variable in self.variables:
            variable_ids.append(variable["id"])
        variable_query: str = ""
        for id in variable_ids:
            variable_query += f"&var-id={id}"
        # page-size cannot exceed 100
        variable_query += f"&page-size={len(variable_ids)}"
        return variable_query


@dataclass
class VariableData:
    id: int
    values: list[dict]

    def get_data_for_variable(self, unit: UnitDetails, subject: SubjectDetails) -> dict:
        data: dict = {}
        variable_dimensions: dict = subject.get_variable_dimensions(self.id)
        for k in self.values[0]:
            data["Jednostka terytorialna"] = unit.name
            data["Temat"] = subject.name
            data["Identyfikator zmiennej"] = self.id
            for dimension in variable_dimensions:
                data[dimension] = variable_dimensions[dimension]
            for variable in range(len(subject.variables)):
                if subject.variables[variable]["id"] == self.id:
                    data["Jednostka pomiaru"] = subject.variables[variable][
                        "measureUnitName"
                    ]
                    break
            data[k] = [d[k] for d in self.values]
        return data


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ByDLe")
        self.geometry("600x400")
        self["padx"] = 20
        self["pady"] = 20


class QueryFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)
        options = {"padx": 5, "pady": 5}
        self.query_choices = ()
        self.query_label = ttk.Label(container, text="Nazwa miejscowości")
        self.query_label.grid(column=0, row=0, sticky=tk.W, **options)

        self.query = tk.StringVar()
        self.query_entry_field = ttk.Entry(container, textvariable=self.query)
        self.query_entry_field.grid(column=1, row=0, sticky=tk.W, **options)
        self.query_entry_field.focus()

        def unit_query():
            if len(self.query.get()) == 0:
                self.modal_error = showerror(
                    title="Błąd",
                    message='Uzupełnij pole "Nazwa miejscowości" i kliknij przycisk "Wyszukaj"',
                )
                self.query_entry_field.focus()
            else:
                self.choices_listbox.delete(0, tk.END)
                query = get_data_from_api("units/search", f"&name={self.query.get()}")
                query_results = query["results"]
                query_choices = ()
                for result in query_results:
                    query_choices = (
                        *query_choices,
                        f"{result['name']} - poziom: {result['level']} - id: {result['id']}",
                    )
                self.query_choices = query_choices
                for item in self.query_choices:
                    self.choices_listbox.insert(tk.END, item)
                self.choices_listbox.focus()

        self.query_submit_btn = ttk.Button(container, text="Szukaj", command=unit_query)
        self.query_submit_btn.grid(column=2, row=0, sticky=tk.W, **options)

        self.choices_listbox = tk.Listbox(
            container, selectmode=tk.SINGLE, width=60, height=5
        )
        self.choices_listbox.grid(column=0, row=1, columnspan=3, sticky=tk.W, **options)

        def subject_query():
            if len(self.subject_query.get()) == 0:
                self.modal_error = showerror(
                    title="Błąd",
                    message='Uzupełnij pole "Tematy" i kliknij przycisk "Pobierz"',
                )
                self.subject_entry_field.focus()
            else:
                self.unit_selection = self.choices_listbox.curselection()
                if self.unit_selection:
                    unit_choice_id = (
                        self.choices_listbox.get(self.unit_selection)
                        .split(" - ")[-1]
                        .strip("id: ")
                    )
                    unit_choice_name = self.choices_listbox.get(
                        self.unit_selection
                    ).split(" - ")[0]
                    unit_choice_level = int(
                        self.choices_listbox.get(self.unit_selection)
                        .split(" - ")[1]
                        .strip("poziom: ")
                    )
                    unit = UnitDetails(
                        id=unit_choice_id,
                        name=unit_choice_name,
                        level=unit_choice_level,
                    )
                    for s in self.subject_query.get().split(" "):
                        subject_details = get_data_from_api(f"subjects/{s}")
                        subject_variables = get_data_from_api(
                            "variables", f"&subject-id={s}"
                        )
                        if subject_variables["totalRecords"] > 100:
                            print(
                                f"Skipping subject {s}.\nSupport for larger datasets is not yet implemented"
                            )
                        elif (
                            subject_variables["totalRecords"]
                            > subject_variables["pageSize"]
                        ):
                            subject_variables = get_data_from_api(
                                "variables",
                                f"&subject-id={s}",
                                f"&pagesize={subject_variables['totalRecords']}",
                            )
                        subject_variables = subject_variables["results"]
                        subject = SubjectDetails(
                            id=subject_details["id"],
                            name=subject_details["name"],
                            dimensions=subject_details["dimensions"],
                            variables=subject_variables,
                        )
                        variable_data = get_data_from_api(
                            f"data/by-unit/{unit.id}",
                            subject.construct_variable_query(),
                        )
                        variables: list = []
                        for var in range(len(variable_data["results"])):
                            variable = VariableData(
                                variable_data["results"][var]["id"],
                                variable_data["results"][var]["values"],
                            )
                            variables.append(variable)
                        collected_data_frames: list = []
                        for variable in range(len(variables)):
                            df = pd.DataFrame.from_dict(
                                variables[variable].get_data_for_variable(
                                    unit=unit, subject=subject
                                )
                            )
                            collected_data_frames.append(df)
                        df = pd.concat(collected_data_frames, ignore_index=True)
                        # attdId of 0 signals no data - remove such rows
                        df = df[df["attrId"] != 0]
                        # Write dataframe to a csv
                        df.drop(columns=["attrId"]).to_csv(f"{s}.csv", index=False)
                else:
                    self.modal_error = showerror(
                        title="Błąd", message="Wybierz jednostkę z listy"
                    )
                    self.choices_listbox.focus()

        self.subject_label = ttk.Label(container, text="Tematy")
        self.subject_label.grid(column=0, row=2, sticky=tk.W, **options)
        self.subject_info = ttk.Label(
            container,
            text="Wpisz identyfikatory tematów (podgrup) oddzielane spacją, np. P2914 P3256 ...",
        )
        self.subject_info.grid(column=0, row=3, columnspan=3, sticky=tk.W, **options)
        self.subject_query = tk.StringVar()
        self.subject_entry_field = ttk.Entry(
            container, textvariable=self.subject_query, width=60
        )
        self.subject_entry_field.grid(
            column=0, row=4, columnspan=3, sticky=tk.W, **options
        )
        self.subject_query_submit_btn = ttk.Button(
            container, text="Pobierz", command=subject_query
        )
        self.subject_query_submit_btn.grid(column=2, row=5, sticky=tk.W, **options)


if __name__ == "__main__":
    app = Application()
    QueryFrame(app)
    app.mainloop()
