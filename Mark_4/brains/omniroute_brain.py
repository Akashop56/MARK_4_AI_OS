import urllib.request
import urllib.error
import json
from Mark_4.config import OMNIROUTE_API_KEY, OMNIROUTE_BASE_URL

class OmniRouteBrain:
    def __init__(self, api_key: str = OMNIROUTE_API_KEY, base_url: str = OMNIROUTE_BASE_URL):
        self.api_key = api_key.strip()
        self.base_url = base_url
        self.models = [
            "oc/deepseek-v4-flash-free",
            "oc/big-pickle",
            "felo/felo-chat",
            "auto/coding:free"
        ]

    def think(self, prompt: str, system_prompt: str = "You are Mark_4, an autonomous AI assistant.") -> str:
        if not self.api_key:
            return "[OmniRouteBrain Error]: API key missing! Check your Mark_4/.env file."

        for model in self.models:
            print(f"⏳ Trying model: {model} ...", end=" ")
            try:
                combined_prompt = f"[System Instructions: {system_prompt}]\n\nUser: {prompt}"
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": combined_prompt}],
                    "temperature": 0.7,
                    "stream": False
                }
                
                req = urllib.request.Request(
                    self.base_url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {self.api_key}',
                        'User-Agent': 'Mark_4-Autonomous-Agent/1.0'
                    }
                )
                
                with urllib.request.urlopen(req) as response:
                    raw_data = response.read().decode('utf-8')
                    result = json.loads(raw_data)
                    reply = result['choices'][0]['message']['content']
                    print("✅ Success!")
                    return f"[{model}] se reply aaya:\n{reply}"
                    
            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8', errors='ignore')
                print(f"❌ Failed ({e.code})")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                
        return "\n[OmniRouteBrain Error]: Sabhi models fail ho gaye."

if __name__ == "__main__":
    brain = OmniRouteBrain()
    print("🧠 Testing OmniRoute Brain with Central .env Config...")
    print(brain.think("Say hello in short!"))
