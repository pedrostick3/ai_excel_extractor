from langflow.custom import Component
from langflow.io import MultilineInput, Output
from langflow.schema.message import Message

class RemoveLinesComponent(Component):
    display_name = "Remove Lines"
    description = "Remove lines from a text based on a specified string."
    icon = "code"
    name = "RemoveLines"

    inputs = [
        MultilineInput(
            name="text",
            display_name="Input Text",
            info="The text to process.",
            value="{text}",
            required=True,
        ),
        MultilineInput(
            name="remove_string",
            display_name="String to Remove",
            info="The string to remove from the text.",
            value="{text}",
            required=True,
        ),
    ]

    outputs = [
        Output(display_name="Processed Text", name="processed_text", method="process_text"),
    ]
    
    def process_text(self) -> Message:
        """Remove lines from the text based on the specified string."""
        text = self.text
        remove_string = self.remove_string

        # Split the text into lines
        lines = text.splitlines()

        # Filter out lines that match the remove string
        filtered_lines = [line for line in lines if line != remove_string]

        # Join the filtered lines back into a string
        processed_text = "\n".join(filtered_lines)

        return Message(text=processed_text, templates_list=processed_text)