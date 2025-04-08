import pandas as pd
from io import StringIO
from langflow.custom import Component
from langflow.io import MessageTextInput, Output, MultilineInput
from langflow.schema import Data

class MapParametrizationComponent(Component):
    display_name: str = "Map Parametrization to Output"
    description: str = "Maps parametrization columns to a specific output format."
    icon = "code"
    name = "MapParametrization"

    inputs = [
        MultilineInput(
            name="parametrization",
            display_name="Parametrization CSV",
            info="CSV data with the original mapping.",
            value="{text}",
            required=True,
        ),
        MultilineInput(
            name="output_parametrization",
            display_name="Output Parametrization CSV",
            info="CSV with header (output columns) and row (mapping).",
            value="{text}",
            required=True,
        ),
        MessageTextInput(
            name="delimiter",
            display_name="CSV Delimiter",
            info="CSV delimiter.",
            value=";",
            required=False,
        ),
        MessageTextInput(
            name="encoding",
            display_name="File Encoding",
            info="File encoding.",
            value="utf-8-sig",
            required=False,
        ),
        MessageTextInput(
            name="change_nan_to_empty_string",
            display_name="Change NaN to Empty String",
            info="Convert null values to empty string.",
            value="True",
            required=False,
        ),
    ]

    outputs = [
        Output(display_name="Mapped Output", name="mapped_output", method="map_parametrization"),
    ]

    def map_parametrization(self) -> Data:
        """Maps parametrization columns to a specific output format."""
        parametrization = self.parametrization
        output_parametrization = self.output_parametrization
        delimiter = self.delimiter
        encoding = self.encoding
        change_nan_to_empty_string = self.change_nan_to_empty_string.lower() == 'true'

        # Read the parametrization CSV
        parametrization_df = pd.read_csv(StringIO(parametrization), delimiter=delimiter, encoding=encoding)

        if change_nan_to_empty_string:
            parametrization_df = parametrization_df.fillna("")

        # Read the output mapping CSV
        output_map_df = pd.read_csv(
            StringIO(output_parametrization),
            delimiter=delimiter,
            encoding=encoding,
            header=None,
        )

        output_columns = output_map_df.iloc[0].tolist()  # Header
        parametrization_mapping = output_map_df.iloc[1].tolist()  # Mapping

        to_return = {}
        for output_col, map_col in zip(output_columns, parametrization_mapping):
            try:
                if map_col in parametrization_df.columns:
                    value = parametrization_df[map_col].iloc[0]
                    if pd.isna(value) and change_nan_to_empty_string:
                        value = ""
                else:
                    value = ""
            except (IndexError, KeyError):
                value = ""
                
            to_return[output_col] = str(value) if value is not None else ""

        return Data(text=str(to_return))  # Return the mapping as a string representation