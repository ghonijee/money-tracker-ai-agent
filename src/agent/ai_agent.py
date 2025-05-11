


import ast
import json
from fastapi import Depends

from src.agent.tools.greet import GreetTool
from src.services.llm_service import LLMService, get_llm_service

def get_agent(llm_service: LLMService = Depends(get_llm_service)):
    agent = Agent(llm_service)
    agent.add_tool(GreetTool())
    return agent

class Agent:
    def __init__(self, llm_service: LLMService = Depends(get_llm_service)) -> None:
        self.tools = []
        self.memory = []
        self.max_memory = 5
        self.llm_service = llm_service

    def add_tool(self, tool):
        self.tools.append(tool)

    def process_input(self, input):
        self.memory.append(
            f"User: {input}"
        )
        self.memory = self.memory[-self.max_memory:]

        context = "\n".join(self.memory)
        tools_description = "\n".join([f"{tool.name()}: {tool.description()}" for tool in self.tools])
        response_format = {"action":"", "args":""}

        prompt = f"""
        You are a helpful assistant. Answer the following question using the context provided. 
        Context: {context}

        You have access to the following tools:
        {tools_description}

        Based on the user's input and context, decide if you should use a tool or respond directly.
        Sometimes you might have to use multiple tools to solve user's input. You have to do that in a loop.
        If you identify a action, respond with the tool name and the arguments for the tool.
        If you decide to respond directly to the user then make the action "respond_to_user" with args as your response in the following format. 
        Response format: 
        {response_format}

        Only respond with the JSON format and nothing else. Do not add any other text or indentation causing the JSON to be invalid.
        """
        
        response = self.llm_service.query_execute([
            {"role": "user", "content": prompt},
        ])

        print(response)
        response_dict = self.json_parser(response)

        for tool in self.tools:
            if tool.name().lower() in response_dict["action"].lower():
                return tool.run(response_dict["args"])
        return response_dict['args']

    def json_parser(self, input_string):
        try:
            python_dict = ast.literal_eval(input_string)
            json_string = json.dumps(python_dict)
            json_dict = json.loads(json_string)
            
            if isinstance(json_dict, dict):
                return json_dict   
            else:
                return {"action": 'respond_to_user', "args": json_dict['args']}
        except:
            return {"action": 'respond_to_user', "args": input_string}
    