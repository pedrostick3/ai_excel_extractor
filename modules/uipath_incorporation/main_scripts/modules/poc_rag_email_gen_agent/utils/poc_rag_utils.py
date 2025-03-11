import email
import logging

class PoCRagUtils:
    @staticmethod
    def get_email_date(eml_path: str, encoding: str = 'utf-8-sig') -> float:
        """
        Extract the date from the EML file and return it as a timestamp.
        
        Args:
            eml_path (str): The path to the EML file.
            encoding (str, optional): Encoding for the EML file. Defaults to 'utf-8-sig'.

        Returns:
            The timestamp representing the email date.
            If no date is found or an error occurs, returns -1.
        """
        try:
            with open(eml_path, 'r', encoding=encoding) as file:
                msg = email.message_from_file(file)
                date_str = msg.get('Date')
                if date_str:
                    return email.utils.parsedate_to_datetime(date_str).timestamp()
        except UnicodeDecodeError:
            # If encoding fails, try with 'ISO-8859-1' encoding
            with open(eml_path, 'r', encoding='ISO-8859-1') as file:
                msg = email.message_from_file(file)
                date_str = msg.get('Date')
                if date_str:
                    return email.utils.parsedate_to_datetime(date_str).timestamp()
        except Exception as e:
            logging.error(f"Error processing {eml_path}: {e}")

        return -1
    
    @staticmethod
    def get_email_body(eml_path: str, encoding: str ='utf-8-sig') -> str:
        """
        Extract the body from the EML file.

        Args:
            eml_path (str): The path to the EML file.
            encoding (str, optional): Encoding for the EML file. Defaults to 'utf-8-sig'.

        Returns:
            The body of the email as a string.
            If no body is found or an error occurs, returns an empty string.        
        """
        try:
            with open(eml_path, 'r', encoding=encoding) as file:
                msg = email.message_from_file(file)
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == 'text/plain': # can be 'text/plain' or 'text/html'
                            return part.get_payload(decode=True).decode(encoding)
                else:
                    return msg.get_payload(decode=True).decode(encoding)
        except Exception as e:
            logging.error(f"Error extracting body from {eml_path}: {e}")

        return ""
