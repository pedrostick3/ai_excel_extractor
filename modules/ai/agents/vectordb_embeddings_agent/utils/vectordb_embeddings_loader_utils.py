from email import policy
from email.parser import BytesParser
import logging
import chardet
from langchain_core.documents import Document
from langchain_community.document_loaders import UnstructuredEmailLoader

class VectordbEmbeddingsLoaderUtils:
    @staticmethod
    def get_encoding_of_file(
        file_path: str,
        default_encoding: str = 'utf-8-sig',
    ) -> str:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            return chardet.detect(raw_data)['encoding'] or default_encoding

    @staticmethod
    def load_documents_from_eml(
        eml_path: str,
        documents_split_mode: str = "single",
        encoding: str = 'utf-8-sig',
        log_found_documents: bool = True,
    ) -> list[Document]:
        """
        Load documents from an email file (EML) into a list of Documents.

        Args:
            eml_path (str): The file path to the email file in EML format. This file should be accessible and 
                properly formatted as an email message.
            documents_split_mode (str, optional): Specifies how to handle documents. The options are:
                - 'single': Combine all elements into a single Document (default).
                - 'elements': Maintain each element as a separate Document (ex: useful for html) and gets better metadata.
                - 'paged': Combine elements by page into separate Documents.
            encoding (str, optional): Encoding for the EML file. Defaults to 'utf-8-sig'.
            log_found_documents (bool): Enables logging of found documents. Defaults to True.
        """
        encoding = VectordbEmbeddingsLoaderUtils.get_encoding_of_file(file_path=eml_path, default_encoding=encoding)

        # Load plain text body
        email_body_text = UnstructuredEmailLoader(
            eml_path,
            include_headers=True,
            process_attachments=False, # Only get email body
            content_source="text/plain", # Email body in text
            encoding=encoding,
        ).load_and_split()

        # Load HTML body
        email_body_html = UnstructuredEmailLoader(
            eml_path,
            include_headers=True,
            process_attachments=False, # Only get email body
            content_source="text/html", # Email body in html
            mode=documents_split_mode,
            encoding=encoding,
        ).load_and_split()

        email_body = email_body_text + email_body_html
        for doc in email_body:
            doc.metadata.setdefault('content_type', 'email_body')

        # Load the attachments
        email_attachments = UnstructuredEmailLoader(
            eml_path,
            include_headers=True,
            process_attachments=True, # Only get attachments
            mode=documents_split_mode,
            encoding=encoding,
        ).load_and_split()

        # Metadata assignment
        email_attachments_filenames = VectordbEmbeddingsLoaderUtils._extract_attachments_from_eml_file(eml_path)
        if not email_attachments_filenames:
            email_attachments = []
        else:
            current_attachment_idx = -1
            seen_filenames = set()
        
        for doc in email_attachments:
            # Detect new attachments using multiple metadata signals
            is_new_attachment = (
                doc.metadata.get('category') == 'AttachmentHeader' or
                doc.metadata.get('filename') not in seen_filenames
            )
            
            if (email_attachments_filenames and is_new_attachment and current_attachment_idx < len(email_attachments_filenames) - 1):
                current_attachment_idx += 1
                seen_filenames.add(doc.metadata.get('filename', ''))

            # Assign metadata
            filename = ""
            if email_attachments_filenames:
                filename = (
                    email_attachments_filenames[current_attachment_idx] 
                    if 0 <= current_attachment_idx < len(email_attachments_filenames)
                    else f'unknown_attachment_{current_attachment_idx}'
                )
            else:
                filename = f'no_attachment_{current_attachment_idx}'
            
            doc.metadata.update({
                'content_type': 'attachment',
                'attachment_filename': filename,
                'attachment_index': current_attachment_idx,
            })

        full_docs = email_body + email_attachments
        for doc in full_docs:
            doc.metadata = VectordbEmbeddingsLoaderUtils._stringify_non_string_dict_values(doc.metadata)
        
        if log_found_documents:
            logging.info("#"*80)
            logging.info(f"Processed EML: {eml_path}")
            logging.info(f"Detected {len(full_docs)} documents with {len(email_attachments_filenames)} attachments")
            for i, doc in enumerate(full_docs):
                logging.info(f"Document {i} metadata: {dict(doc.metadata)}")
            logging.info("#"*80)

        return full_docs

    @staticmethod
    def _extract_attachments_from_eml_file(eml_path: str) -> list:
        """
        Returns a list of attachments filenames extracted from the given eml file.
        """
        try:
            with open(eml_path, 'rb') as f:
                msg = BytesParser(policy=policy.default).parsebytes(f.read())
                return [str(part.get_filename()) for part in msg.iter_attachments() if part.get_filename()]
        except Exception as e:
            logging.error(f"Attachment extraction failed on file {eml_path}\nError: {e}")
            return []
    
    @staticmethod
    def _stringify_non_string_dict_values(input_dict: dict) -> dict:
        """
        Check if a dictionary has non-string values and convert them to strings.

        Args:
            input_dict (dict): The dictionary to check and modify.

        Returns:
            dict: A new dictionary with all non-string values converted to strings.
        """
        modified_dict = {}
        
        for key, value in input_dict.items():
            if not isinstance(value, str):
                modified_dict[key] = str(value)
            else:
                modified_dict[key] = value
        
        return modified_dict
