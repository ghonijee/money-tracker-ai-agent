from fastapi import Depends
from jinja2 import Template
from sqlalchemy import null
import yaml

from src.agent.memory_management import MemoryManagement
from src.agent.tools.category_tools import GetListCategoryTool
from src.agent.tools.common_tools import GetDateTool, ImageExtractInformationTool
from src.agent.tools.greet import GreetTool
from src.agent.tools.transaction_tools import CreateTransactionTool, DeleteTransactionTool, FindTransactionTool, UpdateTransactionTool
from src.core.models.message_model import MessageModel
from src.services.llm_service import LLMService, get_llm_service
from src.services.utils import extract_json_from_string

## TODO: Add memory management to the agent
## 1. Insert memory to the database
## 2. Retrieve memory from the database
## 3. Summarize memory
## 4. Inject memory into the prompt


def get_agent(llm_service: LLMService = Depends(get_llm_service)):
	agent = Agent(llm_service)
	return agent


class Agent:
	def __init__(self, llm_service: LLMService = Depends(get_llm_service)) -> None:
		self.llm_service = llm_service
		self.memory = MemoryManagement(llm_service)
		self.user_memory = null
		self.user_id = ""
		self.tools = []
		self.messages = []
		self.max_memory = 10
		self.max_iterations = 0
		self.max_retry_on_error = 3
		self.initialize_tools()
		self.model_selected = self.llm_service.get_random_model()

	def initialize_tools(self):
		self.add_tool(ImageExtractInformationTool())
		self.add_tool(GetDateTool())
		self.add_tool(GetListCategoryTool())
		self.add_tool(CreateTransactionTool())
		self.add_tool(FindTransactionTool())
		self.add_tool(UpdateTransactionTool())
		self.add_tool(DeleteTransactionTool())

	def initialize_prompt(self):
		tools_description = "\n".join([f"{tool.name()}: {tool.description()} Args: {tool.get_args_schema()} Output: {tool.output_schema()}" for tool in self.tools])

		template = yaml.safe_load(open("src/agent/prompt/system_prompt.yaml", "r"))
		self.prompt = Template(template["system_prompt"]["v4"]).render(tools_description=tools_description, user_memory=self.user_memory)
		self.messages.append({"role": "system", "content": self.prompt})

	def add_tool(self, tool):
		self.tools.append(tool)

	def add_memory(self, role, content):
		self.memory.add_memory(self.user_id, role, content)

	def add_message(self, role: str, content: str):
		print(f"{role} : {content}")
		self.messages.append({"role": role, "content": content})

	def process_message(self, message: MessageModel):
		self.user_id = message.user_id
		self.user_memory = self.memory.summarize_memory(self.user_id, self.max_memory)
		self.initialize_prompt()
		self.memory.add_memory(self.user_id, "user", message.message_content)
		response = self.run(message.to_context())
		self.memory.add_memory(self.user_id, "assistant", response or '')
		return response or ""

	def submit_query(self, input: str, role: str = "user"):
		self.add_message(role=role, content=input)
		response = self.llm_service.query_execute(self.messages, stop=["<STOP>"], model=self.model_selected)
		return response or ""

	def run(self, input, max_iterations: int = 10):
		response = ""
		try:
			self.max_iterations = max_iterations
			query = input
			while self.max_iterations > 0:
				response = self.submit_query(query)
				self.add_message("assistant", response)
				self.max_iterations -= 1
				if "Action:" in response:
					action_name, action_args = self.extract_action_from_response(response)
					if action_name == "final_answer":
						return action_args["answer"]
					for tool in self.tools:
						if tool.name().lower() == action_name.lower():
							result = tool.run(action_args)
							query = f"Observation: {result}"
							break
				else:
					query = "Observation: You not provide the Action on your answer. Provide the Action in your answer to continue the process. If you want to finish the process, provide the final_answer action with the answer."
		except Exception as e:
			if self.max_retry_on_error > 0:
				response = f"""
			   	Observation: System Error {e}, please try again"""
				self.max_retry_on_error -= 1
				return self.run(response, max_iterations=self.max_iterations)
			else:
				response = """
			   	Observation: System Error, direct generate the final answer informed the user that the system is error and apologize for the error."""
				return self.run(response, max_iterations=1)

	def extract_action_from_response(self, response):
		json_dict = extract_json_from_string(response)
		action_name = json_dict["name"]
		action_args = json_dict["args"] if json_dict["args"] != "" else {}
		return action_name, action_args
