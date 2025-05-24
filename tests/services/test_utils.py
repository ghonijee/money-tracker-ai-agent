import json
import pytest
from src.services.utils import extract_json_from_string


def test_extract_json_from_string_simple():
	input_str = '{"key": "value"}'
	expected = {"key": "value"}
	assert extract_json_from_string(input_str) == expected


def test_extract_json_from_string_with_prefix():
	input_str = 'Some text before {"key": "value"}'
	expected = {"key": "value"}
	assert extract_json_from_string(input_str) == expected


def test_extract_json_from_string_with_suffix():
	input_str = '{"key": "value"} and some text after'
	expected = {"key": "value"}
	assert extract_json_from_string(input_str) == expected


def test_extract_json_from_string_complex():
	input_str = 'Start {"name": "John", "age": 30, "city": {"name": "New York", "country": "USA"}} End'
	expected = {"name": "John", "age": 30, "city": {"name": "New York", "country": "USA"}}
	assert extract_json_from_string(input_str) == expected


def test_extract_json_from_string_invalid():
	with pytest.raises(json.JSONDecodeError):
		extract_json_from_string('{"invalid": "json"')
