import os
import httpx
import asyncio
import google.auth
from google.auth.transport.requests import Request
from dotenv import load_dotenv
from app.embeddings import EmbeddingService

# Load environment variables
load_dotenv()

PROJECT_ID = os.getenv("VERTEX_AI_PROJECT_ID")
LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")

async def test_integration():
    print("Testing Vertex AI Integration (Service Account)...")
    print(f"Project: {PROJECT_ID}, Location: {LOCATION}")

    # 1. Test Embedding Service
    print("\n--- Testing Embeddings ---")
    service = EmbeddingService()
    try:
        vector = service.get_embedding("Test document content")
        print(f"Embedding generated. Dimension: {len(vector)}")
        if len(vector) == 768:
            print("SUCCESS: Embedding dimension is 768.")
        else:
            print(f"FAILURE: Expected 768 dimensions, got {len(vector)}.")
    except Exception as e:
        print(f"FAILURE: Embedding generation failed: {e}")
        if hasattr(e, 'response'):
             print(f"Response Body: {e.response.text}")

    # 2. Test Chat Generation
    print("\n--- Testing Chat Generation ---")
    if not PROJECT_ID:
        print("FAILURE: VERTEX_AI_PROJECT_ID not found in environment.")
        return

    try:
        # Get Token
        credentials, project = google.auth.default(
            scopes=[
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/generative-language"
            ]
        )
        auth_req = Request()
        credentials.refresh(auth_req)
        token = credentials.token
        
        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": "Hello, can you explain what is Vertex AI in one sentence?"}]
            }],
             "generationConfig": {
                "temperature": 0.5,
                "maxOutputTokens": 1024
            }
        }

        # Try Global API with Bearer Token (gemini-2.0-flash)
        print("\n--- Testing Global API (gemini-2.0-flash) ---")
        url_global = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        headers_global = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "x-goog-user-project": PROJECT_ID
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url_global, json=payload, headers=headers_global, timeout=30.0)
            if response.status_code == 200:
                print("SUCCESS: Global API with Service Account worked!")
                data = response.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                print(f"Response: {text}")
                return
            else:
                print(f"Global API Failed: {response.status_code} {response.text}")

        # If Global failed, try Regional again (or we already failed it effectively)
        # Try Regional with v1beta1
        print("\n--- Testing Vertex AI Regional (v1beta1) ---")
        url = f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/gemini-1.5-flash-001:generateContent"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": "Hello, can you explain what is Vertex AI in one sentence?"}]
            }],
             "generationConfig": {
                "temperature": 0.5,
                "maxOutputTokens": 1024
            }
        }
    
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            
            if response.status_code != 200:
                print(f"FAILURE: Vertex AI API Error: {response.status_code}")
                # print(f"Response Body: {response.text}") # Reduced logging
            else:
                data = response.json()
                if "candidates" in data:
                    try:
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        print(f"Response received:\n{text}")
                        print("SUCCESS: Chat response generated.")
                    except:
                        print(f"FAILURE: Unexpected response structure: {data}")
                else:
                     print(f"FAILURE: No candidates in response: {data}")

    except Exception as e:
         print(f"FAILURE: Chat generation failed: {e}")

async def list_models():
    print("\n--- Listing Available Models (Global API) ---")
    try:
        credentials, project = google.auth.default(
            scopes=[
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/generative-language"
            ]
        )
        auth_req = Request()
        credentials.refresh(auth_req)
        token = credentials.token
        
        # Global API list models
        url = "https://generativelanguage.googleapis.com/v1beta/models"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "x-goog-user-project": PROJECT_ID
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10.0)
            if response.status_code == 200:
                data = response.json()
                print("Available Models (Global):")
                for model in data.get("models", []):
                    name = model.get("name", "")
                    if "gemini" in name:
                        print(f" - {name}")
            else:
                print(f"Failed to list models: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    asyncio.run(list_models())
    asyncio.run(test_integration())
