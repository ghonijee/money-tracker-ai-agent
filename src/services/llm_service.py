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
		self.models = [
			# "meta-llama/llama-4-scout:free",
			"meta-llama/llama-4-maverick:free",
			# "meta-llama/llama-3.3-70b-instruct:free",
			# "deepseek/deepseek-chat-v3-0324:free",
			# "google/gemma-3-27b-it:free", #best for image
			# "meta-llama/llama-3.2-11b-vision-instruct:free",
			# "opengvlab/internvl3-14b:free", # best for image
		]

	def get_random_model(self):
		import random

		return random.choice(self.models)

	def query_execute(
		self,
		messages: Iterable[ChatCompletionMessageParam],
		max_token: int | None | NotGiven = NOT_GIVEN,
		stop: Union[Optional[str], List[str], None] | NotGiven = NOT_GIVEN,
		model: str | None = None,
	):
		completion = self.client.chat.completions.create(
			extra_headers={
				"X-Title": "Expense Tracker AI Agent",
				"HTTP-Referer": "https://github.com/ghonijee/money-tracker-ai-agent",
			},
			model=model if model is not None else self.get_random_model(),
			messages=messages,
			stop=stop,
			max_tokens=max_token,
		)

		if completion.choices is None:
			# throw an error
			print(completion)
			return completion.error.message

		return completion.choices[0].message.content
