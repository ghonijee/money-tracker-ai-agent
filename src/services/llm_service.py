import os
from typing import Iterable
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam


def get_llm_service():
    return LLMService()

class LLMService:
    client: OpenAI

    def __init__(self):
        
        self.client = OpenAI(
            api_key=os.getenv("OPEN_ROUTER_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )
    
    def query_execute(self, messages: Iterable[ChatCompletionMessageParam]):
        completion = self.client.chat.completions.create(
            model="meta-llama/llama-4-maverick:free",
            messages=messages,
            stop=['Observation:']
        )

        if(completion.choices is None):
            # throw an error
            print(completion)
            return completion.error.message
    
        return completion.choices[0].message.content