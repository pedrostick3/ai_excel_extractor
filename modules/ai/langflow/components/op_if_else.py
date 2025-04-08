import re
from langflow.custom import Component
from langflow.io import DropdownInput, IntInput, MessageInput, MessageTextInput, BoolInput, Output
from langflow.schema.message import Message


class ConditionalRouterComponent(Component):
    display_name = "OP If-Else"
    description = "Routes an input message to a corresponding output based on text comparison."
    icon = "split"
    name = "ConditionalRouter"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__iteration_updated = False

    inputs = [
        MessageTextInput(
            name="input_text",
            display_name="Text Input",
            info="The primary text input for the operation.",
            required=True,
        ),
        MessageTextInput(
            name="match_text",
            display_name="Match Text",
            info="The text input to compare against.",
            required=False,
        ),
        DropdownInput(
            name="operator",
            display_name="Operator",
            options=["equals", "not equals", "contains", "starts with", "ends with", "regex"],
            info="The operator to apply for comparing the texts.",
            value="equals",
            real_time_refresh=True,
        ),
        BoolInput(
            name="case_sensitive",
            display_name="Case Sensitive",
            info="If true, the comparison will be case sensitive.",
            value=False,
        ),
        MessageInput(
            name="message",
            display_name="Message",
            info="The message to pass through either route.",
        ),
        MessageTextInput(
            name="pass_message_on_true",
            display_name="Pass Message on True",
            info="The message to pass when the condition is met.",
            required=False,
        ),
        MessageTextInput(
            name="pass_message_on_false",
            display_name="Pass Message on False",
            info="The message to pass when the condition is not met.",
            required=False,
        ),
        MessageTextInput(
            name="pass_message_on_empty",
            display_name="Pass Message on Empty",
            info="The message to pass when input_text is empty.",
            required=False,
        ),
        IntInput(
            name="max_iterations",
            display_name="Max Iterations",
            info="The maximum number of iterations for the conditional router.",
            value=10,
            advanced=True,
        ),
        DropdownInput(
            name="default_route",
            display_name="Default Route",
            options=["true_result", "false_result"],
            info="The default route to take when max iterations are reached.",
            value="false_result",
            advanced=True,
        ),
    ]

    outputs = [
        Output(display_name="True", name="true_result", method="true_response"),
        Output(display_name="False", name="false_result", method="false_response"),
        Output(display_name="Empty Input", name="empty_input", method="empty_response"),
    ]

    def _pre_run_setup(self):
        self.__iteration_updated = False

    def _evaluate_condition(self, input_text: str, match_text: str, operator: str, *, case_sensitive: bool) -> bool:
        if match_text is None:
            return False
        
        if not case_sensitive and operator != "regex":
            input_text = input_text.lower()
            match_text = match_text.lower()

        if operator == "equals":
            return input_text == match_text
        if operator == "not equals":
            return input_text != match_text
        if operator == "contains":
            return match_text in input_text
        if operator == "starts with":
            return input_text.startswith(match_text)
        if operator == "ends with":
            return input_text.endswith(match_text)
        if operator == "regex":
            try:
                return bool(re.match(match_text, input_text))
            except re.error:
                return False  # Return False if the regex is invalid
        return False

    def _iterate_and_stop_once(self, route_to_stop: str):
        if not self.__iteration_updated:
            self.update_ctx({f"{self._id}_iteration": self.ctx.get(f"{self._id}_iteration", 0) + 1})
            self.__iteration_updated = True
            if self.ctx.get(f"{self._id}_iteration", 0) >= self.max_iterations and route_to_stop == self.default_route:
                route_to_stop = "true_result" if route_to_stop == "false_result" else "false_result"
            self.stop(route_to_stop)

    def true_response(self) -> Message:
        result = self._evaluate_condition(self.input_text, self.match_text, self.operator, case_sensitive=self.case_sensitive)
        
        if not result:
            return Message()
        
        if result and self.pass_message_on_true:
            return Message(text=self.pass_message_on_true)
        
        self._iterate_and_stop_once("true_result")
        return Message(text="Condition met but no message provided.")

    def false_response(self) -> Message:
        result = self._evaluate_condition(self.input_text, self.match_text, self.operator, case_sensitive=self.case_sensitive)

        if result:
            return Message()
        
        if not result and self.pass_message_on_false:
            return Message(text=self.pass_message_on_false)
        
        self._iterate_and_stop_once("false_result")
        return Message(text="Condition not met but no message provided.")
    
    def empty_response(self) -> Message:
        if self.input_text.strip():
            return Message()
        
        if self.pass_message_on_empty:
            return Message(text=self.pass_message_on_empty)
        
        return Message(text="Input text is empty but no message provided.")
