import os
from typing import Iterable, List, Optional, Union
from openai import NOT_GIVEN, NotGiven, OpenAI
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

	def query_execute(self, messages: Iterable[ChatCompletionMessageParam], max_token: int | None | NotGiven = NOT_GIVEN, stop: Union[Optional[str], List[str], None] | NotGiven = NOT_GIVEN):
		completion = self.client.chat.completions.create(
			extra_headers={
				"X-Title": "Expense Tracker AI Agent",
				"HTTP-Referer": "https://github.com/ghonijee/money-tracker-ai-agent",
			},
			# model="meta-llama/llama-3.3-70b-instruct:free",
			model="meta-llama/llama-4-maverick:free",
			# model="meta-llama/llama-4-scout:free",
			# model="deepseek/deepseek-chat-v3-0324:free",
			messages=messages,
			stop=stop,
			max_tokens=max_token,
		)

		if completion.choices is None:
			# throw an error
			print(completion)
			return completion.error.message

		return completion.choices[0].message.content
