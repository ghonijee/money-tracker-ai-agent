from typing import Optional


class MessageModel:
	def __init__(
		self,
		user_id: str,
		sender_phone_number: str,
		sender_name: str,
		message_type: str,
		message_content: str,
		image_public_url: Optional[str] = None,
		image_file_path: Optional[str] = None,
		source: Optional[str] = None,
	):
		"""
		Initialize the MessageModel with sender's phone number, name, message type, content, and optional image details.
		:param sender_phone_number: The phone number of the sender.
		:param sender_name: The name of the sender.
		:param
		message_type: The type of the message (e.g., text, image, video).
		:param message_content: The content of the message.
		:param image_public_url: The public URL of the image (if applicable).
		:param image_file_path: The file path of the image (if applicable).
		:param source: The source of the message (e.g., WhatsApp, Telegram).
		"""
		self.user_id = user_id
		self.sender_phone_number = sender_phone_number
		self.sender_name = sender_name
		self.message_type = message_type
		self.message_content = message_content
		self.image_public_url = image_public_url
		self.image_file_path = image_file_path
		self.source = source

	def is_have_image(self):
		"""
		Check if the message has an image.
		:return: True if the message has an image, False otherwise.
		"""
		return self.message_type == "image" and self.image_file_path is not None

	def __str__(self):
		"""
		Return a string representation of the MessageModel.
		:return: A string representation of the MessageModel.
		"""
		return f"MessageModel(sender_phone_number={self.sender_phone_number}, sender_name={self.sender_name}, message_type={self.message_type}, message_content={self.message_content}, image_public_url={self.image_public_url}, image_file_path={self.image_file_path}, source={self.source})"

	def to_context(self):
		"""
		Convert the MessageModel to a context string.
		:return: A string representation of the MessageModel in context format.
		"""
		return f"""
		User ID: {self.user_id}
		Message Type: {self.message_type} 
		Message Content: {self.message_content} 
		Image URL: {self.image_public_url} 
		Image File Path: {self.image_file_path} 
		Source: {self.source}
		"""
	def to_dict(self):
		"""
		Convert the MessageModel to a dictionary.
		:return: A dictionary representation of the MessageModel.
		"""
		return {
			"user_id": self.user_id,
			"sender_phone_number": self.sender_phone_number,
			"sender_name": self.sender_name,
			"message_type": self.message_type,
			"message_content": self.message_content,
			"image_public_url": self.image_public_url,
			"image_file_path": self.image_file_path,
			"source": self.source
		}
