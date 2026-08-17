"""
Fonction liée à Groq : analyse de la transcription par le LLM.
"""

import json

def analyze(text, client, prompt):
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text}
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(completion.choices[0].message.content)