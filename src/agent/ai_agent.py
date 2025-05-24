from fastapi import Depends

from src.agent.tools.category_tools import GetListCategoryTool
from src.agent.tools.common_tools import GetDateTool, GetUserIdTool
from src.agent.tools.greet import GreetTool
from src.agent.tools.transaction_tools import CreateTransactionTool, DeleteTransactionTool, FindTransactionTool, UpdateTransactionTool
from src.core.models.message_model import MessageModel
from src.services.llm_service import LLMService, get_llm_service
from src.services.utils import extract_json_from_string


def get_agent(llm_service: LLMService = Depends(get_llm_service)):
	agent = Agent(llm_service)
	agent.add_tool(GreetTool())
	return agent


class Agent:
	def __init__(self, llm_service: LLMService = Depends(get_llm_service)) -> None:
		self.user_id = ""
		self.tools = []
		self.messages = []
		self.memory = []
		self.max_memory = 10
		self.llm_service = llm_service
		self.initialize_tools()
		self.context = None

	def initialize_tools(self):
		self.add_tool(GetDateTool())
		self.add_tool(GetListCategoryTool())
		self.add_tool(CreateTransactionTool())
		self.add_tool(FindTransactionTool())
		self.add_tool(UpdateTransactionTool())
		self.add_tool(DeleteTransactionTool())

	def initialize_prompt(self):
		self.messages = []
		tools_description = "\n".join([f"{tool.name()}: {tool.description()} Args: {tool.get_args_schema()} Output: {tool.output_schema()}" for tool in self.tools])

		self.prompt = f"""
		You are an AI agent that can assist users with their financial transactions. for each task, output exactly:
		Thought: <your reasoning about the task, only one task at a time>
		Action: {{"name": "tool_name", "args": {{"<tool_args>""}}}}

		Repeat steps as needed until you have a final answer.
		Action: {{"name": "final_answer", "args": {{"answer": <your final answer>"}}}}

		You have access to the following tools:
		{tools_description}

		Use only the provided tools. Always response final answer in Bahasa Indonesia. No extra text.
		"""
		self.messages.append({"role": "system", "content": self.prompt})
		self.add_memory(f"System: {self.prompt}")

	def add_tool(self, tool):
		self.tools.append(tool)

	def add_memory(self, memory):
		self.memory.append(memory)
		self.memory = self.memory[-self.max_memory :]

	def process_message(self, message: MessageModel):
		response = self.run(message.to_context(), message.sender_phone_number)
		return response or ""

	def submit_query(self, input: str, role: str = "user"):
		self.add_memory(f"{role}: {input}")
		self.messages.append({"role": role, "content": input})
		response = self.llm_service.query_execute(self.messages, stop=["Observation:", "<|end_of_text|>"])
		return response or ""

	def run(self, input, user_id):
		response = ""
		try:
			self.add_tool(GetUserIdTool(user_id))
			self.initialize_prompt()

			query = input
			# submit the query to the LLM
			response = self.submit_query(query)
			self.messages.append({"role": "assistant", "content": response})

			max_loop = 10
			while max_loop > 0:
				max_loop -= 1
				if "Action:" in response:
					action_name, action_args = self.extract_action_from_response(response)
					if action_name == "final_answer":
						return action_args["answer"]
					for tool in self.tools:
						if tool.name().lower() == action_name.lower():
							result = tool.run(action_args)
							query = f"Observation: {result}"
							break
					# resubmit the query again to the LLM
					response = self.submit_query(query, "user")
					self.messages.append({"role": "assistant", "content": response})
				else:
					print("No action found in response, returning final answer")
					response = self.submit_query("Observation: You not provide the Action on your answer", "user")
					self.messages.append({"role": "assistant", "content": response})
		except Exception as e:
			response = f"""
				{response}
			   	Observation: System Error, direct generate the final answer informed the user that the system is error and apologize for the error."""
			response = self.submit_query(response, "assistant")
			action, action_args = self.extract_action_from_response(response)
			if action == "final_answer":
				return action_args["answer"]

	def extract_action_from_response(self, response):
		json_dict = extract_json_from_string(response)
		action_name = json_dict["name"]
		action_args = json_dict["args"] if json_dict["args"] != "" else {}
		return action_name, action_args
