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
    report = json.loads(completion.choices[0].message.content)
    report["actions"] = [{"texte": texte, "fait": False} for texte in report.get("actions", [])]
    return report
