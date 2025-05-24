from src.core.interfaces.tool import Tool


class GetListCategoryTool(Tool):
	def name(self) -> str:
		return "get_list_category"

	def description(self) -> str:
		return "Get list of category for expense/income classification, ALWASYS use this tool to get the list of categories"

	def run(self, args) -> str:
		cartegories = [
			"Housing",
			"Clothing",
			"Personal Care",
			"Food",
			"Transportation",
			"Entertainment",
			"Shopping",
			"Medical",
			"Transfer",
			"Salary",
			"Taxes",
			"Insurance",
			"Debt",
			"Savings",
			"Investment",
			"Gifts",
			"Education",
			"Charity",
			"Credit Card",
			"Other",
		]
		# join the list of categories with a comma
		return ",".join(cartegories)

	def get_args_schema(self):
		return None

	def output_schema(self):
		return "str"
