import os
import pandas as pd

def get_excel_csv_to_csv_str(excel_file_path: str, only_get_first_rows: int = None) -> str:
    """
    Reads an Excel or CSV file and returns its content as a CSV formatted string.

    Args:
        excel_file_path (str): The path to the Excel or CSV file.
        only_get_first_rows (int): The number of rows to read from the file.
        
    Returns:
        str: A string containing the file content in CSV format.
    """
    if not pd.io.common.file_exists(excel_file_path):
        print(f"File not found: {excel_file_path}")
        raise FileNotFoundError(f"File not found: {excel_file_path}")

    # Check if the file is an Excel or CSV file
    _, file_extension = os.path.splitext(excel_file_path)
    if file_extension.lower() not in ['.xls', '.xlsx', '.csv']:
        print(f"Invalid file type: {file_extension}")
        raise ValueError(f"Invalid file type: {file_extension}")

    try:
        if file_extension.lower() == '.csv':
            dataFrame = pd.read_csv(excel_file_path, header=None)
        else:
            dataFrame = pd.read_excel(excel_file_path, header=None)

        # Check if only_get_first_rows is a positive integer
        if only_get_first_rows is not None and only_get_first_rows > 0:
            dataFrame = dataFrame.head(only_get_first_rows)

        return dataFrame.to_csv(index=False, header=False)
    except Exception as e:
        print(f"Error reading the excel file: {e}")
        raise