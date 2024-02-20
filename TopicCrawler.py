import requests

import apikeys


class TopicCrawler:
    def __init__(self, url):
        self.currTopic = ''

    def chat_with_chatgpt(prompt):
        url = "https://api.openai.com/v1/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": apikeys.get_gpt_key()  # replace with api key
        }
        data = {
            "model": "text-davinci-003",  # You can choose the model you prefer
            "prompt": prompt,
            "max_tokens": 150  # Adjust the max tokens as per your requirement
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["choices"][0]["text"]
        else:
            return "Error: Failed to communicate with ChatGPT API"

    # Example usage:
    prompt = "Q: What is the capital of France?\nA: Paris\nQ: Who wrote Hamlet?\nA: William Shakespeare\nQ: What is the boiling point of water?"
    response = chat_with_chatgpt(prompt)
    print(response)

