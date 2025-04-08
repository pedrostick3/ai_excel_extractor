import pandas as pd
from io import StringIO
from langflow.custom import Component
from langflow.io import MessageTextInput, MultilineInput, IntInput, BoolInput, Output, FileInput
from langflow.schema import Data, DataFrame, Message


class StandardizedDataExtractor(Component):
    display_name = "Standardized Data Extractor"
    description = "Extracts and standardizes data from a CSV file based on a mapping template."
    icon = "table"
    name = "StandardizedDataExtractor"

    inputs = [
        FileInput(
            name="csv_file",
            display_name="CSV File",
            info="Upload the CSV file to be processed.",
            advanced=True,
        ),
        MultilineInput(
            name="csv_content",
            display_name="CSV Content",
            info="Paste the content of the CSV file here.",
            value="{text}",
        ),
        MessageTextInput(
            name="csv_mapping_template",
            display_name="CSV Mapping Template",
            info="JSON-formatted string defining column mappings.",
            required=True,
        ),
        MultilineInput(
            name="table_header_row",
            display_name="Table Header Row",
            info="Row of the header (if applicable).",
            value="{text}",
        ),
        MessageTextInput(
            name="sep",
            display_name="CSV Separator",
            info="Column separator used in the CSV file.",
            value=";",
            advanced=True,
        ),
        MessageTextInput(
            name="encoding",
            display_name="Encoding",
            info="Encoding format of the CSV file.",
            value="utf-8-sig",
            advanced=True,
        ),
        BoolInput(
            name="strip_and_case_insensitive",
            display_name="Strip & Case Insensitive",
            info="Whether to strip whitespace and ignore case when matching columns.",
            value=True,
            advanced=True,
        ),
        IntInput(
            name="append_row_if_higher_than",
            display_name="Append Row If Higher Than",
            info="Minimum number of non-empty values required to append a row.",
            value=2,
            advanced=True,
        ),
        BoolInput(
            name="add_csv_mapping_template_to_last_column",
            display_name="Add Mapping Template Column",
            info="Whether to add the mapping template as a new column.",
            value=True,
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Standardized CSV", name="standardized_csv", method="build_message"),
        Output(display_name="Standardized DataFrame", name="standardized_dataframe", method="build_dataframe"),
        Output(display_name="Standardized Data", name="standardized_data", method="build_data"),
    ]
    
    def build_message(self) -> Message:
        standardized_df = self._process_csv()
        csv_output = standardized_df.to_csv(index=False, sep=self.sep, encoding=self.encoding, lineterminator='\r\n')
        return Message(text=csv_output)
    
    def build_dataframe(self) -> DataFrame:
        standardized_df = self._process_csv()
        df_result = DataFrame(standardized_df)
        self.status = df_result  # store in self.status for logs
        return df_result
    
    def build_data(self) -> Data:
        standardized_df = self._process_csv()
        data_output = standardized_df.to_dict(orient='records')
        self.log(f"list_of_rows: {data_output}")
        return Data(list_of_rows=data_output)

    def _process_csv(self) -> pd.DataFrame:
        header_row_index = self._get_csv_row_number(
            csv_content= self.csv_content,
            row_content = self._remove_last_column(self.table_header_row),
            csv_sep = ";",
        ) - 1

        if self.csv_file:
            try:
                original_df = pd.read_csv(self.csv_file, sep=self.sep, encoding=self.encoding, header=header_row_index)
            except Exception as e:
                self.log(f"Error reading CSV file: {e}")
                return ValueError(text=f"Error reading CSV file: {e}")
        elif self.csv_content:
            try:
                original_df = pd.read_csv(StringIO(self.csv_content), sep=self.sep, encoding=self.encoding, header=header_row_index)
            except Exception as e:
                self.log(f"Error reading CSV content: {e}")
                return ValueError(text=f"Error reading CSV content: {e}")
        else:
            return ValueError(text="No CSV file or content provided.")
        
        
        try:
            csv_mapping_template = eval(self.csv_mapping_template)  # Convert string to dict
        except Exception as e:
            self.log(f"Invalid CSV mapping template: {e}")
            return ValueError(text=f"Error: Invalid mapping template - {e}")
        
        column_map = {}
        for col in original_df.columns:
            processed_name = col.strip().lower() if self.strip_and_case_insensitive else col
            column_map[processed_name] = col
        
        standardized_data = []
        
        for _, row in original_df.iterrows():
            standardized_row = {}
            for standardized_col, original_col in csv_mapping_template.items():
                value = ""
                if original_col:
                    lookup_col = original_col.strip().lower() if self.strip_and_case_insensitive else original_col
                    
                    if lookup_col in column_map:
                        actual_col = column_map[lookup_col]
                        raw_value = row[actual_col]
                        
                        if pd.notna(raw_value):
                            if isinstance(raw_value, float) and raw_value.is_integer():
                                value = int(raw_value)
                            else:
                                value = raw_value.strip() if isinstance(raw_value, str) else raw_value
                    else:
                        self.log(f"Original column '{original_col}' not found in CSV columns")
                        
                standardized_row[standardized_col] = value
            
            non_empty_count = sum(1 for v in standardized_row.values() if v not in ["", None])
            if non_empty_count > self.append_row_if_higher_than:
                standardized_data.append(standardized_row)
        
        if self.add_csv_mapping_template_to_last_column and standardized_data:
            for i, row in enumerate(standardized_data):
                row["CSV_MAPPING_TEMPLATE"] = str(csv_mapping_template) if i == 0 else ""
        
        standardized_df = pd.DataFrame(standardized_data)
        return standardized_df
    
    def _remove_last_column(self, input_string: str, delimiter: str = ';') -> str:
        columns = input_string.split(delimiter)
        if columns:
            columns.pop()
        return delimiter.join(columns)

    def _get_csv_row_number(
        self,
        csv_content: str,
        row_content: str,
        csv_sep: str = ',',
        encoding: str = 'utf-8-sig',
    ) -> int:
        """
        Finds the row number of the specified content in the Excel or CSV file.

        Args:
            csv_content (str): The CSV content.
            row_content (str): The content to find in the file.

        Returns:
            int: The row number of the content in the file.
        """
        if not csv_content:
            self.log("CSV content is empty.")
            raise ValueError("CSV content is empty.")
        try:
            dataFrame = pd.read_csv(StringIO(csv_content), header=None, sep=csv_sep, encoding=encoding)

            # Busca a linha que contém o conteúdo especificado
            matching_rows = dataFrame[dataFrame.apply(lambda row: csv_sep.join(row.astype(str)).strip() == row_content.strip(), axis=1)]

            if matching_rows.empty:
                self.log(f"Content '{row_content}' not found in the file.")
                raise ValueError(f"Content '{row_content}' not found in the file:\n{csv_content}.")

            row_number = matching_rows.index[0]
            return row_number + 1
        except Exception as e:
            self.log(f"Error finding the row number: {e}")
            raise
