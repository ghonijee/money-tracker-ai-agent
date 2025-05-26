import ast
import hashlib
import hmac
import json
import os


def extract_json_from_string(string: str) -> dict:
	"""
	Extracts a JSON object from a string. The JSON object is expected to be enclosed in curly braces.

	Args:
	    string (str): The input string containing the JSON object.

	Returns:
	    dict: The extracted JSON object as a dictionary.
	"""
	# validate the JSON string
	if not isinstance(string, str):
		raise ValueError("Input must be a string")
	if "{" not in string or "}" not in string:
		raise ValueError("Input string does not contain a valid JSON object")

	start = string.find("{")
	end = string.rfind("}") + 1
	json_str = string[start:end]
	json_dict = ast.literal_eval(json_str)
	if not isinstance(json_dict, dict):
		raise ValueError("Extracted JSON is not a valid dictionary")
	json_str = json.dumps(json_dict)
	return json.loads(json_str)


def create_encrypted_user_id(user_id: str) -> str:
	secret_key = os.getenv("SECRET_KEY")
	if not secret_key:
		raise RuntimeError("Set SECRET_KEY for encryption!")
	digest = hmac.new(secret_key.encode(), user_id.encode(), digestmod=hashlib.sha256).hexdigest()
	return digest
