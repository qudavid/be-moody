import sqlite3
from flask import Flask, request, render_template, jsonify
import os
import openai
from hume import HumeBatchClient
from hume.models.config import LanguageConfig

from pathlib import Path

from typing import Any, Dict, List

from flask_cors import CORS

import numpy as np
from typing import List

import random


HUME_API_KEY = "DszRVXebgKf0A5EdYEqjgP3edtjVusiVYCw8g5FThj9BmxAu"

openai.organization = "org-dWtPz3lHouUKNmZD89G7NTBy"
openai.api_key = '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'

openai.Model.list()

app = Flask(__name__)
CORS(app)


# filepath = "backend/samples/best_cry_ever.mp4"
# client = HumeBatchClient(HUME_API_KEY)
# config = LanguageConfig(granularity="sentence", identify_speakers=True)
# job = client.submit_job(None, [config], files=[filepath])

# print("Running...", job)

# job.await_complete()
# print("Job completed with status: ", job.get_status())



def print_emotions(emotions: List[Dict[str, Any]]) -> None:
    emotion_map = {e["name"]: e["score"] for e in emotions}
    for emotion in ["Excitement", "Joy", "Sadness", "Anger", "Confusion", "Fear"]:
        print(f"- {emotion}: {emotion_map[emotion]:4f}")

class Stringifier:
    RANGES = [(0.26, 0.35), (0.35, 0.44), (0.44, 0.53), (0.53, 0.62), (0.62, 0.71), (0.71, 1.0)]
    ADVERBS = ["slightly", "somewhat", "moderately", "quite", "very", "extremely"]

    ADJECTIVES_48 = [
        "admiring", "adoring", "appreciative", "amused", "angry", "anxious", "awestruck", "uncomfortable", "bored",
        "calm", "focused", "contemplative", "confused", "contemptuous", "content", "hungry", "determined",
        "disappointed", "disgusted", "distressed", "doubtful", "euphoric", "embarrassed", "disturbed", "entranced",
        "envious", "excited", "fearful", "guilty", "horrified", "interested", "happy", "enamored", "nostalgic",
        "pained", "proud", "inspired", "relieved", "smitten", "sad", "satisfied", "desirous", "ashamed",
        "negatively surprised", "positively surprised", "sympathetic", "tired", "triumphant"
    ]

    ADJECTIVES_53 = [
        "admiring", "adoring", "appreciative", "amused", "angry", "annoyed", "anxious", "awestruck", "uncomfortable",
        "bored", "calm", "focused", "contemplative", "confused", "contemptuous", "content", "hungry", "desirous",
        "determined", "disappointed", "disapproving", "disgusted", "distressed", "doubtful", "euphoric", "embarrassed",
        "disturbed", "enthusiastic", "entranced", "envious", "excited", "fearful", "grateful", "guilty", "horrified",
        "interested", "happy", "enamored", "nostalgic", "pained", "proud", "inspired", "relieved", "smitten", "sad",
        "satisfied", "desirous", "ashamed", "negatively surprised", "positively surprised", "sympathetic", "tired",
        "triumphant"
    ]

    @classmethod
    def scores_to_text(cls, emotion_scores: List[float]) -> str:
        if len(emotion_scores) == 48:
            adjectives = cls.ADJECTIVES_48
        elif len(emotion_scores) == 53:
            adjectives = cls.ADJECTIVES_53
        else:
            raise ValueError(f"Invalid length for emotion_scores {len(emotion_scores)}")

        # Return "neutral" if no emotions rate highly
        if all(emotion_score < cls.RANGES[0][0] for emotion_score in emotion_scores):
            return "neutral"

        # Construct phrases for all emotions that rate highly enough
        phrases = [""] * len(emotion_scores)
        for range_idx, (range_min, range_max) in enumerate(cls.RANGES):
            for emotion_idx, emotion_score in enumerate(emotion_scores):
                if range_min < emotion_score < range_max:
                    phrases[emotion_idx] = f"{cls.ADVERBS[range_idx]} {adjectives[emotion_idx]}"

        # Sort phrases by score
        sorted_indices = np.argsort(emotion_scores)[::-1]
        phrases = [phrases[i] for i in sorted_indices if phrases[i] != ""]

        # If there is only one phrase that rates highly, return it
        if len(phrases) == 0:
            return phrases[0]

        # Return all phrases separated by conjunctions
        return ", ".join(phrases[:-1]) + ", and " + phrases[-1]

def createImageFromPrompt(prompt):
    response = openai.Image.create(prompt=prompt, n=2, size="512x512")
    return response['data']

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        print("success")
        images = []
        prompt = request.json['message']

        # filepath = "backend/samples/best_cry_ever.mp4"

        filepath = "backend/samples/test.txt"
        with open(filepath, "w") as fp:
            fp.write(prompt)


        client = HumeBatchClient(HUME_API_KEY)
        config = LanguageConfig(granularity="sentence", identify_speakers=True)
        job = client.submit_job(None, [config], files=[filepath])

        print("Running...", job)

        job.await_complete()
        print("Job completed with status: ", job.get_status())



        emotion_embeddings = []
        full_predictions = job.get_predictions()
        for source in full_predictions:
            predictions = source["results"]["predictions"]
            for prediction in predictions:
                language_predictions = prediction["models"]["language"]["grouped_predictions"]
                for language_prediction in language_predictions:
                    for chunk in language_prediction["predictions"]:
                        print(chunk["text"])
                        print_emotions(chunk["emotions"])
                        emotion_embeddings.append(chunk["emotions"])
                        print()


        stringifier = Stringifier()
        for emotion_embedding in emotion_embeddings:
            emotion_scores = [emotion["score"] for emotion in emotion_embedding]
            hume_response = stringifier.scores_to_text(emotion_scores)

        # generate sentiment analysis of the prompt
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": "summarize the following in one sentence:" +
                prompt}
            ],
        )
        gpt_response = completion.choices[0].message["content"]
        print("Hume response: " + hume_response)
        #simplify sentiment analysis into one to two words
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": "describe an artwork that represents this sentiment in three sentences:" +
                hume_response + gpt_response}
            ],
        )
        combined_response = completion.choices[0].message["content"]
        print("Combined response: " + combined_response)
        res = createImageFromPrompt(combined_response)
        if len(res) > 0:
            for img in res:
                images.append(img['url'])
        print(images[0])
        return images[0]
        

    return render_template('index.html', **locals())


@app.route('/message', methods=['POST'])
def get_prompt_from_user():
    # CORS(app, origins='http://127.0.0.1/3000', allow_headers=['Content-Type'], methods=['POST'])
    if request.method == 'POST':
        var = request.json['message']
        print(var)
        if var:

            completion = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": "Write a children's story that rhymes about" +
                    var + "with a moral or lesson at the end of the story."}
                ],
                temperature=1.00
            )
            returnStr = completion.choices[0].message["content"]
            print(returnStr)
            return returnStr

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    file.save('backend/samples/file')
    return

@app.route("/addrec", methods = ['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:
            name = request.json['username']
            print("adding name: " + name)
            # Connect to SQLite3 database and execute the INSERT
            with sqlite3.connect('database.db') as con:
                cur = con.cursor()
                ids = [id[0] for id in cur.execute("SELECT id FROM database")]
                while randNumber in ids:
                    randNumber = random.randit(1000, 9999)
                id = randNumber
                cur.execute("INSERT INTO database (id, name) VALUES (?,?)",(id, name))
                con.commit()
                msg = "Record successfully added to database"
        except:
            con.rollback()
            msg = "Error in the INSERT"
        finally:
            con.close()

            return render_template('result.html',msg=msg)
    else:
        return "no post" 

@app.route("/queries", methods=['GET'])
def query():
    with sqlite3.connect('database.db') as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM queries")
        rows = cur.fetchall()

        queries = []
        for row in rows:
            query = {'id': row[0], 'name': row[1]}
            queries.append(query)
        
        return jsonify(queries)





if __name__ == "__main__":    
    app.run()