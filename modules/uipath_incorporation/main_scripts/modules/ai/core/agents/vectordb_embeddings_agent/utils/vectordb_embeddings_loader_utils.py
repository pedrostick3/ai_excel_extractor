import logging
from langchain_core.documents import Document
from langchain_community.document_loaders import UnstructuredEmailLoader

class VectordbEmbeddingsLoaderUtils:    
    @staticmethod
    def load_documents_from_eml(
        eml_path: str,
        documents_split_mode: str = "single",
        log_found_documents: bool = True,
    ) -> list[Document]:
        """
        Load documents from an email file (EML) into a list of Documents.

        Args:
            eml_path (str): The file path to the email file in EML format. This file should be accessible and 
                properly formatted as an email message.
            documents_split_mode (str, optional): Specifies how to handle documents. The options are:
                - 'single': Combine all elements into a single Document (default).
                - 'elements': Maintain each element as a separate Document (ex: useful for html).
                - 'paged': Combine elements by page into separate Documents.
            log_found_documents (bool): Enables logging of found documents. Defaults to True.
        """
        # Load plain text body
        email_body_text = UnstructuredEmailLoader(
            eml_path,
            include_headers=True,
            process_attachments=False, # Only get email body
            content_source="text/plain", # Email body in text
        ).load_and_split()

        # Load HTML body
        email_body_html = UnstructuredEmailLoader(
            eml_path,
            include_headers=True,
            process_attachments=False, # Only get email body
            content_source="text/html", # Email body in html
            mode=documents_split_mode,
        ).load_and_split()

        email_body = email_body_text + email_body_html

        # Load the attachments
        email_attachments = UnstructuredEmailLoader(
            eml_path,
            include_headers=True,
            process_attachments=True,  # Only get attachments
            mode=documents_split_mode,
        ).load_and_split()

        # Add source types to metadata
        for doc in email_body:
            doc.metadata["content_type"] = "email_body"
        for doc in email_attachments:
            doc.metadata["content_type"] = "attachment"

        full_email = email_body + email_attachments

        if log_found_documents:
            logging.info("################################################################")
            cnt=0
            for docs in full_email:
                logging.info(f"full_email[{cnt}] = {docs}")
                cnt+=1
            logging.info("################################################################")

        return full_email
