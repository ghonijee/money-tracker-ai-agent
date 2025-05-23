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
		self.messages = []
		tools_description = "\n".join([f"{tool.name()}: {tool.description()} Args: {tool.get_args_schema()} Output: {tool.output_schema()}" for tool in self.tools])

		self.prompt = f"""You are an expert assistant who can solve any task using thinking what step should be and tool calls. You will be given a task to solve as best you can.
  		To do so, you have been given access to some tools.
		  
		The tool call you write is an action: after the tool is executed, you will get the result of the tool call as an "observation".
  		This Action/Observation can repeat N times, you should take several steps when needed.
		  
		You can use the result of the previous action as input for the next action.
		The observation will always be a string.
		Then you can use it as input for the next action. You can do it for instance as follows:

		Thought: I need to get the user ID for the transaction.
		Action: {{"name": "get_user_id", "args": {{}}}}
		Observation: "useridrandomstring"

		Thought: I need to greet the user.
		Action: {{"name": "greet", "args": {{"user_id": "useridrandomstring"}}}}

		To provide the final answer to the task, use an action blob with "name": "final_answer" tool. It is the only way to complete the task, else you will be stuck on a loop. So your final output should look like this:
		Action:
		{{"name": "final_answer",
			"arguments": {{"answer": "insert your final answer here"}}
		}}

		Here are a few examples using notional tools:
		---
		Task: "What is the result of the following operation: 5 + 3 + 1294.678?"
		Thought: I need to calculate the result of the operation.
		Action:
		{{"name": "python_interpreter",
			"arguments": {{"code": "5 + 3 + 1294.678"}}
		}}
		Observation: 1302.678

		Thought: I now know the final answer
		Action:
		{{
			"name": "final_answer",
			"arguments": "1302.678"
		}}

		---
		Task: "Which city has the highest population , Guangzhou or Shanghai?"
		Thought: I need to get the population of Guangzhou.
		Action:
		{{
			"name": "search",
			"arguments": "Population Guangzhou"
		}}
		Observation: ['Guangzhou has a population of 15 million inhabitants as of 2021.']

		Thought: I need to get the population of Shanghai.
		Action:
		{{
			"name": "search",
			"arguments": "Population Shanghai"
		}}
		Observation: '26 million (2019)'

		Thought: I now know the final answer
		Action:
		{{"name": "final_answer",
			"arguments": "Shanghai"
		}}

		---
		Above example were using notional tools that might not exist for you. You only have access to these tools:
		{tools_description}

		Here are the rules you should always follow to solve your task:
		1. ALWAYS provide a tool call, else you will fail.
		2. Always use the right arguments for the tools. Never use variable names as the action arguments, use the value instead.
		3. Call a tool only when needed: do not call the search agent if you do not need information, try to solve the task yourself. If no tool call is needed, use final_answer tool to return your answer.
		4. Never re-do a tool call that you previously did with the exact same parameters.
		5. Always use the `get_user_id` tool to retrieve the user ID for the transaction
		6. Always use the `generate_date` tool to retrieve the date for the transaction, when the date is not fully defined in the input.
		7. Analyze, summarize the answer and give the final answer using friendly and concise style and generate answer targeted to the user input source.

		Now Begin!
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
		self.add_tool(GetUserIdTool(user_id))
		self.initialize_prompt()

		query = input
		# submit the query to the LLM
		response = self.submit_query(query)
		isFinalResponse = False
		max_loop = 10
		while max_loop > 0:
			max_loop -= 1
			if "Action:" in response:
				json_blob = response.split("Action:")[1].split("Observation:")[0].strip()
				json_dict = self.json_parser(json_blob)
				# # get the action name from the dictionary
				action_name = json_dict["name"]
				# # get the arguments from the dictionary
				if json_dict["args"] == "":
					action_args = {}
				else:
					action_args = json_dict["args"]
				# check if the action is a tool
				if action_name == "final_answer":
					# get the final answer
					return json_dict["args"]["answer"]

				for tool in self.tools:
					if tool.name().lower() == action_name.lower():
						result = tool.run(action_args)
						# append result tool to response
						response += " Observation: " + result

						self.add_memory(f"Assistant: {response}")
						query = response
						break

				# resubmit the query again to the LLM
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
