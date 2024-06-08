import os
import base64
from time import sleep
import time
import random
import requests
from googletrans import Translator # type: ignore
from dotenv import load_dotenv # type: ignore
from flask import Flask, request, render_template # type: ignore

application = Flask(__name__)
# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variable
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

translator = Translator()
def translate_to_english(text):
    translator = Translator()
    translated_text = translator.translate(text, dest='en').text
    return translated_text

@application.route("/")
def index():
    # Returns index.html
    return render_template("index.html")

@application.route("/transcribe", methods=["GET","POST"])
def transcribe():
        if request.method == "POST":
            APII_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
            
            audio_file = request.files["audioFile"]

            if audio_file:

                def quary(audio_data, max_tries=3):
                    for i in range(1,max_tries+1):
                        try:
                            response = requests.post(APII_URL, headers=headers, data=audio_data)
                            response_json = response.json()
                            text = response_json["text"]
                            if text:
                                return text
                
                        except Exception as e:
                            if i < max_tries:
                                time.sleep(20)  # Delay before retrying
                            else:
                                raise 

                    return "Failed after multiple attempts"

            if audio_file:
                audio_data = audio_file.read()
                output = quary(audio_data)
                return output
            else:
                return "error"
            
        return "Error"

@application.route("/help", methods=['GET','POST'])
def help():
    if request.method == "POST":
        data = request.form.get('data')
        if data:
            API_URL = "https://api-inference.huggingface.co/models/Gustavosta/MagicPrompt-Stable-Diffusion"
        
            def query(payload):
                max_retries = 3
                for attempt in range(1, max_retries + 1):
                    try:
                        response = requests.post(API_URL, headers=headers, json=payload)
                        response.raise_for_status()  # Raise an exception for non-200 status codes
                        return response.json()
                    except requests.exceptions.RequestException as e:
                        if attempt < max_retries:
                            sleep(20)  # Delay before retrying
                        else:
                            raise  # Raise the last exception if all retries fail

            prompt1 = translate_to_english(data)

            output = query({"inputs": prompt1,
                            "parameters":{"max_length":200,
                            "num_return_sequences":3,
                            "no_repeat_ngram_size":2,
                            "early_stopping": True }
                            })

            out = output[0]['generated_text']

            def original(text):
                detect = translator.detect(text)
                return detect.lang
        
            srcv = original(data)

            def translat(text):
                translate = translator.translate(text , src= 'auto',dest=srcv)
                return translate.text
        
            tran = translat(out)

            return tran
        
    return "Error"
        
        
@application.route("/generate", methods=['GET', 'POST'])
def generate():
    if request.method == "POST":
        API_URL = "https://api-inference.huggingface.co/models/ZB-Tech/Text-to-Image"
        data = request.form['data']
        inputx = translate_to_english(data)
        def query(payload):
            max_retries = 3
            for attempt in range(1, max_retries + 1):
                try:
                    response = requests.post(API_URL, headers=headers, json=payload)
                    response.raise_for_status()  # Raise an exception for non-200 status codes
                    return response.content
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries:
                        sleep(20)  # Delay before retrying
                    else:
                        raise  # Raise the last exception if all retries fail
        
        image_bytes = query({"inputs": inputx + "<lora:dalle-3-xl-lora-v2:0.8>",
                             "parameters": {"seed":random.randint(1,9999999),
                                            "num_inference_steps":50,
                                            "guidance_scale":9,
                                            "wait_for_model": True,
                                            "use_cache": False}
                            })
          # Print the image bytes for debugging
        
        try:
            # Try opening the image using PIL
            #image = Image.open(io.BytesIO(image_bytes))
            # Convert image to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            #return render_template("index.html", result=image_base64, download_link=temp_image_path)
            return render_template("index.html", result=image_base64)
        except Exception as e:
            print("Error:", e)  # Print the error for debugging
            return "Error generating image. Please try again."

if __name__ == "__main__":
    application.run()
