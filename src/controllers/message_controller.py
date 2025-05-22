from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.agent.ai_agent import Agent, get_agent


router = APIRouter()


class MessageRequest(BaseModel):
	phone_number: str = Field(..., description="Phone number of the user", min_length=9, max_length=15)
	message: str = Field(..., description="Message to be sent", min_length=1, max_length=225)


@router.post("/message")
def incoming_message(payload: MessageRequest, agent: Agent = Depends(get_agent)):
	response = agent.run(payload.message, payload.phone_number)
	return {"message": response}
