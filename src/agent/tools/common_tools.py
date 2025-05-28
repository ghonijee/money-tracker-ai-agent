from datetime import datetime
import hashlib
import hmac
from mimetypes import guess_type
import os
import sys

from dotenv import load_dotenv
from src.core.interfaces.tool import Tool
from datetime import timezone as tz

from src.services.llm_service import get_llm_service
import base64

load_dotenv()


class GetDateTool(Tool):
	def name(self) -> str:
		return "generate_date"

	def description(self) -> str:
		return "Convert a natural-language date/time expression into an exact ISO-8601 date or datetime. "

	def run(self, args):
		ref_ts = datetime.now().isoformat()
		expression = args["expression"]
		timezone = args["timezone"] or tz.utc

		system_prompt = (
			"You are a precise date/time parser."
			"Given a natural-language expression and a reference timestamp + timezone"
			'When the clock is not specified, use the start of day time in the given timezone.'
			'always output ONLY valid JSON with format {"datetime": "YYYY-MM-DDTHH:MM:SS±HH:MM"}.'
			"don't output anything else."
		)
		user_prompt = f'Expression: "{expression}"\nReference Current Timestamp: "{ref_ts}"\nTimezone: "{timezone}"\nReturn the exact ISO-8601 date/time in the following format: {{format}}'

		# 2) Call the LLM
		llm_service = get_llm_service()
		resp = llm_service.query_execute(messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], max_token=200)
		return resp

	def get_args_schema(self):
		return [
			{"name": "expression", "type": "str", "description": "Natural-language date/time expression", "status": "required"},
			{"name": "timezone", "type": "str", "description": "Timezone of the output date/time, Optional IANA timezone (e.g. 'Asia/Jakarta').", "status": "required"},
		]

	def output_schema(self):
		return "str"


class GetUserIdTool(Tool):
	def __init__(self, user_id) -> None:
		self.id = user_id

	def name(self) -> str:
		return "get_user_id"

	def description(self) -> str:
		return "Get user ID from the encrypted user ID. Always use this tool to get the user ID when you need a user ID."

	def run(self, args):
		return self.create_encrypted_user_id(self.id)

	def output_schema(self):
		return "str"

	def create_encrypted_user_id(self, user_id):
		secret_key = os.getenv("SECRET_KEY")
		if not secret_key:
			raise RuntimeError("Set SECRET_KEY for encryption!")
		digest = hmac.new(secret_key.encode(), user_id.encode(), digestmod=hashlib.sha256).hexdigest()
		return digest


class ImageExtractInformationTool(Tool):
	def name(self) -> str:
		return "image_extract_information"

	def description(self) -> str:
		return "Extract information from an image."

	def run(self, args):
		if "image_path" in args:
			image_path = args["image_path"]
			if not os.path.exists(image_path):
				raise FileNotFoundError(f"Image file not found: {image_path}")

		# get full path from root directory
		if not os.path.isabs(image_path):
			image_path = os.path.join(os.getcwd(), image_path)
		if not os.path.isfile(image_path):
			raise FileNotFoundError(f"Image file does not exist or is not a file: {image_path}")
		if not image_path.lower().endswith((".png", ".jpg", ".jpeg", ".gif")):
			raise ValueError("Unsupported image format. Supported formats are: PNG, JPG, JPEG, GIF.")
		if not os.access(image_path, os.R_OK):
			raise PermissionError(f"Image file is not readable: {image_path}")

		image_base64_resuslt = self.image_to_data_uri(image_path)

		contents = []
		if "caption" in args and args["caption"]:
			contents.append(
				{
					"type": "text",
					"text": f"""
					What is the information in this image?
					Caption: {args.get("caption", "No caption provided")}
					""",
				}
			)

		system_prompt = (
			"You are an image information extractor. "
			"Given an image, extract the information from the image and return it in a structured format JSON_BLOB."
			"Always output ONLY valid JSON with format {'information': {...}}."
			"Don't output anything else."
		)

		contents.append({"type": "image_url", "image_url": {"url": image_base64_resuslt}})
		llm_service = get_llm_service()
		resp = llm_service.query_execute(messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": contents}], model="opengvlab/internvl3-14b:free")
		self.remove_image_file(image_path)
		return resp

	def encode_image_to_base64(self, image_path: str) -> str:
		with open(image_path, "rb") as image_file:
			encoded_bytes = base64.b64encode(image_file.read())
		return encoded_bytes.decode("utf-8")

	from mimetypes import guess_type

	def image_to_data_uri(self, image_path: str) -> str:
		mime_type, _ = guess_type(image_path)
		if not mime_type:
			mime_type = "application/octet-stream"
		base64_str = self.encode_image_to_base64(image_path)
		return f"data:{mime_type};base64,{base64_str}"

	def remove_image_file(self, image_path: str):
		if os.path.exists(image_path):
			try:
				os.remove(image_path)
			except OSError as e:
				print(f"Error removing file {image_path}: {e}")
		else:
			print(f"File {image_path} does not exist, cannot remove.")

	def get_args_schema(self):
		return [
			{"name": "caption", "type": "str", "description": "Caption for the image from the user input/message", "status": "optional"},
			{"name": "image_path", "type": "str", "description": "Path to the image to analyze", "status": "required"},
		]

	def output_schema(self):
		return "str"
