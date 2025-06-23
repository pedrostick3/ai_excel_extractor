import ast
import json
from langflow.custom import Component
from langflow.io import DataInput, BoolInput, Output
from langflow.schema import Data


class MergeStringDictListComponent(Component):
    display_name = "Combine Dict List into Dict"
    description = "Combines a list[dict] received as string into a single dict."
    icon = "merge"

    inputs = [
        DataInput(
            name="data_inputs",
            display_name="Data Inputs",
            info="Data to combine",
            is_list=True,
            required=True
        ),
        BoolInput(
            name="convert_text_to_json",
            display_name="Convert Text to JSON",
            advanced=True,
            value=False,
            info="If true, the component will convert text inputs to JSON.",
        ),
    ]
    outputs = [Output(display_name="Data", name="combined_data", method="combine_data")]

    def combine_data(self) -> Data:
        self.log(f"self.data_inputs = {self.data_inputs}")
        combined_data = {}

        # Iterate over the list of Data objects
        for data_input in self.data_inputs:
            input_str = data_input.text  # Access the string representation of the Data object
            self.log(f"input_str = {input_str}")

            if not input_str:
                self.log("Skipped empty input string.")
                continue  # Skip empty strings

            try:
                # Parse the string
                list_of_dict_strs = ast.literal_eval(input_str)
                parsed_data = [json.loads(dict_str) for dict_str in list_of_dict_strs]
                self.log(f"parsed_data = {parsed_data}")
                
                if isinstance(parsed_data, dict):
                    self.log(f"parsed_data is dict = {parsed_data}")
                    # Merge the dictionaries
                    combined_data.update(parsed_data)
                elif isinstance(parsed_data, list):
                    self.log(f"parsed_data is list = {parsed_data}")
                    for dict_item in parsed_data:
                        if isinstance(dict_item, dict):
                            combined_data.update(dict_item)
                        else:
                            self.log(f"Item '{dict_item}' is not a valid dictionary.")
                else:
                    self.log(f"Input '{input_str}' is not a valid dictionary.")
            except (json.JSONDecodeError, SyntaxError, ValueError) as e:
                self.log(f"Error parsing input '{input_str}': {e}")

        self.log(f"combined_data = {combined_data}")

        if self.convert_text_to_json:
            # Convert the combined dictionary back to a JSON string with proper Unicode handling
            combined_json_str = json.dumps(combined_data, ensure_ascii=False)
            self.log(f"combined_json_str = {combined_json_str}")
            to_return = Data(text=combined_json_str)
        else:
            to_return = Data(text=str(combined_data))
        
        to_return.data.update(combined_data)  # Update the data attribute with the combined dictionary

        return to_return
