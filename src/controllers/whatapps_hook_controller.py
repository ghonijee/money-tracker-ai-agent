import os
from unittest import result
from fastapi import Depends, routing
from fastapi import HTTPException, Query, Response, Request
from heyoo import WhatsApp

from src.agent.ai_agent import Agent, get_agent
from src.services.utils import create_encrypted_user_id
from src.services.webhook_message_service import WebhookMessageService, get_webhook_message_service

router = routing.APIRouter()
messenger = WhatsApp(os.getenv("WHATAPP_APP_TOKEN"), phone_number_id=os.getenv("WHATAPP_PHONE_NUMBER_ID"))

VERIFY_TOKEN = os.getenv("WHATAPP_WEBHOOK_API_KEY", "secret_verify_token")


@router.get("/webhook")
async def webhook_verify(
	hub_mode: str | None = Query(None, alias="hub.mode"),
	hub_token: str | None = Query(None, alias="hub.verify_token"),
	hub_challenge: str | None = Query(None, alias="hub.challenge"),
):
	"""
	Verifikasi webhook ala Meta. Meta akan mem-panggi /webhook?hub.mode=subscribe&hub.verify_token=...&hub.challenge=...
	Jika mode=subscribe dan token cocok, kita kembalikan challenge apa adanya (200).
	Kalau tidak, balas 403.
	"""
	if hub_mode == "subscribe" and hub_token == VERIFY_TOKEN:
		# challenge harus dikembalikan sebagai plain text persis
		return Response(content=hub_challenge or "", media_type="text/plain")
	raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def hook(request: Request, webhook_service: WebhookMessageService = Depends(get_webhook_message_service), agent: Agent = Depends(get_agent)):
	"""
	Endpoint ini akan dipanggil oleh WhatsApp setiap kali ada pesan baru.
	Kita bisa menggunakan webhook ini untuk memproses pesan yang masuk.
	"""
	# ambil data dari request body
	data = await request.json()
	webhook_data = webhook_service.parse_whatsapp_hook_data(data)

	if webhook_data.is_changed_field() and webhook_data.is_new_message and webhook_data.message is not None:
		# jika ada pesan baru, kita proses pesan tersebut
		response = agent.process_message(webhook_data.message)

	return "OK", 200


@router.post("/webhook/test")
async def hookTest(request: Request, webhook_service: WebhookMessageService = Depends(get_webhook_message_service), agent: Agent = Depends(get_agent)):
	"""
	Endpoint ini akan dipanggil oleh WhatsApp setiap kali ada pesan baru.
	Kita bisa menggunakan webhook ini untuk memproses pesan yang masuk.
	"""
	# ambil data dari request body
	data = await request.json()
	webhook_data = webhook_service.parse_whatsapp_hook_data(data)

	if webhook_data.is_changed_field() and webhook_data.is_new_message and webhook_data.message is not None:
		# jika ada pesan baru, kita proses pesan tersebut
		result = agent.process_message(webhook_data.message)

	return {
		"status": "success",
		"message": "Webhook received",
		"data": {
			"result": result,
			"message": webhook_data.message,
		},
	}
