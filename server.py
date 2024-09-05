from flask import Flask, request, send_file, jsonify
from flask_cors import CORS  # Import CORS
import torch
from pathlib import Path
from io import BytesIO
from scipy.io import wavfile
from pyngrok import ngrok
from huggingface_hub import hf_hub_download
import os
from style_bert_vits2.tts_model import TTSModel, TTSModelHolder
from style_bert_vits2.nlp import bert_models
from style_bert_vits2.constants import Languages

app = Flask(__name__)
CORS(app)  # Enable CORS

bert_models.load_model(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")
bert_models.load_tokenizer(Languages.JP, "ku-nlp/deberta-v2-large-japanese-char-wwm")

model_file = "hskw_v1/hskw_v1_best.safetensors"
config_file = "hskw_v1/config.json"
style_file = "hskw_v1/style_vectors.npy"

for file in [model_file, config_file, style_file]:
    print(file)
    hf_hub_download("nonmetal/jvnv-test", file, local_dir="model_assets")

# TTS model loading
model_dir = Path("model_assets")
device = "cuda" if torch.cuda.is_available() else "cpu"
model_holder = TTSModelHolder(model_dir, device)
loaded_models = []

def load_models():
    global loaded_models
    for model_name, model_paths in model_holder.model_files_dict.items():
        model = TTSModel(
            model_path=model_dir / model_file,
            config_path=model_dir / config_file,
            style_vec_path=model_dir / style_file,
            device=model_holder.device,
        )
        loaded_models.append(model)
    print(f"Models loaded: {len(loaded_models)}")

@app.route('/tts', methods=['POST'])
def tts():
    data = request.json
    text = data.get("text")
    model_id = data.get("model_id", 0)
    speaker_id = data.get("speaker_id", 0)
    language = data.get("language", "JP")

    print(f"Received request with text: {text}, model_id: {model_id}, speaker_id: {speaker_id}, language: {language}")

    if model_id >= len(loaded_models):
        error_message = "Invalid model_id"
        print(f"Error: {error_message}")
        return jsonify({"error": error_message}), 400

    model = loaded_models[model_id]

    try:
        sr, audio = model.infer(
            text=text,
            language=language,
            speaker_id=speaker_id,
        )
        print(f"Audio synthesized successfully with sample rate: {sr} and audio length: {len(audio)}")
    except Exception as e:
        error_message = f"Error during synthesis: {e}"
        print(error_message)
        return jsonify({"error": error_message}), 500

    # Save audio file in memory
    wav_io = BytesIO()
    wavfile.write(wav_io, sr, audio)
    wav_io.seek(0)
    print("Sending audio file back to client...")

    return send_file(
        wav_io,
        mimetype="audio/wav",
        as_attachment=True,
        download_name="output.wav"
    )

if __name__ == "__main__":
    # Load models
    load_models()

    # Ngrok tunnel creation
    url = ngrok.connect(5000)
    print(f"Ngrok tunnel open at: {url}")
    
    # Run Flask server
    app.run(host='0.0.0.0', port=5000)
