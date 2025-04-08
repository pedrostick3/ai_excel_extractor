import os
import pandas as pd
from langflow.custom import Component
from langflow.io import FileInput, IntInput, MultilineInput, MessageTextInput, Output
from langflow.schema.message import Message


class ExcelCSVtoCSVStrComponent(Component):
    display_name = "Excel/CSV to CSV String"
    description = "Converts an Excel or CSV file to a CSV-formatted string. Accepts both file path and direct CSV content."
    icon = "file"
    name = "ExcelCSVtoCSVStr"

    inputs = [
        MultilineInput(
            name="csv_content",
            display_name="CSV Content",
            info="Direct CSV content as a string.",
        ),
        FileInput(
            name="excel_file_path",
            display_name="Excel/CSV File",
            info="The path to the Excel or CSV file.",
            advanced=True,
        ),
        IntInput(
            name="only_get_first_rows",
            display_name="Max Rows",
            info="Number of rows to read (optional).",
            value=None,
            advanced=True,
        ),
        MessageTextInput(
            name="csv_sep",
            display_name="CSV Separator",
            info="Character used as separator in CSV files.",
            value=";",
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="CSV String", name="csv_string", method="convert_to_csv_string"),
    ]

    def convert_to_csv_string(self) -> Message:
        if self.excel_file_path:
            csv_data = self._process_file(self.excel_file_path)
            return Message(text=csv_data, csv_data=csv_data)
        elif self.csv_content:
            csv_data = self._process_csv_string(self.csv_content)
            return Message(text=csv_data, csv_data=csv_data)
        else:
            self.log("No valid input provided.")
            return Message(text="Error: No valid input provided.")

    def _process_file(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            self.log(f"File not found: {file_path}")
            return "Error: File not found."

        _, file_extension = os.path.splitext(file_path)
        if file_extension.lower() not in [".xls", ".xlsx", ".csv"]:
            self.log(f"Invalid file type: {file_extension}")
            return "Error: Invalid file type."

        try:
            if file_extension.lower() == ".csv":
                df = pd.read_csv(file_path, header=None, sep=self.csv_sep)
            else:
                df = pd.read_excel(file_path, header=None)
            
            if self.only_get_first_rows is not None and self.only_get_first_rows > 0:
                df = df.head(self.only_get_first_rows)
            
            return df.to_csv(index=False, header=False, sep=self.csv_sep)
        except Exception as e:
            self.log(f"Error processing file: {e}")
            return f"Error: {str(e)}"

    def _process_csv_string(self, csv_string: str) -> str:
        try:
            from io import StringIO
            df = pd.read_csv(StringIO(csv_string), header=None, sep=self.csv_sep)
            
            if self.only_get_first_rows is not None and self.only_get_first_rows > 0:
                df = df.head(self.only_get_first_rows)
            
            return df.to_csv(index=False, header=False, sep=self.csv_sep)
        except Exception as e:
            self.log(f"Error processing CSV content: {e}")
            return f"Error: {str(e)}"
