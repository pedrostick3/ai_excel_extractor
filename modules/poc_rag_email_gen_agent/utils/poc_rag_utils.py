import email
import logging
from modules.ai.agents.vectordb_embeddings_agent.utils.vectordb_embeddings_loader_utils import VectordbEmbeddingsLoaderUtils

class PoCRagUtils:
    @staticmethod
    def get_email_date(eml_path: str) -> float:
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
                    logging.warning(f"No Date header found in {eml_path}")
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
                        logging.error(f"Date parsing failed for {eml_path}: {parse_error}, {fallback_error}")
                        return -1

        except Exception as e:
            logging.error(f"Error processing {eml_path}: {str(e)}", exc_info=True)
            return -1
    
    @staticmethod
    def get_email_body(eml_path: str, default_encoding: str = 'utf-8-sig') -> str:
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
            logging.error(f"Error extracting body from {eml_path}: {e}", exc_info=True)
            return ""
