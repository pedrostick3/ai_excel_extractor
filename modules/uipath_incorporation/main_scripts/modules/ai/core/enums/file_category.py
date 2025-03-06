from enum import Enum
class FileCategory(Enum):
    """
    Enum for the different file categories.
    """
    EXECUCAO = "Execução"
    TESTE_EXECUCAO = "Teste Execução"
    INVALIDO = "INVALIDO"

    @staticmethod
    def get_category_by_name(category_name: str) -> "FileCategory":
        """
        Get the FileCategory by its name.

        Args:
            category_name (str): The category name.

        Returns:
            FileCategory: The FileCategory.
        """
        for category in FileCategory:
            if category.value == category_name:
                return category

        return FileCategory.INVALIDO