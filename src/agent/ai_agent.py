


import ast
import json
import re
from fastapi import Depends

from src.agent.tools.category_tools import GetListCategoryTool
from src.agent.tools.common_tools import GetDateTool, GetUserIdTool
from src.agent.tools.greet import GreetTool
from src.agent.tools.transaction_tools import CreateTransactionTool
from src.services.llm_service import LLMService, get_llm_service


def get_agent(llm_service: LLMService = Depends(get_llm_service)):
    agent = Agent(llm_service)
    agent.add_tool(GreetTool())
    return agent

class Agent:
    def __init__(self, llm_service: LLMService = Depends(get_llm_service)) -> None:
        self.user_id = "";
        self.tools = []
        self.messages = []
        self.memory = []
        self.max_memory = 10
        self.llm_service = llm_service
        self.initialize_tools()

    def initialize_tools(self):
        self.add_tool(GreetTool())
        self.add_tool(GetDateTool())
        self.add_tool(GetListCategoryTool())
        self.add_tool(CreateTransactionTool())

    def initialize_prompt(self):
        tools_description = "\n".join([f"{tool.name()}: {tool.description()} Args: {tool.get_args_schema()} Output: {tool.output_schema()}" for tool in self.tools])

        self.prompt = f"""
        You are a helpful assistant designed to help users effectively and accurately. Your primary goal is to provide helpfull, precise, and clear information to users. 
        
        You have access to the following tools:
        {tools_description}

        The way you use the tools is by specifying a json. This example is a valid json that uses the tool 'greet':
        {{"action": "greet", "args": {{}}}}

        You must call the `get_user_id` tool to retrieve the user ID for the transaction, and do so only once.
        You must call the `generate_date` tool only once to retrieve the date for the transaction, when the date is not fully defined in the input.

        You should think step by step in order to fulfill the objective with reasoing divide into Thought, Action, and Observation.
        You should always use the following format:

        Question: the input question you must answer
        Thought: you should always think about one action to take. Only one action at a time in this format:
        Action: $JSON (This is the JSON that contains the action and arguments, only JSON without markdown)
        Observation: the result of the action. This Observation is unique, complete, and the source of truth.  

        ... (this Thought/Action/Observation can repeat N times, you should take several steps when needed)

        If you have the answer, you must always response with the following format:

        Thought: I now know the final answer
        Final Answer: The final answer to the user's input. 

        Begin! Reminder to always use the exact characters `Final Answer: ` when you provide the final answer.
        """
        self.messages.append({"role": "system", "content": self.prompt})
        self.add_memory(f"System: {self.prompt}")

    def add_tool(self, tool):
        self.tools.append(tool)

    def add_memory(self, memory):
        self.memory.append(memory)
        self.memory = self.memory[-self.max_memory:]

    def process_input(self, input):
        self.add_memory(f"User: {input}")
        self.messages.append({"role": "user", "content": input})
        response = self.llm_service.query_execute(self.messages)
        return response or ""

    
    def run(self, input, user_id):
        self.add_tool(GetUserIdTool(user_id))
        self.initialize_prompt()

        query = input
        maxIterarion= 10

        while maxIterarion > 0:
            response = self.process_input(query)
            
            if "Final Answer:" in response:
                print(self.memory)
                print(self.messages)
                return response.split("Final Answer:")[1].strip()
            elif "Action:" in response:
                json_blob = response.split("Action:")[1]
                json_dict = self.json_parser(json_blob)
                # # get the action name from the dictionary
                action_name = json_dict["action"]
                # # get the arguments from the dictionary
                if(json_dict["args"] == ""):
                    action_args = {}
                else:
                    action_args = json_dict["args"]

                # check if the action is a tool
                for tool in self.tools:
                    if tool.name().lower() == action_name.lower():
                        result = tool.run(action_args)
                        # append result tool to response
                        response += " Observation: " + result
                       
                        self.add_memory(f"Assistant: {response}")
                        query = response
                        break 
                # remove action from context
                # query = re.sub(r'Action:.*?(?=Observation:)', '', response, flags=re.DOTALL)
            else:
                print(response)

            maxIterarion -= 1
    def json_parser(self, input_string):
        try:
            python_dict = ast.literal_eval(input_string)
            json_string = json.dumps(python_dict)
            json_dict = json.loads(json_string)
            return json_dict
        except:
            raise Exception("Invalid JSON")
    