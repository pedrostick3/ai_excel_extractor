import json
from langflow.custom import Component
from langflow.io import HandleInput, Output
from langflow.schema import Data

class LoopThroughDictionaryComponent(Component):
    display_name: str = "Loop Through Dictionary"
    description: str = "Iterate through a dictionary and format the output."
    icon = "infinity"
    name = "LoopThroughDictionary"

    inputs = [
        HandleInput(
            name="str_map",
            display_name="Input Map",
            info="A dictionary to iterate over.",
            input_types=["Data"],
            required=True,
        ),
    ]

    outputs = [
        Output(display_name="Item", name="item", method="item_output", allows_loop=True),
        Output(display_name="Done", name="done", method="done_output"),
    ]

    def _initialize_data(self) -> None:
        """Initialize the data dictionary, context index, and aggregated list."""
        if self.ctx.get(f"{self._id}_initialized", False):
            return

        # Ensure data is a dictionary
        if not self.str_map:
            raise ValueError("Input Map is empty or None.")
        data_dict:dict[str, str] = self._validate_data(self.str_map)

        # Store the initial data and context variables
        self.update_ctx(
            {
                f"{self._id}_data": data_dict,
                f"{self._id}_keys": list(data_dict.keys()),
                f"{self._id}_index": 0,
                f"{self._id}_aggregated": [],
                f"{self._id}_initialized": True,
            }
        )

    def _validate_data(self, data: Data):
        """Validate and return a dictionary."""
        self.log(f"data.text = {data.text}")

        # Check if the input is a Data object and extract the dictionary
        if isinstance(data, Data):
            # Log the types of data.text
            self.log(f"isinstance(data.text, dict) = {isinstance(data.text, dict)}")
            self.log(f"isinstance(data.text, str) = {isinstance(data.text, str)}")

            # Check if data.text is a string
            if isinstance(data.text, str):
                try:
                    # Check if the string starts and ends with single quotes
                    if data.text.startswith("'") and data.text.endswith("'"):
                        # Replace the outer single quotes with double quotes
                        json_string = '"' + data.text[1:-1].replace("'", '"') + '"'
                    else:
                        json_string = data.text.replace("'", '"')

                    # Attempt to parse the string as JSON
                    data_dict = json.loads(json_string)
                    self.log(f"data_dict = {data_dict}")
                    self.log(f"isinstance(data_dict, dict) = {isinstance(data_dict, dict)}")

                    if isinstance(data_dict, dict):
                        self.log(f"Parsed data is a valid dictionary.")
                        return data_dict
                    else:
                        raise TypeError("Parsed data is not a dictionary.")
                except json.JSONDecodeError as e:
                    raise TypeError(f"Failed to parse input data as JSON: {e}")
                except Exception as e:
                    raise TypeError(f"An error occurred while processing input data: {e}")
            elif isinstance(data.text, dict):
                # If data.text is a dictionary, return it directly
                return data.text
            else:
                raise TypeError("data.text is not a string or a dictionary.")
        
        # Check if data is already a dictionary
        if isinstance(data, dict):
            return data

        msg = "The 'data' input must be a Data object or a dictionary."
        raise TypeError(msg)

    def _evaluate_stop_loop(self) -> bool:
        """Evaluate whether to stop item or done output."""
        current_index = self.ctx.get(f"{self._id}_index", 0)
        keys_length = len(self.ctx.get(f"{self._id}_keys", []))
        return current_index > keys_length

    def item_output(self) -> Data:
        """Output the next key-value pair in the dictionary or stop if done."""
        self._initialize_data()
        current_item = Data(text="")

        if self._evaluate_stop_loop():
            self.stop("item")
            return Data(text="")

        # Get data dictionary and current index
        data_dict:dict[str, str] = self.ctx.get(f"{self._id}_data", {})
        keys = self.ctx.get(f"{self._id}_keys", [])
        current_index = self.ctx.get(f"{self._id}_index", 0)

        if current_index < len(keys):
            # Get the current key and value
            current_key = keys[current_index]
            current_value = data_dict[current_key]
            current_item = Data(
                text=f"{current_key}: {current_value}",
                key=current_key,
                value=current_value,
            )
        
        self.log(f"item_output - #1 data_dict = {data_dict}")
        self.log(f"item_output - #2 self.item = {self.item}")

        self._aggregated_output()
        self.update_ctx({f"{self._id}_index": current_index + 1})
        return current_item  # Return the Data object directly

    def done_output(self) -> Data:
        """Trigger the done output when iteration is complete."""
        self._initialize_data()

        if self._evaluate_stop_loop():
            self.stop("item")
            self.start("done")

            return Data(text=str(self.ctx.get(f"{self._id}_aggregated", [])))
        self.stop("done")
        return Data(text="")

    def _aggregated_output(self) -> Data:
        """Return the aggregated list once all items are processed."""
        # Get data dictionary and aggregated list
        data_dict = self.ctx.get(f"{self._id}_data", {})
        aggregated = self.ctx.get(f"{self._id}_aggregated", [])

        # Check if loop input is provided and append to aggregated list
        self.log(f"_aggregated_output - #1 data_dict = {data_dict}")
        self.log(f"_aggregated_output - #2 aggregated = {aggregated}")
        self.log(f"_aggregated_output - #3 self.item = {self.item}")
        self.log(f"_aggregated_output - #4 self.item = {type(self.item)}")
        
        if self.item is not None:  # Ensure item is not None
            aggregated.append(self.item.text)  # Access the text of the Data object
            self.update_ctx({f"{self._id}_aggregated": aggregated})
        return Data(text=str(aggregated))  # Return the aggregated list as a Data object
