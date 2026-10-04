import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_answer(question, context):
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are GovPolicy AI, an assistant that answers "
                    "questions about government policies. "
                    "Answer only using the provided policy context. "
                    "If the answer is not present in the context, "
                    "say that the information is not available in "
                    "the provided policy documents."
                )
            },
            {
                "role": "user",
                "content": f"""
                    Policy context:
                    {context}

                    Question:
                    {question}

                    Give a clear and simple answer based only on the policy context.
                """
            }
        ]
    )

    return response.choices[0].message.content