from src.core.interfaces.tool import Tool


class GreetTool(Tool):
	def name(self) -> str:
		return "greet"

	def description(self) -> str:
		return "Greet the user"

	def run(self, args):
		return "Hello, My name is AI. How can I help you today?"
