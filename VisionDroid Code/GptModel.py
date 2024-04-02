from openai import OpenAI

import os
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:10809'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:10809'


class GptModel:
    client = OpenAI(
        api_key="xxxxxx",
    )

    def chat(self, question: str):
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": question,
                }
            ],
            model="gpt-xxx",
        )

        return chat_completion.choices[0].message.content
