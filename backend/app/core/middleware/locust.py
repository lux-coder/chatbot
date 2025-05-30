
from locust import HttpUser, task, between

class ChatbotUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        # Zamijeni ovo stvarnim JWT tokenom ako je poznat
        self.token = ""
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "X-Tenant-ID": "9c512999-f380-4863-83ab-b5a469ae9262"
        }

    @task(3)
    def send_prompt(self):
        payload = {
            "message": "En ten tore, you are great",
            "chatbot_instance_id": "3793bebc-23d0-48a0-8950-40b2ab7a5949",
            "conversation_id": "d13bb920-2131-4f31-92f7-28334248ed21"
        }
        self.client.post("/api/v1/chat", json=payload, headers=self.headers)

    @task(1)
    def get_chat_history(self):
        conversation_id = "7eeb6999-8ae7-4a76-8c96-323048b2bd58"
        url = f"/api/v1/chat/history?conversation_id={conversation_id}"
        self.client.get(url, headers=self.headers)    

    @task(1)
    def get_health(self):
        self.client.get("/api/v1/healthz", headers=self.headers)