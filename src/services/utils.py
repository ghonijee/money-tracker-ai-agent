import json


def extract_json_from_string(string: str) -> dict:
	"""
	Extracts a JSON object from a string. The JSON object is expected to be enclosed in curly braces.

	Args:
	    string (str): The input string containing the JSON object.

	Returns:
	    dict: The extracted JSON object as a dictionary.
	"""
	start = string.find("{")
	end = string.rfind("}") + 1
	json_str = string[start:end]
	return json.loads(json_str)
