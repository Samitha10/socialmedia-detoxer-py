from textwrap import dedent

from openai import OpenAI

from config.loader import config

# Initialize client pointing to your local llama.cpp server
# Default llama.cpp server port is 8080. Update if your Jan CLI uses a different port.
client = OpenAI(base_url=f"{config['server']}/v1", api_key=config["api-key"])

system = dedent(
    """You are a helpful, note taking assistant. Based on the Social media Video transcription, generate a researched markdown note."""
)


def stream_local_completion(context: list | str, model_name: str):
    """
    Streams a chat completion from a local llama.cpp instance.
    """
    try:
        response_stream = client.chat.completions.create(
            model=model_name,  # Often ignored by llama.cpp, but required by the SDK
            messages=[
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": f"Video Transcription : {context}",
                },
            ],
            stream=True,
        )

        for chunk in response_stream:
            # Safely grab the text token delta
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except Exception as e:
        yield f"\n[Local Stream Error: {e}]"
