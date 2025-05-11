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
            model="deepseek/deepseek-chat-v3-0324:free",
            messages=messages
        )

        return completion.choices[0].message.content