from src.core.schemas.memory_message_schema import CreateMemoryMessageSchema
from src.repositories.memory_message_repository import get_memory_message_repository
from src.services.llm_service import LLMService


class MemoryManagement:
	def __init__(self, llm_service: LLMService):
		self.llm_service = llm_service
		self.memory_repo = get_memory_message_repository()

	def add_memory(self, user_id: str, role: str, message: str):
		"""Add a memory message to the database"""
		memory_data = CreateMemoryMessageSchema(
			user_id=user_id,
			role=role,
			message=message
		)
		return self.memory_repo.create(memory_data)

	def get_memory_from_user(self, user_id: str, limit: int = 50) -> list:
		"""Get memory messages for a user, sorted by latest"""
		memory_messages = self.memory_repo.get_list(user_id, limit)
		return [
			{
				"role": msg.role,
				"message": msg.message,
				"created_at": msg.created_at.isoformat()
			}
			for msg in memory_messages
		]

	def summarize_memory(self, user_id: str, limit: int = 100) -> str:
		"""Summarize memory messages for a user"""
		memories = self.get_memory_from_user(user_id, limit)
		
		if not memories:
			return "No previous conversations found."
		
		# Format memories for summarization
		memory_text = "\n".join([
			f"{mem['role']}: {mem['message']}" 
			for mem in reversed(memories)  # Reverse to get chronological order
		])
		
		# Create summarization prompt
		summarization_prompt = f"""
		You are an AI assistant tasked with summarizing a conversation between a user and an assistant.
		Given the following conversation, create a concise summary that clearly outlines the user's questions or requests and provides a brief overview of the assistant's responses.
		Highlight key points, including the user's requests and the assistant's specific Final Answers.
		Ensure the summary is clear, concise, and written in a single short paragraph.

		Chat History:
		{memory_text}
		"""
		
		# Use LLM service to generate summary
		messages = [{"role": "user", "content": summarization_prompt}]
		summary = self.llm_service.query_execute(messages) # type: ignore
		
		return summary or "Unable to generate summary."