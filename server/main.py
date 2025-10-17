from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv
import requests
import os
from google import genai
from google.genai import types
import json

# ------------------- Setup -------------------
load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "meet_audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
DRIVE_FOLDER_ID =  os.getenv("DRIVE_FOLDER_ID") # 🔸 Replace with your folder ID
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
token_data = json.loads(os.getenv("GDRIVE_TOKEN"))


# ------------------- Helper Functions -------------------
def upload_to_gdrive(file_path: str, file_name: str):
    """Uploads file to Google Drive and returns public download link."""
    creds = Credentials.from_authorized_user_info(token_data)
    service = build("drive", "v3", credentials=creds)

    # Metadata for the uploaded file
    file_metadata = {
        "name": file_name,
        "parents": [DRIVE_FOLDER_ID]
    }
    media = MediaFileUpload(file_path, mimetype="audio/wav")

    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    file_id = uploaded_file.get("id")

    # Make it public
    service.permissions().create(
        fileId=file_id,
        body={"role": "reader", "type": "anyone"}
    ).execute()

    #print(f"https://drive.google.com/uc?export=download&id={file_id}")

    # Create download link
    return f"https://drive.google.com/uc?export=download&id={file_id}"


def transcribe_with_deepgram(audio_url: str):
    """Sends the audio URL to Deepgram and returns the transcription."""
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {"url": audio_url}
    response = requests.post("https://api.deepgram.com/v1/listen", headers=headers, json=payload)

    #print(response.text)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}

def summarize_with_gemini(transcript: str) -> str:
    """Send transcription to Gemini AI and get summary, key decisions, tasks."""
    result = {"summary": ""}
    try:
        model = "gemini-2.5-pro"

        prompt_text = f"""
        Given the meeting transcript below, give summary, key decisions and action steps

        Transcript:
        {transcript}
        """

        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt_text)],
            )
        ]

        generate_config = types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=-1)
        )

        full_text = ""
        for chunk in gemini_client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=generate_config,
        ):
            full_text += chunk.text

        result["summary"] = full_text.strip()

    except Exception as e:
        print(f"[Gemini Error] {e}")  # log error
        result["summary"] = f"Gemini error: {str(e)}"

    return result


# ------------------- API Endpoint -------------------
@app.post("/process")
async def process_input(
    prompt: str = Form(None),
    audio_0: UploadFile = None,
):
    messages = []  # To hold step-wise updates

    try:
        # Step 1: Save audio locally
        messages.append("Received your audio file, starting upload...")
        file_path = os.path.join(UPLOAD_DIR, audio_0.filename)
        with open(file_path, "wb") as f:
            f.write(await audio_0.read())

        # Step 2: Upload to Google Drive
        messages.append("Uploading file to Google Drive...")
        download_link = upload_to_gdrive(file_path, audio_0.filename)
        messages.append(f"Uploaded to Google Drive successfully!\nLink: {download_link}")

        # Step 3: Transcription via Deepgram
        messages.append("Sending audio to Deepgram for transcription...")
        deepgram_response = transcribe_with_deepgram(download_link)

        transcript = deepgram_response.get("results", {}).get("channels", [{}])[0].get("alternatives", [{}])[0].get("transcript", "")
        messages.append(f"Transcription complete:\n\n{transcript if transcript else 'No speech detected.'}")

        # Step 4: Summarize using Gemini
        messages.append("Sending transcription to Gemini AI for summary and key decisions...")
        gemini_result = summarize_with_gemini(transcript)
        messages.append(f"📝 Summary:\n{gemini_result['summary']}")

        os.remove(file_path)

        return JSONResponse({
            "steps": messages,
            "gdrive_link": download_link,
            "transcription": transcript,
            "summary": gemini_result['summary'],
        })


    except Exception as e:
        messages.append(f"Error: {str(e)}")
        return JSONResponse({"steps": messages}, status_code=500)



