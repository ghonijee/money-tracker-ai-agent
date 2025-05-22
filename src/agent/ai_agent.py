import json
from fastapi import Depends

from src.agent.tools.category_tools import GetListCategoryTool
from src.agent.tools.common_tools import GetDateTool, GetUserIdTool
from src.agent.tools.greet import GreetTool
from src.agent.tools.transaction_tools import CreateTransactionTool, DeleteTransactionTool, FindTransactionTool, UpdateTransactionTool
from src.core.models.message_model import MessageModel
from src.services.llm_service import LLMService, get_llm_service


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
		# self.add_tool(GreetTool())
		self.add_tool(GetDateTool())
		self.add_tool(GetListCategoryTool())
		self.add_tool(CreateTransactionTool())
		self.add_tool(FindTransactionTool())
		self.add_tool(UpdateTransactionTool())
		self.add_tool(DeleteTransactionTool())

	def initialize_prompt(self):
		tools_description = "\n".join([f"{tool.name()}: {tool.description()} Args: {tool.get_args_schema()} Output: {tool.output_schema()}" for tool in self.tools])

		self.prompt = f"""You are a helpful assistant named "Agent Ali" designed to help users effectively and accurately.
		
		You have access to the following tools:
		{tools_description}

		Use the tool when necessary to answer the user's question or solve the task. The way you use the tools is by specifying a JSON. This example is a valid JSON that uses the tool 'greet':
		{{"action": "greet", "args": {{}}}}

		You must call the `get_user_id` tool to retrieve the user ID for the transaction, and do so only once.
		You must call the `generate_date` tool only once to retrieve the date for the transaction, when the date is not fully defined in the input.

		You should think step by step in order to fulfill the objective with reasoing divide into Thought, Action, and Observation.
		You should always use the following format:

		Question: the input question you must answer/process.
		Thought: you should always think about one action to take. Only one action at a time in this format.
		Action: $JSON (This is the JSON that contains the action and arguments to call the tool, only JSON without markdown)
		Observation: the result of the action. This Observation is unique, complete, and the source of truth.

		... (this Thought/Action/Observation can repeat N times, you should take several steps when needed)

		If you have the answer, you must always response with the following format:

		Thought: I now know the final answer
		Final Answer: The final answer to the user's input. give the refID (ID) if user want to see the transaction details. 
		
		Analyze, summarize the answer and give the final answer using friendly and concise style.
		Begin! Reminder to always use the exact characters `Final Answer: ` when you provide the final answer.
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
		response = self.llm_service.query_execute(self.messages, stop=["Observation:"])
		return response or ""

	def run(self, input, user_id):
		self.add_tool(GetUserIdTool(user_id))
		self.initialize_prompt()

		query = input
		# submit the query to the LLM
		response = self.submit_query(query)
		isFinalResponse = False
		max_loop = 10

		while not isFinalResponse and max_loop > 0:
			max_loop -= 1
			print("Response: ", response)
			if "Final Answer:" in response:
				isFinalResponse = True
				print(self.messages)
				return response.split("Final Answer:")[1].strip()
			elif "Action:" in response:
				json_blob = response.split("Action:")[1]
				json_dict = self.json_parser(json_blob)
				# # get the action name from the dictionary
				action_name = json_dict["action"]
				# # get the arguments from the dictionary
				if json_dict["args"] == "":
					action_args = {}
				else:
					action_args = json_dict["args"]
				print("Action: ", action_name)
				print("Args: ", action_args)
				# check if the action is a tool
				for tool in self.tools:
					if tool.name().lower() == action_name.lower():
						result = tool.run(action_args)
						print("result: of tool ", result)

						# append result tool to response
						response += " Observation: " + result

						self.add_memory(f"Assistant: {response}")
						query = response
						break

				# submit the query again to the LLM
				print("Query: ", query)
				response = self.submit_query(query, "assistant")

	def json_parser(self, input_string):
		clean = input_string.strip()
		try:
			# python_dict = ast.literal_eval(input_string)
			# json_string = json.dumps(python_dict)
			json_dict = json.loads(clean)
			return json_dict
		except Exception as e:
			print(e)
			print(input_string)
			raise Exception("Invalid JSON")
