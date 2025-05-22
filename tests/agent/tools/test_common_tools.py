import hashlib
import hmac
import pytest
from cryptography.fernet import Fernet

from src.agent.tools.common_tools import GetUserIdTool

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
