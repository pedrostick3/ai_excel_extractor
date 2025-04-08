from langflow.base.data.utils import TEXT_FILE_TYPES, parse_text_file_to_data, retrieve_file_paths
from langflow.custom import Component
from langflow.io import BoolInput, IntInput, MessageTextInput, MultiselectInput, DropdownInput
from langflow.schema import Data
from langflow.schema.dataframe import DataFrame
from langflow.template import Output
import pandas as pd
import re
import os

# Adds XLSX to supported file types and common encodings
CUSTOM_FILE_TYPES = sorted([*TEXT_FILE_TYPES, "xlsx"])
COMMON_ENCODINGS = sorted(['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1', 'utf-16', 'windows-1252'])

class DirectoryComponent(Component):
    display_name = "Directory + xlsx"
    description = "Recursively load files from a directory."
    icon = "folder"
    name = "Directory"

    inputs = [
        MessageTextInput(
            name="path",
            display_name="Path",
            info="Path to the directory to load files from. Defaults to current directory ('.')",
            value=".",
            tool_mode=True,
        ),
        MultiselectInput(
            name="types",
            display_name="File Types",
            info="File types to load. Select one or more types or leave empty to load all supported types.",
            options=CUSTOM_FILE_TYPES,
            value=[],
        ),
        IntInput(
            name="depth",
            display_name="Depth",
            info="Depth to search for files.",
            value=0,
            advanced=True,
        ),
        BoolInput(
            name="load_hidden",
            display_name="Load Hidden",
            advanced=True,
            info="If true, hidden files will be loaded.",
        ),
        BoolInput(
            name="recursive",
            display_name="Recursive",
            advanced=True,
            info="If true, the search will be recursive.",
        ),
        BoolInput(
            name="silent_errors",
            display_name="Silent Errors",
            advanced=True,
            info="If true, errors will not raise an exception.",
        ),
        BoolInput(
            name="clean_file_path",
            display_name="Clean File Path",
            advanced=True,
            value=True,
            info="Clean File Path by replacing non-alphanumeric characters with underscores.",
        ),
        BoolInput(
            name="excel_header",
            display_name="Excel Header Row",
            info="Use the first row as column headers for Excel files",
            value=False,
            advanced=True
        ),
        DropdownInput(
            name="encoding",
            display_name="File Encoding",
            info="Character encoding of the text file (does not affect Excel files)",
            options=COMMON_ENCODINGS,
            value='utf-8-sig',
            advanced=True
        ),
    ]

    outputs = [
        Output(display_name="Data", name="data", method="load_directory"),
        Output(display_name="DataFrame", name="dataframe", method="as_dataframe"),
    ]

    def load_directory(self) -> list[Data]:
        path = self.path
        types = self.types
        depth = self.depth
        load_hidden = self.load_hidden
        recursive = self.recursive
        silent_errors = self.silent_errors

        resolved_path = self.resolve_path(path)

        # If no types are specified, use all supported types
        if not types:
            types = CUSTOM_FILE_TYPES

        # Check if all specified types are valid
        invalid_types = [t for t in types if t not in CUSTOM_FILE_TYPES]
        if invalid_types:
            msg = f"Invalid file types specified: {invalid_types}. Valid types are: {CUSTOM_FILE_TYPES}"
            raise ValueError(msg)

        valid_types = types

        file_paths = retrieve_file_paths(
            resolved_path,
            load_hidden=load_hidden,
            recursive=recursive,
            depth=depth,
            types=valid_types,
        )

        loaded_data = []
        for file_path in file_paths:
            try:
                if file_path.endswith('.xlsx'):
                    # Use pandas to read the Excel file
                    df = pd.read_excel(file_path, header=None)
                    #loaded_data.append(Data(text=df.to_csv(sep=';', encoding='utf-8-sig', index=False, header=False)))
                    loaded_data.append(self._process_excel(file_path, self.clean_file_path))
                else:
                    # Handle other file types as before
                    loaded_data.append(parse_text_file_to_data(file_path, silent_errors=silent_errors))
            except Exception as e:
                if not silent_errors:
                    raise e  # Raise the exception if silent_errors is False
                else:
                    print(f"Error loading file {file_path}: {e}")

        valid_data = [x for x in loaded_data if x is not None and isinstance(x, Data)]
        self.status = valid_data
        return valid_data

    def _process_excel(self, file_path: str, clean_file_path: bool) -> Data:
        """Processes Excel files and returns the content in CSV format with ';' separator."""
        try:
            df = pd.read_excel(
                file_path,
                engine='openpyxl',
                header=0 if self.excel_header else None,
                dtype=str  # Reads all data as strings to preserve formatting
            )

            # Converts the DataFrame to CSV format with ';' separator
            content = df.to_csv(sep=';', encoding=self.encoding, header=self.excel_header, index=False)
            
            excel_sheet_name = self._get_sheet_name(file_path)

            # Clean file path by removing strange characters
            self.log(f"raw file_path: {file_path}")
            self.log(f"clean_file_path: {clean_file_path}")
            if clean_file_path:
                file_path = self._clean_file_name(str(file_path))
                self.log(f"cleaned file_path: {file_path}")

            # Changes the file_path extension to .csv
            csv_file_path = os.path.splitext(file_path)[0] + '.csv'
            self.log(f"csv_file_path: {csv_file_path}")

            # Returns a single Data object with the CSV file path and full content in CSV format
            return Data(
                file_path=csv_file_path,  # Changes the extension to .csv
                text=content,
                excel_sheet_name=excel_sheet_name,
            )
        except Exception as e:
            self.log(f"Error processing Excel file {file_path}: {str(e)}")
            return None  # Returns None in case of an error
        
    def _clean_file_name(self, file_name: str) -> str:
        """Removes non-alphanumeric characters and replaces them with a safe character."""
        # Replaces non-alphanumeric characters with an underscore
        return re.sub(r'[^a-zA-Z0-9._-]', '_', file_name)
    
    def _get_sheet_name(self, xlsx_path: str) -> str:
        """
        Returns the name of the first sheet in the given Excel file.
        """
        try:
            return pd.ExcelFile(xlsx_path).sheet_names[0]
        except Exception as e:
            self.log(f"get_sheet_name() - Error getting sheet name from file '{xlsx_path}': {e}")
            raise

    def as_dataframe(self) -> DataFrame:
        return DataFrame(self.load_directory())
