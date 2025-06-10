
class CreateMemoryMessageSchema:
	user_id: str
	role: str
	message: str

	def __init__(self, user_id, role, message):
		self.user_id = user_id
		self.role = role
		self.message = message

	@classmethod
	def from_dict(cls, data: dict):
		return cls(
			user_id=data.get("user_id"),
			role=data.get("role"),
			message=data.get("message")
		)

	def to_dict(self):
		return {
			"user_id": self.user_id,
			"role": self.role,
			"message": self.message
		}