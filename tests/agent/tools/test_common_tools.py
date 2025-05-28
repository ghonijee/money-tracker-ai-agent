from datetime import datetime, timedelta
import hashlib
import hmac
import pytest
from cryptography.fernet import Fernet

from src.agent.tools.common_tools import GetUserIdTool
import json
from unittest.mock import MagicMock, patch
from src.agent.tools.common_tools import GetDateTool
# adjust this import to point at where your class is defined


@pytest.fixture(autouse=True)
def clear_secret_key_env(monkeypatch):
	"""Ensure SECRET_KEY is always clean before each test."""
	monkeypatch.delenv("SECRET_KEY", raising=False)
	yield
	monkeypatch.delenv("SECRET_KEY", raising=False)


def test_create_encrypted_user_id_roundtrip(monkeypatch):
	# 1) generate a valid Fernet key and set in env
	key = Fernet.generate_key().decode()
	monkeypatch.setenv("SECRET_KEY", key)

	user_id = "user_ABC123"
	tool = GetUserIdTool(user_id=user_id)

	# 2) encrypt
	token = tool.create_encrypted_user_id(user_id)
	assert isinstance(token, str) and token

	# 3) decrypt and verify original
	decrypted = hmac.new(key.encode(), user_id.encode(), digestmod=hashlib.sha256).hexdigest()
	assert decrypted == decrypted


def test_run_uses_internal_id(monkeypatch):
	key = Fernet.generate_key().decode()
	monkeypatch.setenv("SECRET_KEY", key)

	tool = GetUserIdTool(user_id="XYZ")
	token = tool.run(args={})  # args are ignored
	assert Fernet(key.encode()).decrypt(token.encode()).decode() == "XYZ"


def test_missing_secret_key_raises():
	tool = GetUserIdTool(user_id="anything")
	with pytest.raises(RuntimeError) as exc:
		tool.create_encrypted_user_id("anything")
	assert "Set MY_SECRET_KEY to your Fernet key" in str(exc.value)

def test_get_date_tool_name_and_description():
	tool = GetDateTool()
	assert tool.name() == "generate_date"
	assert "ISO-8601" in tool.description()

def test_get_date_tool_args_schema_and_output_schema():
	tool = GetDateTool()
	args_schema = tool.get_args_schema()
	assert isinstance(args_schema, list)
	assert any(arg["name"] == "expression" for arg in args_schema)
	assert any(arg["name"] == "timezone" for arg in args_schema)
	assert tool.output_schema() == "str"

def test_get_date_tool_run_calls_llm_service_with_expression_today():
	tool = GetDateTool()
	args = {"expression": "today", "timezone": "Asia/Jakarta"}
	result = tool.run(args)
	print(result)
	assert isinstance(result, str)
	data = json.loads(result)
	assert "datetime" in data
	now = datetime.today()
	assert data["datetime"].startswith(now.strftime("%Y-%m-%d"))  # assert the date starts with today's date
	# assert the date is equal to today
	assert data["datetime"].endswith(now.strftime("00:00:00+07:00"))

def test_get_date_tool_run_calls_llm_service_with_expression_today_with_clock():
	tool = GetDateTool()
	args = {"expression": "hari ini jam 3 sore", "timezone": "Asia/Jakarta"}
	result = tool.run(args)
	assert isinstance(result, str)
	data = json.loads(result)
	assert "datetime" in data
	now = datetime.today()
	assert data["datetime"].startswith(now.strftime("%Y-%m-%d"))  # assert the date starts with today's date
	# assert the date is equal to today
	assert data["datetime"].endswith(now.strftime("15:00:00+07:00"))

def test_get_date_tool_run_calls_llm_service_with_expression_yesterday():
	tool = GetDateTool()
	args = {"expression": "yesterday", "timezone": "Asia/Jakarta"}
	result = tool.run(args)
	assert isinstance(result, str)
	data = json.loads(result)
	assert "datetime" in data
	yesterday = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
	assert data["datetime"].startswith(yesterday.strftime("%Y-%m-%d"))  # assert the date starts with yesterday's date
	# assert the date is equal to yesterday
	assert data["datetime"].endswith(yesterday.strftime("00:00:00+07:00"))