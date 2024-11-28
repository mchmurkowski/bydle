import logging
import tkinter as tk
from tkinter import filedialog, ttk
from tkinter.messagebox import showerror, showinfo

from bydle.helpers import collect_frames, get_data_from_api, write_frames_as_csv
from bydle.models import SubjectDetails, UnitDetails

logger = logging.getLogger(__name__)


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ByDLe")
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
                showerror(
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
                showerror(
                    title="Błąd", message="Wyszukaj nazwę jednostki w polu wyszukiwania"
                )
                self.unit_query_ef.focus()
            elif not self.unit_query_results_lb.curselection():
                showinfo(title="Wskazówka", message="Wybierz jednostkę z listy wyników")
                self.unit_query_results_lb.focus()
            elif len(self.subject_query.get()) == 0:
                showerror(
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
                        logger.warning(
                            f"Support for larger datasets is not yet implemented. Skipping subject {s}."
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
                        collected_data_frames = collect_frames(
                            variable_data=variable_data, subject=subject, unit=unit
                        )
                        try:
                            write_frames_as_csv(
                                subject_id=s,
                                collected_frames=collected_data_frames,
                                target_dir=output_directory,
                            )
                        except PermissionError:
                            logger.error(
                                "Tried to write file to directory with no permission"
                            )
                            showerror(
                                title="Błąd",
                                message="Brak uprawnień do zapisywania plików we wskazanym folderze. Wybierz inny folder",
                            )
                        except TypeError:
                            # This occurs when user cancels out of directory chooser dialog, but only on Linux machines. On Windows the file is written to current working directory anyway
                            # TODO: do not write files and do not send a request if the users cancels out of dialog as this is expected behavior from ux standpoint
                            logger.error("No valid target directory provided")
                            showerror(
                                title="Błąd",
                                message="Nie wskazano folderu docelowego. Wskaż folder, do którego mają zostać zapisane pliki",
                            )

        self.subject_query_submit_btn = ttk.Button(
            self.subject_query_lf, text="Pobierz", command=submit_subject_query
        )
        self.subject_query_submit_btn.grid(column=0, row=2, sticky="e", **options)

        self.unit_query_ef.focus()
