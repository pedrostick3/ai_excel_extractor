import pandas as pd

class PoC4Utils:
    temp_vars: dict[str, str] = {}
    
    @staticmethod
    def update_temp_vars(x: dict[str, str]):
        PoC4Utils.temp_vars.update(x)

    @staticmethod
    def reset_temp_vars():
        PoC4Utils.temp_vars = {}
    
    @staticmethod
    def get_non_empty_values(map:dict) -> list:
        return [value for value in map.values() if not pd.isna(value) and value != "" and value != "None"]
