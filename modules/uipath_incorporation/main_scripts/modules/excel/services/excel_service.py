import os
import logging
import pandas as pd
from io import StringIO
from difflib import SequenceMatcher
from modules.poc4.constants.poc4_constants import PoC4Constants

class ExcelService:
    """
    Service class to handle excel operations.
    """

    @staticmethod
    def get_excel_csv_to_csv_str(
        excel_file_path: str,
        only_get_first_rows: int = None,
        csv_sep=",",
    ) -> str:
        """
        Reads an Excel or CSV file and returns its content as a CSV formatted string.

        Args:
            excel_file_path (str): The path to the Excel or CSV file.
            only_get_first_rows (int): The number of rows to read from the file.
            
        Returns:
            str: A string containing the file content in CSV format.
        """        
        if not pd.io.common.file_exists(excel_file_path):
            logging.error(f"File not found: {excel_file_path}")
            raise FileNotFoundError(f"File not found: {excel_file_path}")

        # Check if the file is an Excel or CSV file
        _, file_extension = os.path.splitext(excel_file_path)
        if file_extension.lower() not in ['.xls', '.xlsx', '.csv']:
            logging.error(f"Invalid file type: {file_extension}")
            raise ValueError(f"Invalid file type: {file_extension}")

        try:
            if file_extension.lower() == '.csv':
                dataFrame = pd.read_csv(excel_file_path, header=None, sep=csv_sep)
            else:
                dataFrame = pd.read_excel(excel_file_path, header=None)

            # Check if only_get_first_rows is a positive integer
            if only_get_first_rows is not None and only_get_first_rows > 0:
                dataFrame = dataFrame.head(only_get_first_rows)

            return dataFrame.to_csv(index=False, header=False, sep=csv_sep)
        except Exception as e:
            logging.error(f"Error reading the excel file: {e}")
            raise

    @staticmethod
    def get_excel_csv_row_number(
        excel_file_path: str,
        excel_row_content: str,
        csv_sep: str = ',',
        encoding: str = 'utf-8-sig',
    ) -> int:
        """
        Finds the row number of the specified content in the Excel or CSV file.

        Args:
            excel_file_path (str): The path to the Excel or CSV file.
            excel_row_content (str): The content to find in the file.

        Returns:
            int: The row number of the content in the file.
        """
        if not pd.io.common.file_exists(excel_file_path):
            logging.error(f"File not found: {excel_file_path}")
            raise FileNotFoundError(f"File not found: {excel_file_path}")

        _, file_extension = os.path.splitext(excel_file_path)
        if file_extension.lower() not in ['.xls', '.xlsx', '.csv']:
            logging.error(f"Invalid file type: {file_extension}")
            raise ValueError(f"Invalid file type: {file_extension}")

        try:
            if file_extension.lower() == '.csv':
                dataFrame = pd.read_csv(excel_file_path, header=None, sep=csv_sep, encoding=encoding)
            else:
                dataFrame = pd.read_excel(excel_file_path, header=None)

            # Busca a linha que contém o conteúdo especificado
            matching_rows = dataFrame[dataFrame.apply(lambda row: csv_sep.join(row.astype(str)).strip() == excel_row_content.strip(), axis=1)]

            if matching_rows.empty:
                logging.error(f"Content '{excel_row_content}' not found in the file.")
                raise ValueError(f"Content '{excel_row_content}' not found in the file.")

            row_number = matching_rows.index[0]
            return row_number + 1
        except Exception as e:
            logging.error(f"Error finding the row number: {e}")
            raise
    
    @staticmethod
    def replace_excel_csv_data_in_file(
        excel_input_file_path: str,
        excel_output_file_path: str,
        excel_data: str,
        initial_index_for_replacement: int,
        final_index_for_replacement: int,
        log_excel_data: bool = False
    ) -> bool:
        """
        Replaces a portion of the data in an existing Excel or CSV file with new data and saves it to a new file.

        Args:
            excel_input_file_path (str): Path to the input file.
            excel_output_file_path (str): Path to save the resulting file.
            excel_data (str): CSV data in string format to replace the existing data.
            initial_index_for_replacement (int): Starting index for the replacement.
            final_index_for_replacement (int): Ending index for the replacement.
            log_excel_data (bool): Flag to log the excel data.

        Returns:
            bool: True if the operation was successful, False otherwise.
        """
        try:
            if log_excel_data:
                logging.info(f"Excel data to replace: {excel_data}")

            # Convert CSV string to DataFrame
            new_data_frame = pd.read_csv(StringIO(excel_data), header=None)

            # Determine the file type based on extension
            _, file_extension = os.path.splitext(excel_input_file_path)
            file_extension = file_extension.lower()

            # Read the existing file into a DataFrame
            if file_extension == '.csv':
                existing_data_frame = pd.read_csv(excel_input_file_path, header=None)
            elif file_extension in ['.xls', '.xlsx']:
                existing_data_frame = pd.read_excel(excel_input_file_path, header=None)
            else:
                logging.error(f"Invalid input file type: {file_extension}")
                raise ValueError(f"Invalid input file type: {file_extension}")

            # Delete rows
            existing_data_frame.drop(existing_data_frame.index[initial_index_for_replacement:final_index_for_replacement])

            # Add the specified rows with new data
            existing_data_frame = pd.concat([existing_data_frame.iloc[:initial_index_for_replacement], new_data_frame, existing_data_frame.iloc[final_index_for_replacement:]], ignore_index=True)

            # Save the modified DataFrame to the output file
            if file_extension == '.csv':
                existing_data_frame.to_csv(excel_output_file_path, index=False, header=False)
                logging.info(f"File successfully saved as CSV at: {excel_output_file_path}")
            elif file_extension in ['.xls', '.xlsx']:
                existing_data_frame.to_excel(excel_output_file_path, index=False, header=False, engine='openpyxl')
                logging.info(f"File successfully saved as Excel at: {excel_output_file_path}")
            else:
                logging.error(f"Invalid output file type: {file_extension}")
                raise ValueError(f"Invalid output file type: {file_extension}")

            return True
        except Exception as e:
            logging.error(f"Error replacing data in the file: {e}")
            return False
        
    @staticmethod
    def get_value_from_csv_string(
        csv_string: str,
        column: str,
        delimiter:str = ";",
        encoding: str = 'utf-8-sig',
        case_sensitive = True,
    ) -> str:
        df = pd.read_csv(StringIO(csv_string), delimiter=delimiter, encoding=encoding, quoting=1)  # quoting=1 corresponds to csv.QUOTE_ALL
        if df.empty:
            return None

        if not case_sensitive:
            df.columns = df.columns.str.lower()
            value = df[column.lower()].iloc[0]
        else:
            value = df[column].iloc[0]

        return "" if pd.isna(value) else value

    @staticmethod
    def delete_columns_from_csv_string(
        csv_string: str,
        columns: list[str],
        delimiter: str = ';',
        encoding: str = 'utf-8-sig',
        case_insensitive_and_strip: bool = True,
    ) -> str:
        """
        Deletes specified columns from a CSV-formatted string.

        Args:
            csv_string (str): The input CSV string.
            columns (list[str]): List of column names to be deleted.
            delimiter (str, optional): The delimiter used in the CSV string. Defaults to ';'.
            encoding (str, optional): The encoding of the CSV string. Defaults to 'utf-8-sig'.
            case_insensitive_and_strip (bool, optional): Whether to perform case insensitive and strip operation on column names. Defaults to True.

        Returns:
            str: The modified CSV string with specified columns removed.
        """
        # Read the CSV string into a DataFrame
        df = pd.read_csv(StringIO(csv_string), delimiter=delimiter, encoding=encoding)

        # Normalize column names based on case sensitivity
        if case_insensitive_and_strip:
            df.columns = df.columns.str.lower().str.strip()
            columns = [col.lower().strip() for col in columns]

        # Drop the specified columns
        df.drop(columns=[col for col in columns if col in df.columns], inplace=True, errors='ignore')

        # Convert the DataFrame back to a CSV string
        output = StringIO()
        df.to_csv(output, index=False, sep=delimiter, encoding=encoding, quoting=1)  # quoting=1 corresponds to csv.QUOTE_ALL

        return output.getvalue()
    
    @staticmethod    
    def remove_last_column(input_string: str, delimiter: str = ';') -> str:
        columns = input_string.split(delimiter)
        if columns:
            columns.pop()
        return delimiter.join(columns)
    
    @staticmethod
    def get_the_most_similar_row_of_csv_file(
        csv_file: str,
        row: str,
        delimiter: str = ";",
        encoding: str = 'utf-8-sig',
        case_sensitive: bool = True,
        change_nan_to_empty_string: bool = True,
        apply_quotes: bool = True,
    ) -> str:
        df = pd.read_csv(csv_file, delimiter=delimiter, encoding=encoding)

        if change_nan_to_empty_string:
            df = df.fillna("")

        if not case_sensitive:
            row = row.lower()
            df = df.applymap(lambda x: x.lower() if isinstance(x, str) else x)
        
        max_similarity = 0
        most_similar_fields = None
        
        for _, csv_row in df.iterrows():
            fields = csv_row.values.tolist()
            csv_row_str = delimiter.join(map(str, fields))
            
            similarity = SequenceMatcher(None, row, csv_row_str).ratio()
            
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_fields = fields

        if most_similar_fields is None:
            return None
        
        if apply_quotes:
            quoted_fields = [f'"{field}"' for field in most_similar_fields]
            return delimiter.join(quoted_fields)
        else:
            return delimiter.join(map(str, most_similar_fields))
    
    @staticmethod
    def convert_xlsx_to_csv(
        xlsx_path: str,
        output_folder: str = None,
        overwrite_if_exists: bool = True,
        csv_sep: str = ';',
        encoding: str = 'utf-8-sig',
        add_sheet_name_as_column: bool = False,
        sheet_name_column_name: str = 'Sheet',
    ) -> str:
        """
        Validates if a .xlsx file exists and, if it does, converts it to .csv.

        Args:
        xlsx_path (str): Path to a .xlsx file.
        csv_dir (str): Directory where the .csv file will be saved (optional, uses the same directory as the .xlsx if empty).
        overwrite_if_exists (bool): Whether to overwrite an existing .csv file if it exists (optional, True by default).
        csv_sep (str): Delimiter for the .csv file (optional, ';' by default). Microsoft Excel only supports the ';' separator.
        encoding (str): Encoding for the .csv file (optional, 'utf-8-sig' by default).
        add_sheet_name_as_column (bool): Whether to add the sheet name as a new column in the .csv file (optional, False by default).
        sheet_name_column_name (str): Name for the new column added when adding the sheet name as a column (optional, 'Sheet' by default).

        Returns:
        str: Path to the created .csv file or None if the .xlsx file does not exist.
        """
        if not os.path.exists(xlsx_path):
            logging.error(f"convert_xlsx_to_csv() - The path '{xlsx_path}' doesn't exist.")
            return None

        if output_folder:
            csv_path = os.path.join(output_folder, os.path.splitext(os.path.basename(xlsx_path))[0] + '.csv')
        else:
            csv_path = os.path.splitext(xlsx_path)[0] + '.csv'
        
        if os.path.exists(csv_path):
            if not overwrite_if_exists:
                logging.info(f"The file '{csv_path}' already exists and it will not be overwritten.")
                return csv_path
            logging.info(f"The file '{csv_path}' already exists and it will be overwritten.")

        try:
            df = pd.read_excel(xlsx_path, header=None)
            if add_sheet_name_as_column:
                sheet_name = pd.ExcelFile(xlsx_path).sheet_names[0]
                df[sheet_name_column_name] = sheet_name
                df.iloc[0, -1] = sheet_name_column_name

            df.to_csv(csv_path, index=False, header=None, sep=csv_sep, encoding=encoding)
            logging.info(f"convert_xlsx_to_csv() - File successfuly converted to CSV: {csv_path}")
            return csv_path
        except Exception as e:
            logging.error(f"convert_xlsx_to_csv() - Error converting file '{csv_path}': {e}")
            raise

    @staticmethod
    def get_sheet_name(xlsx_path: str) -> str:
        """
        Returns the name of the first sheet in the given Excel file.
        """
        try:
            return pd.ExcelFile(xlsx_path).sheet_names[0]
        except Exception as e:
            logging.error(f"get_sheet_name() - Error getting sheet name from file '{xlsx_path}': {e}")
            raise
    
    @staticmethod
    def get_content_lines_of_csv_data(csv_data: str) -> str:
        """
        Returns the number of lines in the CSV data, excluding the header.
        If there are no data lines, returns 0.
        """
        return max(len(csv_data.splitlines()) - 1, 0)  # Subtract 1 for the header

    @staticmethod
    def create_file(
        output_file_path: str,
        insert_columns_if_file_not_exists: list[str] = [],
        force_clean_if_exists: bool = True,
    ) -> str:
        """
        If file not exists, creates a new Excel file and inserts the provided columns.
        """
        if force_clean_if_exists and os.path.exists(output_file_path):
            os.remove(output_file_path)
        if not os.path.exists(output_file_path):
            try:
                pd.DataFrame(columns=insert_columns_if_file_not_exists).to_excel(output_file_path, index=False)
            except Exception as e:
                logging.error(f"create_file() - Error creating file '{output_file_path}': {e}")
                raise
        return output_file_path
    
    @staticmethod
    def map_parametrization_to_output(
        parametrization: str,
        output_parametrization: str = PoC4Constants.OUTPUT_PARAMETRIZATION_MAP,
        delimiter:str = ";",
        encoding: str = 'utf-8-sig',
        change_nan_to_empty_string = True,
    ) -> dict:
        """
        Maps parametrization columns to a specific output format.
        
        Parameters:
            parametrization: CSV data with the original mapping
            output_parametrization: CSV with header (output columns) and row (mapping)
            delimiter: CSV delimiter
            encoding: File encoding
            change_nan_to_empty_string: Convert null values to empty string
            
        Returns:
            Dictionary with the mapping of output columns
        """
        parametrization_df = pd.read_csv(StringIO(parametrization), delimiter=delimiter, encoding=encoding)
        
        if change_nan_to_empty_string:
            parametrization_df = parametrization_df.fillna("")

        output_map_df = pd.read_csv(
            StringIO(output_parametrization),
            delimiter=delimiter,
            encoding=encoding,
            header=None
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

        return to_return

    @staticmethod
    def extract_standardized_data(
        csv_path: str,
        csv_mapping_template: dict,
        excel_header_row_index: int = None,
        sep: str = ';',
        encoding: str = 'utf-8-sig',
        strip_and_case_insensitive: bool = True,
        append_row_if_higher_than: int = 2,
        add_csv_mapping_template_to_last_column: bool = True,
    ) -> str:
        """
        Extracts data from a CSV file and maps it to standardized columns using the provided mapping template.

        Args:
            csv_path (str): Path to the CSV file.
            csv_mapping_template (dict): Dictionary with standardized column names as keys and original column names as values.
            excel_header_row_index (int, optional): Index of the Excel header row. Defaults to None.
            sep (str, optional): Delimiter for CSV file. Defaults to ';'.
            encoding (str, optional): Encoding for CSV file. Defaults to 'utf-8-sig'.
            strip_and_case_insensitive (bool, optional): Whether to strip whitespace and use case-insensitive column matching. Defaults to True.
            append_row_if_higher_than (int, optional): Append the extracted data to the CSV if the number of rows in the extracted data is higher than the specified threshold. Defaults to 2.
            add_csv_mapping_template_to_last_column (bool, optional): Whether to add the CSV mapping template as a new last column. Defaults to True.

        Returns:
            str: CSV string with standardized columns and extracted data.
        """
        if not csv_path:
            logging.error("extract_standardized_data() - csv_path is empty.")
            raise ValueError("extract_standardized_data() - csv_path is empty.") 

        try:
            original_df = pd.read_csv(csv_path, sep=sep, encoding=encoding, header=excel_header_row_index)
        except Exception as e:
            logging.error(f"Error reading CSV file: {e}")
            raise
        
        column_map = {}
        for col in original_df.columns:
            processed_name = col.strip().lower() if strip_and_case_insensitive else col
            column_map[processed_name] = col

        standardized_data = []

        for index, row in original_df.iterrows():
            standardized_row = {}
            for standardized_col, original_col in csv_mapping_template.items():
                value = ""
                if original_col:
                    lookup_col = original_col.strip().lower() if strip_and_case_insensitive else original_col
                    
                    if lookup_col in column_map:
                        actual_col = column_map[lookup_col]
                        raw_value = row[actual_col]
                        
                        if pd.notna(raw_value):
                            if isinstance(raw_value, float) and raw_value.is_integer():
                                value = int(raw_value)
                            else:
                                value = raw_value
                                
                            if isinstance(value, str):
                                value = value.strip()
                    else:
                        logging.warning(f"Original column '{original_col}' not found in CSV columns")
                        
                standardized_row[standardized_col] = value

            non_empty_count = sum(1 for v in standardized_row.values() if v not in ["", None])
            if non_empty_count > append_row_if_higher_than:
                standardized_data.append(standardized_row)

        if add_csv_mapping_template_to_last_column and standardized_data:
            # Create a new column and add the mapping template to the first row
            for i, row in enumerate(standardized_data):
                if i == 0:  # Only add to the first row
                    row["CSV_MAPPING_TEMPLATE"] = str(csv_mapping_template)
                else:
                    row["CSV_MAPPING_TEMPLATE"] = ""  # Leave empty for other rows

        standardized_df = pd.DataFrame(standardized_data)

        return standardized_df.to_csv(index=False, sep=sep, encoding=encoding, lineterminator='\r\n')
    
    @staticmethod
    def save_extracted_data_to_master_file(
        master_file_path: str,
        csv_data: str,
        csv_data_column_sep: str = ';',
        file_extracted: str = None, 
        add_csv_mapping_template_to_last_column: bool = True,
    ):
        """
        Save the extracted CSV data to the master Excel file.

        Args:
            master_file_path (str): Path to the master Excel file.
            csv_data (str): CSV-formatted string containing the extracted data.
            csv_data_column_sep (str): Separator used in the CSV data.
            file_extracted (str): Path to the file containing the extracted data.
            add_csv_mapping_template_to_last_column (bool): Whether to add the CSV mapping template to the last column.
        """
        try:
            master_df = pd.read_excel(master_file_path)
        except FileNotFoundError:
            master_df = pd.DataFrame(columns=PoC4Constants.OUTPUT_COLUMNS)

        rows = csv_data.strip().split('\r\n')
        header = rows[0].split(csv_data_column_sep)  # Base Header: Nome,Quota,NIF,Número de Sócio,Taxa,Mês da Contribuição
        data_rows = rows[1:]  # Data rows

        expected_columns = PoC4Constants.OUTPUT_COLUMNS.copy()
        if add_csv_mapping_template_to_last_column and "CSV_MAPPING_TEMPLATE" in header:
            if file_extracted:
                expected_columns.append("FILE_NAME")
            expected_columns.append("CSV_MAPPING_TEMPLATE")

        new_data = []
        filename_already_inserted = False
        for row in data_rows:
            if not row:
                continue  # Skip empty rows
            
            values = row.split(csv_data_column_sep)
            while len(values) < len(header):
                values.append("")
            
            row_dict = {}
            for col in expected_columns:
                if col == "FILE_NAME" and not filename_already_inserted:
                    row_dict[col] = os.path.basename(file_extracted) if file_extracted else ""
                    filename_already_inserted = True
                else:
                    try:
                        idx = header.index(col)
                        row_dict[col] = values[idx].strip() if idx < len(values) else ""
                    except ValueError:
                        row_dict[col] = ""

            new_data.append(row_dict)

        new_df = pd.DataFrame(new_data, columns=expected_columns)
        updated_df = pd.concat([master_df, new_df], ignore_index=True)

        # Save in master
        updated_df.to_excel(master_file_path, index=False)
        logging.info(f"Data saved in master file: {master_file_path}")