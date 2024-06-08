from flask import Flask, request, jsonify , render_template# type: ignore
import requests
import time
from googletrans import Translator # type: ignore

app = Flask(__name__)

API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
headers = {"Authorization": "Bearer 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"}

translator = Translator()

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/transcribe", methods=["GET", "POST"])
def transcribe():
    if request.method == "POST":
        WHISPER_API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"

        audio_file = request.files["audioFile"]

        if audio_file:
            def query(audio_data, max_tries=3):
                for i in range(1, max_tries + 1):
                    try:
                        response = requests.post(WHISPER_API_URL, headers=headers, data=audio_data)
                        response_json = response.json()
                        text = response_json["text"]
                        if text:
                            return {"text": text} # Return the transcribed text as a JSON response

                    except Exception as e:
                        if i < max_tries:
                            time.sleep(20)  # Delay before retrying
                        else:
                            raise e

                return {"error": "Failed after multiple attempts"}

            if audio_file:
                audio_data = audio_file.read()
                output = query(audio_data)
                return jsonify(output)
            else:
                return jsonify({"error": "No audio file provided"})

    return jsonify({"error": "Error"})

@app.route('/generate_prompts', methods=['GET', 'POST'])
def generate_prompts():
    user_request = request.json.get('request')
    source_lang = translator.detect(user_request).lang  # Detect the source language

    # Translate the user request to English
    user_request_en = translator.translate(user_request, dest='en').text

    payload = {
        "inputs": f"You are an AI assistant skilled in generating creative and descriptive prompts for image generation. Given the topic '{user_request_en}', generate 5 unique and detailed prompts that could be used as input for an image generation model like Stable Diffusion or DALL-E.",
        "parameters": {
            "return_text": True,
            "num_return_sequences": 5,
            "do_sample": True,
            "top_p": 0.9,
            "top_k": 50,
            "temperature": 0.7,
            "max_new_tokens": 500,
            "wait_for_model": True
        }
    }
    output = query(payload)
    prompts_en = [result['generated_text'].replace(f"You are an AI assistant skilled in generating creative and descriptive prompts for image generation. Given the topic '{user_request_en}', generate 5 unique and detailed prompts that could be used as input for an image generation model like Stable Diffusion or DALL-E.", '') for result in output]

    # Translate the prompts back to the source language
    prompts_translated = [translator.translate(prompt, dest=source_lang).text for prompt in prompts_en]

    return jsonify(prompts_translated)

if __name__ == '__main__':
    app.run()
