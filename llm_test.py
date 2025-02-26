from openai import OpenAI
import os
from dotenv import load_dotenv


def test_openai_connection():
    """Test if we can connect to OpenAI API and get a response."""
    try:
        # Load environment variables
        load_dotenv()

        # Initialize the client
        client = OpenAI()

        # Print API key for debugging (first 8 chars only)
        api_key = os.getenv("OPENAI_API_KEY", "")
        print(f"API Key starts with: {api_key[:8]}...")

        # Simple test completion
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello, World!'"},
            ],
            max_tokens=10,
            store=True,
        )

        print("\nAPI Response:")
        print(response.choices[0].message.content)
        print("\nConnection test successful!")
        return True

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        return False


if __name__ == "__main__":
    test_openai_connection()
