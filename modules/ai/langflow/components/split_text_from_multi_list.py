from langchain_text_splitters import CharacterTextSplitter
from langflow.custom import Component
from langflow.io import HandleInput, IntInput, MessageTextInput, Output
from langflow.schema import Data, DataFrame
from langflow.utils.util import unescape_string


class SplitTextComponent(Component):
    display_name: str = "Split Text MultiListInput"
    description: str = "Split text into chunks based on specified criteria from multiple input lists."
    icon = "scissors-line-dashed"
    name = "SplitTextFromMultiList"

    inputs = [
        HandleInput(
            name="data_inputs",
            display_name="Input Documents",
            info="The data to split.",
            input_types=["Data", "DataFrame"],
            is_list=True,
            required=True,
        ),
        IntInput(
            name="chunk_overlap",
            display_name="Chunk Overlap",
            info="Number of characters to overlap between chunks.",
            value=200,
        ),
        IntInput(
            name="chunk_size",
            display_name="Chunk Size",
            info="The maximum number of characters in each chunk.",
            value=1000,
        ),
        MessageTextInput(
            name="separator",
            display_name="Separator",
            info="The character to split on. Defaults to newline.",
            value="\n",
        ),
        MessageTextInput(
            name="text_key",
            display_name="Text Key",
            info="The key to use for the text column.",
            value="text",
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Chunks", name="chunks", method="split_text"),
        Output(display_name="DataFrame", name="dataframe", method="as_dataframe"),
    ]

    def _docs_to_data(self, docs) -> list[Data]:
        return [Data(text=doc.page_content, data=doc.metadata) for doc in docs]

    def _docs_to_dataframe(self, docs):
        data_dicts = [{self.text_key: doc.page_content, **doc.metadata} for doc in docs]
        return DataFrame(data_dicts)

    def split_text_base(self):
        separator = unescape_string(self.separator)
        documents = []
        for input_ in self.data_inputs:
            if isinstance(input_, DataFrame):
                if not len(input_):
                    msg = "DataFrame is empty"
                    raise TypeError(msg)

                input_.text_key = self.text_key
                try:
                    docs = input_.to_lc_documents()
                except Exception as e:
                    msg = f"Error converting DataFrame to documents: {e}"
                    raise TypeError(msg) from e
                documents.extend(docs)
            else:
                if not input_:
                    msg = "No data inputs provided"
                    raise TypeError(msg)

                input_.text_key = self.text_key
                try:
                    doc = input_.to_lc_document()
                except AttributeError as e:
                    msg = f"Invalid input type in collection: {e}"
                    raise TypeError(msg) from e
                documents.append(doc)
        try:
            splitter = CharacterTextSplitter(
                chunk_overlap=self.chunk_overlap,
                chunk_size=self.chunk_size,
                separator=separator,
            )
            return splitter.split_documents(documents)
        except Exception as e:
            msg = f"Error splitting text: {e}"
            raise TypeError(msg) from e

    def split_text(self) -> list[Data]:
        return self._docs_to_data(self.split_text_base())

    def as_dataframe(self) -> DataFrame:
        return self._docs_to_dataframe(self.split_text_base())