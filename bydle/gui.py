import os
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter.messagebox import showerror, showinfo

import pandas as pd

from bydle.helpers import get_data_from_api
from bydle.models import SubjectDetails, UnitDetails, VariableData


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bydle")
        self["padx"] = 20
        self["pady"] = 20


class MainFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__()
        options: dict = {"padx": 10, "pady": 10}

        self.unit_query_lf = ttk.LabelFrame(
            container, text="Wyszukaj i wybierz jednostkę"
        )
        self.unit_query_lf.grid(column=0, row=0, sticky="we", **options)

        self.unit_query = tk.StringVar()
        self.unit_query_ef = ttk.Entry(self.unit_query_lf, textvariable=self.unit_query)
        self.unit_query_ef.grid(column=0, row=0, sticky="we", **options)

        def submit_unit_query():
            if len(self.unit_query.get()) == 0:
                no_unit_error_msg = showerror(
                    title="Błąd", message="Wyszukaj nazwę jednostki w polu wyszukiwania"
                )
                self.unit_query_ef.focus()
            else:
                self.unit_query_results_lb.delete(0, tk.END)
                query: list[tuple[str, str]] = [("name", f"{self.unit_query.get()}")]
                results = get_data_from_api(endpoint="units/search", query_items=query)[
                    "results"
                ]
                unit_query_results: tuple = ()
                for result in results:
                    unit_query_results = (
                        *unit_query_results,
                        f"{result['name']} - poziom: {result['level']} - id: {result['id']}",
                    )
                self.unit_query_choices = unit_query_results
                for choice in self.unit_query_choices:
                    self.unit_query_results_lb.insert(tk.END, choice)
                self.unit_query_results_lb.focus()

        self.unit_query_submit_btn = ttk.Button(
            self.unit_query_lf, text="Szukaj", command=submit_unit_query
        )
        self.unit_query_submit_btn.grid(column=1, row=0, sticky="e", **options)

        self.unit_query_choices: tuple = ()
        self.unit_query_results_lb = tk.Listbox(
            self.unit_query_lf, selectmode=tk.SINGLE, width=60, height=5
        )
        self.unit_query_results_lb.grid(
            column=0, row=1, columnspan=2, sticky="we", **options
        )

        self.unit_query_lf.columnconfigure(0, weight=1)

        self.subject_query_lf = ttk.LabelFrame(
            container, text="Podaj tematy i pobierz dane"
        )
        self.subject_query_lf.grid(column=0, row=1, sticky="we", **options)

        self.subject_query_lbl = ttk.Label(
            self.subject_query_lf,
            text="Wypisz identyfikatory tematów (podgrup) oddzielone spacjami,\nnp. P2914 P3256 ...",
        )
        self.subject_query_lbl.grid(column=0, row=0, sticky="we", **options)

        self.subject_query = tk.StringVar()
        self.subject_query_ef = ttk.Entry(
            self.subject_query_lf, textvariable=self.subject_query, width=60
        )
        self.subject_query_ef.grid(column=0, row=1, sticky="we", **options)

        def submit_subject_query():
            if len(self.unit_query.get()) == 0:
                no_unit_error_msg = showerror(
                    title="Błąd", message="Wyszukaj nazwę jednostki w polu wyszukiwania"
                )
                self.unit_query_ef.focus()
            elif not self.unit_query_results_lb.curselection():
                select_unit_first_msg = showinfo(
                    title="Wskazówka", message="Wybierz jednostkę z listy wyników"
                )
                self.unit_query_results_lb.focus()
            elif len(self.subject_query.get()) == 0:
                no_subjects_error_msg = showerror(
                    title="Błąd", message="Podaj przynajmniej identyfikator podgrupy"
                )
                self.subject_query_ef.focus()
            else:
                output_directory = filedialog.askdirectory()
                unit_selection: list[str] = self.unit_query_results_lb.get(
                    "active"
                ).split(" - ")
                unit_choice: dict[str, str] = {
                    "id": unit_selection[-1].strip("id: "),
                    "name": unit_selection[0],
                    "level": unit_selection[1].strip("poziom: "),
                }
                unit = UnitDetails(
                    id=unit_choice["id"],
                    name=unit_choice["name"],
                    level=int(unit_choice["level"]),
                )
                for s in self.subject_query.get().split(" "):
                    subject_details = get_data_from_api(endpoint=f"subjects/{s}")
                    query: list[tuple[str, str]] = [
                        ("subject-id", f"{s}"),
                        ("page-size", "100"),
                    ]
                    subject_variables = get_data_from_api(
                        endpoint="variables", query_items=query
                    )
                    if subject_variables["totalRecords"] > 100:
                        print(
                            f"Skipping subject {s}.\nSupport for larger datasets is not yet implemented"
                        )
                    else:
                        subject_variables = subject_variables["results"]
                        subject = SubjectDetails(
                            id=subject_details["id"],
                            name=subject_details["name"],
                            dimensions=subject_details["dimensions"],
                            variables=subject_variables,
                        )
                        variable_data = get_data_from_api(
                            endpoint=f"data/by-unit/{unit.id}",
                            query_items=subject.construct_variable_query(),
                        )
                        variables: list = []
                        for var in range(len(variable_data["results"])):
                            variable = VariableData(
                                id=variable_data["results"][var]["id"],
                                values=variable_data["results"][var]["values"],
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
                        # attrId of 0 signals no data - remove such rows
                        df = df[df["attrId"] != 0]
                        output_path = os.path.join(output_directory, f"{s}.csv")
                        df.drop(columns=["attrId"]).to_csv(output_path, index=False)

        self.subject_query_submit_btn = ttk.Button(
            self.subject_query_lf, text="Pobierz", command=submit_subject_query
        )
        self.subject_query_submit_btn.grid(column=0, row=2, sticky="e", **options)

        self.unit_query_ef.focus()
