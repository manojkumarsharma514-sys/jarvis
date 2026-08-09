from openai import OpenAI

client = OpenAI()

def ask_chatgpt(system_prompt="", user_prompt=""):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content

def handle(data):
    print(ask_chatgpt(user_prompt=data["target"]))
