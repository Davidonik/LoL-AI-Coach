import json
import boto3

bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")

model_id = "arn:aws:bedrock:us-east-1:085366697379:inference-profile/us.anthropic.claude-sonnet-4-20250514-v1:0"

# Prompt Creation
prompt = "Explain the difference between supervised and unsupervised learning."

# Request Structure
body = {
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "max_tokens": 1000,
    "anthropic_version": "bedrock-2023-05-31",
}

# Send the request to Bedrock
response = bedrock.invoke_model(
    modelId=model_id,
    body=json.dumps(body),
    contentType="application/json",
    accept="application/json"
)

# The response body comes as a byte stream, so decode it:
response_body = json.loads(response["body"].read())

# Print the result
print("\n Model output:")
print(response_body["content"][0]["text"])
