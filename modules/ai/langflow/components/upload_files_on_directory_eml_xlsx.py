from langflow.base.data.utils import TEXT_FILE_TYPES, parse_text_file_to_data, retrieve_file_paths
from langflow.custom import Component
from langflow.io import BoolInput, IntInput, MessageTextInput, MultiselectInput, DropdownInput
from langflow.schema import Data
from langflow.schema.dataframe import DataFrame
from langflow.template import Output
import pandas as pd
import email
from email import policy
from email.parser import BytesParser
from langchain_community.document_loaders import UnstructuredEmailLoader
from langchain_core.documents import Document
import chardet
import re
import os

# Adds XLSX to supported file types and common encodings
CUSTOM_FILE_TYPES = sorted([*TEXT_FILE_TYPES, "xlsx", "eml"])
COMMON_ENCODINGS = sorted(['utf-8', 'utf-8-sig', 'latin-1', 'iso-8859-1', 'utf-16', 'windows-1252'])

class DirectoryComponent(Component):
    display_name = "Directory + eml + xlsx"
    description = "Recursively load files from a directory."
    icon = "folder"
    name = "Directory"

    inputs = [
        MessageTextInput(
            name="path",
            display_name="Path",
            info="Path to the directory to load files from. Defaults to current directory ('.')",
            value=".",
            tool_mode=True,
        ),
        MultiselectInput(
            name="types",
            display_name="File Types",
            info="File types to load. Select one or more types or leave empty to load all supported types.",
            options=CUSTOM_FILE_TYPES,
            value=[],
        ),
        IntInput(
            name="depth",
            display_name="Depth",
            info="Depth to search for files.",
            value=0,
            advanced=True,
        ),
        BoolInput(
            name="load_hidden",
            display_name="Load Hidden",
            advanced=True,
            info="If true, hidden files will be loaded.",
        ),
        BoolInput(
            name="recursive",
            display_name="Recursive",
            advanced=True,
            info="If true, the search will be recursive.",
        ),
        BoolInput(
            name="silent_errors",
            display_name="Silent Errors",
            advanced=True,
            info="If true, errors will not raise an exception.",
        ),
        BoolInput(
            name="clean_file_path",
            display_name="Clean File Path",
            advanced=True,
            value=True,
            info="Clean File Path by replacing non-alphanumeric characters with underscores.",
        ),
        BoolInput(
            name="excel_header",
            display_name="Excel Header Row",
            info="Use the first row as column headers for Excel files",
            value=False,
            advanced=True
        ),
        DropdownInput(
            name="encoding",
            display_name="File Encoding",
            info="Character encoding of the text file (does not affect Excel files)",
            options=COMMON_ENCODINGS,
            value='utf-8-sig',
            advanced=True
        ),
    ]

    outputs = [
        Output(display_name="Data", name="data", method="load_directory"),
        Output(display_name="DataFrame", name="dataframe", method="as_dataframe"),
    ]

    def load_directory(self) -> list[Data]:
        path = self.path
        types = self.types
        depth = self.depth
        load_hidden = self.load_hidden
        recursive = self.recursive
        silent_errors = self.silent_errors

        resolved_path = self.resolve_path(path)

        # If no types are specified, use all supported types
        if not types:
            types = CUSTOM_FILE_TYPES

        # Check if all specified types are valid
        invalid_types = [t for t in types if t not in CUSTOM_FILE_TYPES]
        if invalid_types:
            msg = f"Invalid file types specified: {invalid_types}. Valid types are: {CUSTOM_FILE_TYPES}"
            raise ValueError(msg)

        valid_types = types

        file_paths = retrieve_file_paths(
            resolved_path,
            load_hidden=load_hidden,
            recursive=recursive,
            depth=depth,
            types=valid_types,
        )

        if types == "eml" and any(file_path.endswith('.eml') for file_path in file_paths):
            # Sort emails with the most recent dates first
            file_paths.sort(key=self._get_email_date, reverse=True)

            # Load the most recent email body
            if file_paths:
                most_recent_email_body = self._get_email_body(file_paths[0])
                self.log(f"Body of the most recent email: {most_recent_email_body}")

        loaded_data = []
        for file_path in file_paths:
            try:
                if file_path.endswith('.xlsx'):
                    loaded_data.append(self._process_excel(file_path, self.clean_file_path))
                elif file_path.endswith('.eml'):
                    loaded_data.extend(self._process_email(file_path))
                else:
                    # Handle other file types as before
                    loaded_data.append(parse_text_file_to_data(file_path, silent_errors=silent_errors))
            except Exception as e:
                if not silent_errors:
                    raise e  # Raise the exception if silent_errors is False
                else:
                    print(f"Error loading file {file_path}: {e}")

        valid_data = [x for x in loaded_data if x is not None and isinstance(x, Data)]
        self.status = valid_data
        return valid_data

    def _process_excel(self, file_path: str, clean_file_path: bool) -> Data:
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
            
            excel_sheet_name = self._get_sheet_name(file_path)

            # Clean file path by removing strange characters
            self.log(f"raw file_path: {file_path}")
            self.log(f"clean_file_path: {clean_file_path}")
            if clean_file_path:
                file_path = self._clean_file_name(str(file_path))
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
    
    def _process_email(self, file_path: str) -> list[Data]:
        """Processes Email files and returns the content in CSV format with ';' separator."""
        try:
            email_docs: list[Document] = self._load_documents_from_eml(file_path)
            email_docs_as_data: list[Data] = [Data.from_document(doc) for doc in email_docs]
            return email_docs_as_data
        except Exception as e:
            self.log(f"Error processing Excel file {file_path}: {str(e)}")
            return None  # Returns None in case of an error
        
    def _clean_file_name(self, file_name: str) -> str:
        """Removes non-alphanumeric characters and replaces them with a safe character."""
        # Replaces non-alphanumeric characters with an underscore
        return re.sub(r'[^a-zA-Z0-9._-]', '_', file_name)
    
    def _get_sheet_name(self, xlsx_path: str) -> str:
        """
        Returns the name of the first sheet in the given Excel file.
        """
        try:
            return pd.ExcelFile(xlsx_path).sheet_names[0]
        except Exception as e:
            self.log(f"get_sheet_name() - Error getting sheet name from file '{xlsx_path}': {e}")
            raise

    def _get_email_date(self, eml_path: str) -> float:
        """
        Extract the date from the EML file and return it as a timestamp.
        
        Args:
            eml_path (str): The path to the EML file.

        Returns:
            The timestamp representing the email date.
            If no date is found or an error occurs, returns -1.
        """
        try:
            with open(eml_path, 'rb') as file:
                msg = email.message_from_binary_file(file)
                date_str = msg.get('Date')
                
                if not date_str:
                    self.log(f"No Date header found in {eml_path}")
                    return -1

                try:
                    # Handle malformed dates with timezone issues
                    date_tuple = email.utils.parsedate_tz(date_str)
                    if date_tuple is None:
                        raise ValueError("Unparseable date format")
                        
                    timestamp = email.utils.mktime_tz(date_tuple)
                    return timestamp
                except Exception as parse_error:
                    # Fallback to parsedate_to_datetime for better parsing
                    try:
                        date_obj = email.utils.parsedate_to_datetime(date_str)
                        return date_obj.timestamp()
                    except Exception as fallback_error:
                        self.log(f"Date parsing failed for {eml_path}: {parse_error}, {fallback_error}")
                        return -1

        except Exception as e:
            self.log(f"Error processing {eml_path}: {str(e)}", exc_info=True)
            return -1
    
    def _get_email_body(self, eml_path: str, default_encoding: str = 'utf-8-sig') -> str:
        """
        Extract the body from the EML file.

        Args:
            eml_path (str): The path to the EML file.
            default_encoding (str, optional): Fallback encoding if part charset isn't specified. 
                Defaults to 'utf-8-sig'.

        Returns:
            The body of the email as a string.
            If no body is found or an error occurs, returns an empty string.        
        """
        try:
            with open(eml_path, 'rb') as file:
                msg = email.message_from_binary_file(file)
                
                # Prefer text/plain parts, fallback to text/html if needed
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type not in ['text/plain', 'text/html']:
                        continue

                    payload = part.get_payload(decode=True)
                    if not payload:
                        continue  # Skip parts with empty payload

                    charset = part.get_content_charset() or default_encoding
                    
                    try:
                        body = payload.decode(charset)
                    except (UnicodeDecodeError, LookupError):
                        try:
                            body = payload.decode(default_encoding)
                        except UnicodeDecodeError:
                            body = payload.decode('latin-1', errors='replace')
                    
                    if content_type == 'text/plain':
                        return body
                
                # If no text/plain found but text/html exists
                for part in msg.walk():
                    if part.get_content_type() == 'text/html':
                        payload = part.get_payload(decode=True)
                        if payload:
                            charset = part.get_content_charset() or default_encoding
                            try:
                                return payload.decode(charset)
                            except (UnicodeDecodeError, LookupError):
                                return payload.decode('latin-1', errors='replace')
                
                # If no body found
                return msg.get_payload(decode=True).decode(msg.get_content_charset() or default_encoding, errors='replace') if not msg.is_multipart() else ""

        except Exception as e:
            self.log(f"Error extracting body from {eml_path}: {e}", exc_info=True)
            return ""
        
    def _get_encoding_of_file(
        self,
        file_path: str,
        default_encoding: str = 'utf-8-sig',
    ) -> str:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            return chardet.detect(raw_data)['encoding'] or default_encoding

    def _load_documents_from_eml(
        self,
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
        encoding = self._get_encoding_of_file(file_path=eml_path, default_encoding=encoding)

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
        email_attachments_filenames = self._extract_attachments_from_eml_file(eml_path)
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
            doc.metadata = self._stringify_non_string_dict_values(doc.metadata)
        
        if log_found_documents:
            self.log("#"*80)
            self.log(f"Processed EML: {eml_path}")
            self.log(f"Detected {len(full_docs)} documents with {len(email_attachments_filenames)} attachments")
            for i, doc in enumerate(full_docs):
                self.log(f"Document {i} metadata: {dict(doc.metadata)}")
            self.log("#"*80)

        return full_docs

    def _extract_attachments_from_eml_file(self, eml_path: str) -> list:
        """
        Returns a list of attachments filenames extracted from the given eml file.
        """
        try:
            with open(eml_path, 'rb') as f:
                msg = BytesParser(policy=policy.default).parsebytes(f.read())
                return [str(part.get_filename()) for part in msg.iter_attachments() if part.get_filename()]
        except Exception as e:
            self.log(f"Attachment extraction failed on file {eml_path}\nError: {e}")
            return []
    
    def _stringify_non_string_dict_values(self, input_dict: dict) -> dict:
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

    def as_dataframe(self) -> DataFrame:
        return DataFrame(self.load_directory())
