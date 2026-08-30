import os

from dotenv import load_dotenv
from openai import AzureOpenAI


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# Read Azure OpenAI configuration
# ---------------------------------------------------------

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
api_version = os.getenv(
    "AZURE_OPENAI_API_VERSION",
    "2024-10-21"
)


# ---------------------------------------------------------
# Validate configuration
# ---------------------------------------------------------

print("==============================================")
print("       Azure OpenAI Connection Test")
print("==============================================")

if not endpoint:
    raise ValueError(
        "AZURE_OPENAI_ENDPOINT is missing from .env"
    )

if not api_key:
    raise ValueError(
        "AZURE_OPENAI_API_KEY is missing from .env"
    )

if not deployment:
    raise ValueError(
        "AZURE_OPENAI_DEPLOYMENT is missing from .env"
    )


print("\nConfiguration found:")
print(f"Endpoint: {endpoint}")
print(f"Deployment: {deployment}")
print(f"API Version: {api_version}")
print("API Key: [HIDDEN]")


# ---------------------------------------------------------
# Create Azure OpenAI client
# ---------------------------------------------------------

client = AzureOpenAI(
    azure_endpoint=endpoint,
    api_key=api_key,
    api_version=api_version
)


# ---------------------------------------------------------
# Send a simple test request
# ---------------------------------------------------------

print("\nSending test request to Azure OpenAI...")


response = client.chat.completions.create(
    model=deployment,
    messages=[
        {
            "role": "system",
            "content": (
                "You are a simple connectivity test assistant."
            )
        },
        {
            "role": "user",
            "content": (
                "Respond with exactly: "
                "Azure OpenAI connection successful."
            )
        }
    ],
    temperature=0
)


# ---------------------------------------------------------
# Display result
# ---------------------------------------------------------

answer = response.choices[0].message.content

print("\nAzure OpenAI Response:")
print(answer)

print("\n==============================================")
print("              TEST COMPLETED")
print("==============================================")