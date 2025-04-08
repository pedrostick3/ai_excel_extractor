from langflow.custom import Component
from langflow.io import MultilineInput, Output
from langflow.schema.message import Message
from langchain.output_parsers import StructuredOutputParser, ResponseSchema


class FormatInstructionsComponent(Component):
    display_name = "Local Structured Output"
    description = "Format instructions for structured output."
    name = "StructuredOutput"
    icon = "braces"

    inputs = [
        MultilineInput(
            name="output_map_name",
            display_name="Output Map Name",
            info="The output map name to store the formated data.",
            value="{text}",
            required=True,
        ),
        MultilineInput(
            name="name_description",
            display_name="Name Description",
            info="The output map name description to format the data.",
            value="{text}",
            required=True,
        ),
    ]

    outputs = [
        Output(
            display_name="Format Instructions",
            name="text",
            info="Format Instructions as a single text Message",
            method="format_instructions",
        ),
    ]

    def format_instructions(self) -> Message:
        email_questions_parser = StructuredOutputParser.from_response_schemas([
            ResponseSchema(name=self.output_map_name, description=self.name_description),
        ])
        return Message(text=email_questions_parser.get_format_instructions())
