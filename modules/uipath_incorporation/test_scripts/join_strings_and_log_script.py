import os
import logging

def join_strings_and_log(str1: str, str2: str) -> str:
    """
    This function takes two strings as input and returns their concatenation.

    Configuração "Normal".
    """
    # Configurar logs
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("process.log", encoding='utf-8'), logging.StreamHandler()],
        )
    logging.info("## join_strings_and_log: A iniciar teste ##")
    
    # Concatenar as strings e registar no log
    concatenated_strings = str1 + str2
    logging.info(f"## join_strings_and_log: concatenated_strings = '{str1}' + '{str2}' = '{concatenated_strings}' ##")

    return concatenated_strings

def join_strings_and_log_0(str1: str, str2: str, logs_type_tests: list[int] = [0,1,2,3,4,5]) -> str:
    """
    This function takes two strings as input and returns their concatenation.

    Configuração "Normal" com os vários tipos e níveis de log.
    """
    # Configurar logs
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("process.log", encoding='utf-8'), logging.StreamHandler()],
        )
    logging.info("## join_strings_and_log_0: A iniciar teste ##")
    
    # Concatenar as strings e registar no log
    concatenated_strings = str1 + str2
    if 0 in logs_type_tests:
        logging.info(f"## join_strings_and_log_0: [0] logging.info: concatenated_strings = '{str1}' + '{str2}' = '{concatenated_strings}' ##")
    if 1 in logs_type_tests:
        logging.warning(f"## join_strings_and_log_0: [1] logging.warning: concatenated_strings = '{str1}' + '{str2}' = '{concatenated_strings}' ##")
    if 2 in logs_type_tests:
        logging.error(f"## join_strings_and_log_0: [2] logging.error: concatenated_strings = '{str1}' + '{str2}' = '{concatenated_strings}' ##")
    if 3 in logs_type_tests:
        logging.critical(f"## join_strings_and_log_0: [3] logging.critical: concatenated_strings = '{str1}' + '{str2}' = '{concatenated_strings}' ##")
    if 4 in logs_type_tests:
        logging.debug(f"## join_strings_and_log_0: [4] logging.debug: concatenated_strings = '{str1}' + '{str2}' = '{concatenated_strings}' ##")
    if 5 in logs_type_tests:
        logging.exception(f"## join_strings_and_log_0: [5] logging.exception: concatenated_strings = '{str1}' + '{str2}' = '{concatenated_strings}' ##")

    return concatenated_strings

def join_strings_and_log_1(str1: str, str2: str) -> str:
    """
    This function takes two strings as input and returns their concatenation.

    Configuração "Normal" usando tambem o `logger.info`.
    """
    # Configurar logs
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("process.log", encoding='utf-8'), logging.StreamHandler()],
        )
    logger = logging.getLogger(__name__)
    logger.info("## join_strings_and_log_1: A iniciar teste ##")
    
    # Concatenar as strings e registar no log
    concatenated_strings = str1 + str2
    logging.info(f"## join_strings_and_log_1: concatenated_strings = '{str1}' + '{str2}' = '{concatenated_strings}' ##")

    return concatenated_strings

def join_strings_and_log_2(str1: str, str2: str) -> str:
    """
    This function takes two strings as input and returns their concatenation.

    Configurar diretório temporário para validar se o ambiente tem permissões restritas que impedem a criação ou gravação do ficheiro.
    """
    # Configurar logs
    log_file_path = os.path.join(os.getenv("TEMP", "/tmp"), "process.log")
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file_path, encoding='utf-8'), logging.StreamHandler()],
        )
    logger = logging.getLogger(__name__)
    logger.info("## join_strings_and_log_2: A iniciar teste ##")
    logger.info(f"## join_strings_and_log_2: temporary log_file_path = {log_file_path} ##")
    
    # Concatenar as strings e registar no log
    concatenated_strings = str1 + str2
    logger.info(f"## join_strings_and_log_2: concatenated_strings = '{str1}' + '{str2}' = '{concatenated_strings}' ##")

    return concatenated_strings

def join_strings_and_log_3(str1: str, str2: str) -> str:
    """
    This function takes two strings as input and returns their concatenation.

    Configurar sem o StreamHandler (pois pode estar a atrofiar com a consola do UiPath).
    """
    # Configurar logs
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("process.log", encoding='utf-8')],
        )
    logger = logging.getLogger(__name__)
    logger.info("## join_strings_and_log_3: A iniciar teste ##")
    
    # Concatenar as strings e registar no log
    concatenated_strings = str1 + str2
    logging.info(f"## join_strings_and_log_3: concatenated_strings = '{str1}' + '{str2}' = '{concatenated_strings}' ##")

    return concatenated_strings

def join_strings_and_log_4(str1: str, str2: str) -> str:
    """
    This function takes two strings as input and returns their concatenation.

    Configurar sem `logging.basicConfig`.
    """
    # Configurar logs
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        file_handler = logging.FileHandler("process.log", encoding='utf-8')
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    logger.info("## join_strings_and_log_4: A iniciar teste ##")
    
    # Concatenar as strings e registar no log
    concatenated_strings = str1 + str2
    logger.info(f"## join_strings_and_log_4: concatenated_strings = '{str1}' + '{str2}' = '{concatenated_strings}' ##")

    return concatenated_strings

def join_strings_and_log_5(str1: str, str2: str) -> str:
    """
    This function takes two strings as input and returns their concatenation.

    Configuração duplicada.
    """
    # Configurar logs
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("process.log", encoding='utf-8'), logging.StreamHandler()],
    )
    logger = logging.getLogger(__name__)
    logger.info("## join_strings_and_log_5: A iniciar teste (1st config) ##")
    
    # Configurar logs
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("process.log", encoding='utf-8'), logging.StreamHandler()],
    )
    logger = logging.getLogger(__name__)
    logger.info("## join_strings_and_log_5: A iniciar teste (2nd config) ##")
    
    # Concatenar as strings e registar no log
    concatenated_strings = str1 + str2
    logging.info(f"## join_strings_and_log_5: concatenated_strings = '{str1}' + '{str2}' = '{concatenated_strings}' ##")

    return concatenated_strings