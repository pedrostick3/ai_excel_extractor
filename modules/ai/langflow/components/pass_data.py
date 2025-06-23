from langflow.custom import Component
from langflow.io import HandleInput, MessageInput, MultilineInput
from langflow.schema import Data, Message
from langflow.template import Output


class PassMessageComponent(Component):
    display_name = "Pass Data"
    description = "Forwards the input Data, unchanged."
    name = "PassData"
    icon = "arrow-right"

    inputs = [
        HandleInput(
            name="input",
            display_name="Input",
            info="The input to be passed forward.",
            input_types=["Data", "Message"],
            required=True,
        ),
        MessageInput(
            name="ignored_message",
            display_name="Ignored Message",
            info="A second message to be ignored. Used as a workaround for continuity.",
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="Output Message", name="output_message", method="pass_message"),
        Output(display_name="Output Data", name="output_data", method="pass_data"),
    ]

    def pass_message(self) -> Message:
        self.status = self.input
        return self.input

    def pass_data(self) -> Data:
        self.status = self.input
        return self.input
