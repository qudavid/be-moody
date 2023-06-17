from flask import Flask, request, render_template
import os
import openai

openai.organization = ""
openai.api_key = ""

openai.Model.list()



app = Flask(__name__)


@app.route('/')
def index():
    response = openai.Image.create(
    prompt="A cute baby sea otter",
    n=2,
    size="1024x1024"
    )
    return response["data"][0]["url"]

@app.route('/message', methods=['GET'])
def get_prompt_from_user():
    message = request.args.get('message')

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": message}
        ]
    )
    return completion.choices[0].message



if __name__ == "__main__":
    app.run()