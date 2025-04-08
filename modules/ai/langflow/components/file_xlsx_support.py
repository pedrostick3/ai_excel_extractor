from langflow.base.data import BaseFileComponent
from langflow.base.data.utils import TEXT_FILE_TYPES, parallel_load_data
from langflow.io import BoolInput, IntInput, DropdownInput
from langflow.schema import Data
import pandas as pd
import os
import re
from functools import partial

# Adds XLSX to supported file types and common encodings
CUSTOM_FILE_TYPES = sorted([*TEXT_FILE_TYPES, "xlsx"])
COMMON_ENCODINGS = sorted(['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1', 'utf-16', 'windows-1252'])

class FileComponent(BaseFileComponent):
    """Handles the loading and processing of text and Excel files with encoding support."""

    display_name = "File + xlsx support"
    description = "Load text or Excel files with configurable encoding support"
    icon = "file-text"
    name = "File + xlsx support"

    VALID_EXTENSIONS = CUSTOM_FILE_TYPES

    inputs = [
        *BaseFileComponent._base_inputs,
        DropdownInput(
            name="encoding",
            display_name="File Encoding",
            info="Character encoding of the text file (does not affect Excel files)",
            options=COMMON_ENCODINGS,
            value='utf-8-sig',
            advanced=True
        ),
        BoolInput(
            name="excel_header",
            display_name="Excel Header Row",
            info="Use the first row as column headers for Excel files",
            value=False,
            advanced=True
        ),
        BoolInput(
            name="use_multithreading",
            display_name="[Deprecated] Use Multithreading",
            advanced=True,
            value=True,
            info="Set 'Processing Concurrency' greater than 1 to enable multithreading.",
        ),
        BoolInput(
            name="clean_file_path",
            display_name="Clean File Path",
            advanced=True,
            value=True,
            info="Clean File Path by replacing non-alphanumeric characters with underscores.",
        ),
        IntInput(
            name="concurrency_multithreading",
            display_name="Processing Concurrency",
            advanced=True,
            info="When multiple files are being processed, the number of files to be processed simultaneously.",
            value=1,
        ),
    ]

    outputs = [
        *BaseFileComponent._base_outputs,
    ]

    def process_files(self, file_list: list[BaseFileComponent.BaseFile]) -> list[BaseFileComponent.BaseFile]:
        """Processes files with support for encoding and special character handling."""
        if not file_list:
            raise ValueError("No files to process.")

        concurrency = 1 if not self.use_multithreading else max(1, self.concurrency_multithreading)
        file_count = len(file_list)

        if concurrency < 2 or file_count < 2:
            self.log(f"Processing {file_count} files sequentially.")
            processed_data = [self.process_file(file.path, self.clean_file_path) for file in file_list]
        else:
            self.log(f"Starting parallel processing of {file_count} files with concurrency: {concurrency}.")
            file_paths = [file.path for file in file_list]
            processed_data = parallel_load_data(
                file_paths,
                silent_errors=self.silent_errors,
                load_function=partial(self.process_file, clean_file_path=self.clean_file_path),
                max_concurrency=concurrency,
            )

        return self.rollup_data(file_list, processed_data)

    def process_file(self, file_path: str, clean_file_path: bool) -> Data:
        """Processes a single file and returns its Data object."""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        if ext in TEXT_FILE_TYPES:
            return self.process_text(file_path, clean_file_path)
        elif ext == ".xlsx":
            return self.process_excel(file_path, clean_file_path)
        else:
            self.log(f"Unsupported file type: {file_path}")
            return None

    def process_text(self, file_path: str, clean_file_path: bool) -> Data:
        """Processes text files with the specified encoding."""
        try:
            with open(file_path, 'r', encoding=self.encoding, errors='replace') as f:
                content = f.read()
            
            # Clean file path by removing strange characters
            self.log(f"raw file_path: {file_path}")
            if clean_file_path:
                file_path = self.clean_file_name(str(file_path))
                self.log(f"cleaned file_path: {file_path}")

            # Returns a single Data object with the file path and full content
            return Data(
                file_path=file_path,
                text=content,
            )
        except Exception as e:
            self.log(f"Error processing text file {file_path}: {str(e)}")
            return None  # Returns None in case of an error

    def process_excel(self, file_path: str, clean_file_path: bool) -> Data:
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
            
            excel_sheet_name = self.get_sheet_name(file_path)

            # Clean file path by removing strange characters
            self.log(f"raw file_path: {file_path}")
            self.log(f"clean_file_path: {clean_file_path}")
            if clean_file_path:
                file_path = self.clean_file_name(str(file_path))
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
        
    def clean_file_name(self, file_name: str) -> str:
        """Removes non-alphanumeric characters and replaces them with a safe character."""
        # Replaces non-alphanumeric characters with an underscore
        return re.sub(r'[^a-zA-Z0-9._-]', '_', file_name)
    
    def get_sheet_name(self, xlsx_path: str) -> str:
        """
        Returns the name of the first sheet in the given Excel file.
        """
        try:
            return pd.ExcelFile(xlsx_path).sheet_names[0]
        except Exception as e:
            self.log(f"get_sheet_name() - Error getting sheet name from file '{xlsx_path}': {e}")
            raise

    def rollup_data(self, file_list: list[BaseFileComponent.BaseFile], processed_data: list[Data]) -> list[BaseFileComponent.BaseFile]:
        """Merges processed data back into the BaseFile objects."""
        for file, data in zip(file_list, processed_data):
            if data is not None:
                file.data = data  # Assuming BaseFile has a 'data' attribute
        return file_list