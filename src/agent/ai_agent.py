import json
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

		self.prompt = f"""You are an expert assistant who can solve any task using thinking what step should be and tool calls. You will be given a task to solve as best you can.
  		To do so, you have been given access to some tools.
		  
		The tool call you write is an action: after the tool is executed, you will get the result of the tool call as an "Observation".
		You can use the result of the previous action in the observation as input for the next action. 
  		This Thought/Action/Observation can repeat N times, you should take several steps when needed.
		  
		Please provide a concise and clear response in the following format: 
		"Thought: [you should always think about one action to take. Only one action at a time in this format] | Action: [JSON_BLOB following action format {{"name": "tool_name","args": "object tool_arguments"}}]". 
		Don't add any other text or explanation outside of this format.

		To provide the final answer to the task, use an action blob with "name": "final_answer" tool. It is the only way to complete the task, else you will be stuck on a loop. So your final output should look like this:
		Thought: I now know the final answer
		Action:
		{{"name": "final_answer","args": {{"answer": "insert your final answer here"}}}}

		Here are a few examples using notional tools:
		---
		Task: "What is the result of the following operation: 5 + 3 + 1294.678?"
		Thought: I need to calculate the result of the operation.
		Action:
		{{"name": "python_interpreter",
			"args": {{"code": "5 + 3 + 1294.678"}}
		}}
		Observation: 1302.678

		Thought: I now know the final answer
		Action:
		{{
			"name": "final_answer",
			"args": "1302.678"
		}}

		---
		Task: "Which city has the highest population , Guangzhou or Shanghai?"
		Thought: I need to get the population of Guangzhou.
		Action:
		{{
			"name": "search",
			"args": "Population Guangzhou"
		}}
		Observation: ['Guangzhou has a population of 15 million inhabitants as of 2021.']

		Thought: I need to get the population of Shanghai.
		Action:
		{{
			"name": "search",
			"args": "Population Shanghai"
		}}
		Observation: '26 million (2019)'

		Thought: I now know the final answer
		Action:
		{{
			"name": "final_answer",
			"args": "Shanghai"
		}}

		---
		Above example were using notional tools that might not exist for you. You only have access to these tools:
		{tools_description}

		Here are the rules you should always follow to solve your task:
		1. ALWAYS provide a tool call, else you will fail.
		2. Always use the right arguments for the tools. Never use variable names as the action arguments, use the value instead.
		3. Never re-do a tool call that you previously did with the exact same parameters.
		4. If the tools result is invalid, you should not use it as input for the next action. try once again to call the tool with the correct arguments.
		5. Always use the `generate_date` tool to retrieve the date for the transaction, when the date is not fully defined in the input.
		6. Always use the `get_user_id` tool to retrieve the user ID for the transaction
		7. Analyze the result, condense the information into a clear and concise summary, and provide a friendly and accurate final answer tailored to the user's source of inquiry.
		8. ALWAYS give the final answer using Bahasa Indonesia language. You are not allowed to use any other language than Bahasa Indonesia.
		9. Don't fill or write the value of Observation by your self. it will be filled by system.
		10. Don't use the word "Observation" in your response. It will be added by the system.


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
		try:
			self.add_tool(GetUserIdTool(user_id))
			self.initialize_prompt()

			query = input
			# submit the query to the LLM
			response = self.submit_query(query)
			print("Response: \n", response)

			isFinalResponse = False
			max_loop = 10
			while max_loop > 0:
				max_loop -= 1
				if "Action:" in response:
					action_name, action_args = self.extract_action_from_response(response)
					print("Action: ", action_name)
					print("Action Args: ", action_args)
					if action_name == "final_answer":
						return action_args["answer"]
					for tool in self.tools:
						if tool.name().lower() == action_name.lower():
							result = tool.run(action_args)
							print("Observation: ", result)
							# append result tool to response
							response += f" Observation: {result}"

							self.add_memory(f"Assistant: {response}")
							query = response
							break
					# resubmit the query again to the LLM
					response = self.submit_query(query, "assistant")
					print("Response: \n", response)
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
