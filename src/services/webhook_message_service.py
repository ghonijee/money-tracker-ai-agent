import os
from typing import Union
from heyoo import WhatsApp
import logging

from src.core.models.message_model import MessageModel
from src.services.utils import create_encrypted_user_id


def get_webhook_message_service():
	return WebhookMessageService()


class WhatAppHookModel:
	changed_field: str
	is_new_message: bool
	message: MessageModel | None

	def __init__(self, changed_field: str, is_new_message: bool, message: MessageModel | None):
		self.changed_field = changed_field
		self.is_new_message = is_new_message
		self.message = message

	def is_changed_field(self):
		return self.changed_field == "messages"


class WebhookMessageService:
	def __init__(self):
		self.whatsapp = WhatsApp(token=os.getenv("WHATAPP_APP_TOKEN"), phone_number_id=os.getenv("WHATAPP_PHONE_NUMBER_ID"))

	def parse_whatsapp_message(self, data, source: str) -> Union[MessageModel, None]:
		changed_field = self.whatsapp.changed_field(data)
		if changed_field == "messages":
			new_message = self.whatsapp.is_message(data)
			if new_message:
				mobile = self.whatsapp.get_mobile(data)
				if mobile is None:
					logging.warning("Received message without mobile number")
					return None
				user_id = create_encrypted_user_id(user_id=mobile)
				name = self.whatsapp.get_name(data)
				message_type = self.whatsapp.get_message_type(data)

				model = MessageModel(
					user_id=user_id,
					sender_phone_number=mobile or "",
					sender_name=name or "",
					message_type=message_type or "text",
					message_content="",
				)
				if message_type == "text":
					message = self.whatsapp.get_message(data)
					model.message_content = message or ""
				elif message_type == "image":
					model.message_type = "image"

					image = self.whatsapp.get_image(data)
					# get caption if available
					model.message_content = image["caption"] if image is not None and "caption" in image and image["caption"] is not None else ""
					if image is not None and "id" in image and "mime_type" in image:
						image_id, mime_type = image["id"], image["mime_type"]
						image_url = self.whatsapp.query_media_url(image_id)
						image_filename = self.whatsapp.download_media(image_url or "", mime_type)
						logging.info(f"{mobile} sent image {image_filename}")
						model.image_file_path = image_filename
					else:
						logging.warning("Received image message but image is None or missing id/mime_type")
				elif message_type == "interactive":
					pass
					# message_response = self.whatsapp.get_interactive_response(data)
					# if message_response is not None:
					#     interactive_type = message_response.get("type")
					#     message_id = message_response[interactive_type]["id"]
					#     message_text = message_response[interactive_type]["title"]
					# else:
					#     logging.warning("Received interactive message but message_response is None")

				elif message_type == "location":
					pass
					# message_location = self.whatsapp.get_location(data)
					# if message_location is not None and "latitude" in message_location and "longitude" in message_location:
					#     message_latitude = message_location["latitude"]
					#     message_longitude = message_location["longitude"]
					#     logging.info("Location: %s, %s", message_latitude, message_longitude)
					# else:
					#     logging.warning("Received location message but message_location is None or missing latitude/longitude")

				elif message_type == "video":
					pass
					# video = self.whatsapp.get_video(data)
					# if video is not None and "id" in video and "mime_type" in video:
					#     video_id, mime_type = video["id"], video["mime_type"]
					#     video_url = self.whatsapp.query_media_url(video_id) or ''
					#     video_filename = self.whatsapp.download_media(video_url, mime_type)
					#     logging.info(f"{mobile} sent video {video_filename}")
					# else:
					#     logging.warning("Received video message but video is None or missing id/mime_type")

				elif message_type == "audio":
					pass
					# audio = self.whatsapp.get_audio(data)
					# if audio is not None and "id" in audio and "mime_type" in audio:
					#     audio_id, mime_type = audio["id"], audio["mime_type"]
					#     audio_url = self.whatsapp.query_media_url(audio_id) or ''
					#     audio_filename = self.whatsapp.download_media(audio_url, mime_type)
					#     logging.info(f"{mobile} sent audio {audio_filename}")
					# else:
					#     logging.warning("Received audio message but audio is None or missing id/mime_type")

				elif message_type == "document":
					pass
					# file = self.whatsapp.get_document(data)
					# if file is not None and "id" in file and "mime_type" in file:
					#     file_id, mime_type = file["id"], file["mime_type"]
					#     file_url = self.whatsapp.query_media_url(file_id) or ''
					#     file_filename = self.whatsapp.download_media(file_url, mime_type)
					#     logging.info(f"{mobile} sent file {file_filename}")
					# else:
					#     logging.warning("Received document message but file is None or missing id/mime_type")
				else:
					logging.warning(f"Unknown message type: {message_type}")
					pass

				return model
		return None

	def parse_whatsapp_hook_data(self, data) -> WhatAppHookModel:
		"""
		Parse the incoming webhook data from WhatsApp.
		:param data: The incoming webhook data.
		:return: Parsed message model or None if not a message.
		"""
		changed_field = self.whatsapp.changed_field(data)
		is_new_message = self.whatsapp.is_message(data)
		message = self.parse_whatsapp_message(data, "WhatsApp") if is_new_message else None

		return WhatAppHookModel(changed_field=changed_field, is_new_message=is_new_message, message=message)
