import pytest
from unittest.mock import MagicMock, patch
from src.agent.tools.transaction_tools import FindTransactionTool

@pytest.fixture
def tool():
	return FindTransactionTool()

def test_name_and_description(tool):
	assert tool.name() == "find_transaction"
	assert "natural-language query" in tool.description()

def test_get_args_schema_and_output_schema(tool):
	args_schema = tool.get_args_schema()
	assert isinstance(args_schema, list)
	assert any(arg["name"] == "query" for arg in args_schema)
	assert any(arg["name"] == "user_id" for arg in args_schema)
	assert tool.output_schema() == "str"

def test_run_missing_keys(tool):
	assert tool.run({"query": "find all"}) == "Args should contain 'query' and 'user_id' keys"
	assert tool.run({"user_id": "abc"}) == "Args should contain 'query' and 'user_id' keys"

def test_run_wrong_types(tool):
	assert tool.run({"query": 123, "user_id": "abc"}) == "Args 'query' and 'user_id' should be strings"
	assert tool.run({"query": "find", "user_id": 456}) == "Args 'query' and 'user_id' should be strings"

def test_validate_query_raw_sql_quotes(tool):
	q1 = '"SELECT * FROM transaction WHERE user_id = \'abc\'"'
	q2 = "'SELECT * FROM transaction WHERE user_id = \"abc\"'"
	assert tool.validate_query_raw_sql(q1) == "SELECT * FROM transaction WHERE user_id = 'abc'"
	assert tool.validate_query_raw_sql(q2) == 'SELECT * FROM transaction WHERE user_id = "abc"'

def test_validate_query_raw_sql_invalid(tool):
	assert tool.validate_query_raw_sql("DELETE FROM transaction") == "Query must start with SELECT"
	assert tool.validate_query_raw_sql("SELECT * FROM transaction") == "Query must contain user_id filter"

# Integration test
@patch("src.agent.tools.transaction_tools.get_llm_service")
@patch("src.agent.tools.transaction_tools.get_transaction_repository")
def test_find_transaction_tool_integration(mock_get_repo, mock_get_llm_service):
	# Setup LLM mock
	mock_llm = MagicMock()
	sql = "SELECT * FROM transaction WHERE user_id = 'user123'"
	mock_llm.query_execute.return_value = sql
	mock_get_llm_service.return_value = mock_llm

	# Setup repository mock
	mock_repo = MagicMock()
	mock_repo.findRaw.return_value = [
		{"id": 1, "user_id": "user123", "amount": 100, "type": "income"},
		{"id": 2, "user_id": "user123", "amount": 50, "type": "expense"},
	]
	mock_get_repo.return_value = mock_repo

	tool = FindTransactionTool()
	args = {"query": "show all my transactions", "user_id": "user123"}
	result = tool.run(args)
	assert "user123" in result
	assert "income" in result or "expense" in result
	