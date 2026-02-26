import os
import httpx
from typing import List
from dotenv import load_dotenv
import google.auth
from google.auth.transport.requests import Request

# Load environment variables
load_dotenv()

PROJECT_ID = os.getenv("VERTEX_AI_PROJECT_ID")
LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")

class EmbeddingService:
    def __init__(self):
        self.dimension = 768 # Gemini text-embedding-004 dimension
        self.model = 'text-embedding-004'
        self.api_endpoint = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{self.model}:predict"
        self.credentials, self.project = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

    def _get_access_token(self):
        auth_req = Request()
        self.credentials.refresh(auth_req)
        return self.credentials.token

    def get_embedding(self, text: str) -> List[float]:
        """
        Returns an embedding vector using Vertex AI REST API.
        """
        if not PROJECT_ID:
             import random
             return [random.uniform(-1, 1) for _ in range(self.dimension)]
        
        try:
            token = self._get_access_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            payload = {
                "instances": [{
                    "content": text
                }]
            }
            
            # Using sync call for simplicity here
            response = httpx.post(self.api_endpoint, json=payload, headers=headers, timeout=10.0)
            if response.status_code != 200:
                print(f"Vertex AI Error: {response.text}")
                response.raise_for_status()
                
            data = response.json()
            # Vertex AI response format: {"predictions": [{"embeddings": {"values": [...]}}]}
            return data['predictions'][0]['embeddings']['values']
        except Exception as e:
            print(f"Error generating embedding via Vertex AI: {e}")
            raise e

    async def get_embedding_async(self, text: str) -> List[float]:
        # For simplicity, reuse sync logic or implement async httpx with token refresh
        return self.get_embedding(text)

