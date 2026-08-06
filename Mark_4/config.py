import os

def _load_env_file(env_path: str = "/sdcard/pa/Mark_4/.env") -> None:
    """Reads .env file and loads keys into os.environ cleanly."""
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        os.environ[key.strip()] = val.strip().strip('"').strip("'")
        except Exception as e:
            print(f"[Config Error]: Failed to read .env file: {e}")

# Load environment variables automatically when config is imported
_load_env_file()

# Central System Configurations
OMNIROUTE_API_KEY = os.environ.get("OMNIROUTE_API_KEY", "")
OMNIROUTE_BASE_URL = os.environ.get("OMNIROUTE_BASE_URL", "http://localhost:20128/v1/chat/completions")

if __name__ == "__main__":
    print("⚙️ Testing MARK_4 Configuration Loader...")
    if OMNIROUTE_API_KEY:
        masked_key = OMNIROUTE_API_KEY[:6] + "..." + OMNIROUTE_API_KEY[-4:]
        print(f"✅ Loaded OMNIROUTE_API_KEY: {masked_key}")
        print(f"✅ Base URL: {OMNIROUTE_BASE_URL}")
    else:
        print("❌ Error: OMNIROUTE_API_KEY not found in .env!")
