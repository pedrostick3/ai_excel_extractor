from datetime import datetime
import scripts_and_classes.join_strings_script as join_strings_script
import scripts_and_classes.read_excel_script as read_excel_script
import scripts_and_classes.write_excel_script as write_excel_script

EXCEL_INPUT_FILE_PATH = "./assets/Execution_data Template.xlsx"

def main():
    print("### START ###")

    # Join strings using the join_strings_script
    result = join_strings_script.join_strings("Hello ", "World!")
    print(f"Resultado da junção: {result}")

    # Read an Excel file using the read_excel_script
    excel_rows = read_excel_script.get_excel_csv_to_csv_str(
        excel_file_path=EXCEL_INPUT_FILE_PATH,
        only_get_first_rows=10,
    )
    print(f"Conteúdo das primeiras 10 linhas do ficheiro Excel '{EXCEL_INPUT_FILE_PATH}':\n{excel_rows}")

    # Modify Excel file using the write_excel_script
    output_excel_file_path = f'EXECUÇÃO - {datetime.now().strftime("%d_%m_%Y %H-%M-%S")} - Execution_data Template.xlsx'
    write_excel_script.modify_excel_content_for_execution_category(
        input_excel_file_path=EXCEL_INPUT_FILE_PATH,
        output_excel_file_path=output_excel_file_path,
        excel_header_row_index=1,
    )
    print(f"Ficheiro Excel {EXCEL_INPUT_FILE_PATH} modificado com sucesso e guardado em '{output_excel_file_path}'")

    print("### END ###")