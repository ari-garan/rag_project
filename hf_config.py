import os

ENV_FILE_PATH = os.path.join(os.path.dirname(__file__), ".env")


def get_hf_token():
    """Retrieve Hugging Face API token from environment or .env file."""
    # 1. Environment Variable
    token = os.environ.get("HF_TOKEN") or os.environ.get("HF_API_KEY") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
    if token and token.strip():
        return token.strip()

    # 2. .env File
    if os.path.exists(ENV_FILE_PATH):
        with open(ENV_FILE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("HF_TOKEN=") or line.startswith("HF_API_KEY="):
                    parts = line.split("=", 1)
                    if len(parts) > 1 and parts[1].strip():
                        return parts[1].strip().strip('"').strip("'")

    return None


def ensure_hf_token():
    """Ensure a valid Hugging Face token exists, prompting user if missing."""
    token = get_hf_token()
    if token:
        return token

    print("\n" + "=" * 60)
    print("HUGGING FACE INFERENCE API TOKEN REQUIRED")
    print("=" * 60)
    print("To make Hugging Face API calls without downloading model weights locally,")
    print("you need a free Hugging Face API Token (HF_TOKEN).")
    print("Get your free token at: https://huggingface.co/settings/tokens")
    print("-" * 60)

    user_token = input("Enter your Hugging Face API Key (e.g. hf_...): ").strip()
    if not user_token:
        raise ValueError("Hugging Face API Token is required to make API calls.")

    # Save to .env file for future automatic use
    with open(ENV_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(f"HF_TOKEN={user_token}\n")

    print(f"Token saved to {ENV_FILE_PATH} successfully!\n")
    return user_token
