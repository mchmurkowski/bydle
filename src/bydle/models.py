from dataclasses import dataclass


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
            variable_dimensions = dict(list(zip(dimension_names, dimensions)))
            collected_dimensions.append(
                {"id": variable["id"], "dimensions": variable_dimensions}
            )
        for variable in collected_dimensions:
            if variable["id"] == variable_id:
                return variable["dimensions"]

    def construct_variable_query(self) -> list[tuple[str, str]]:
        variable_ids: list = []
        for variable in self.variables:
            variable_ids.append(variable["id"])
        variable_query: list[tuple[str, str]] = []
        for id in variable_ids:
            variable_query.append(("var-id", f"{id}"))
        # page-size should not exceed 100
        variable_query.append(("page-size", f"{len(variable_ids)}"))
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
            for _, variable in enumerate(subject.variables):
                if variable["id"] == self.id:
                    data["Jednostka pomiaru"] = variable["measureUnitName"]
                    break
            data[k] = [d[k] for d in self.values]
        return data
