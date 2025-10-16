# 🚀 Project Title
JEFF - Smart AI companion for meeting summarisation

---

## 📝 Description
JEFF – The Smart Meeting Summarizer is an AI-powered tool that automatically converts meeting audio into concise, actionable summaries. It highlights key points, decisions, and action items, helping teams save time and stay organized.

---

## 🏗️  Architecture Diagram
![Architecture Diagram](presentaion/arch.png)

---

## ⚙️ Step by Step Working Process
1. Step 1 – The user uploads a meeting audio file through the frontend interface.
2. Step 2 – The backend uploads the audio to Google Drive and generates a public link.
3. Step 3 – The audio is transcribed into text using Deepgram AI from the public URL received from GDRIVE API.
4. Step 4 – The transcription is processed by Google Gemini 2.5 Pro to create a structured summary.
5. Step 5 - The summarized text, including key decisions and action items, is sent back to the frontend for display to the user.

---

## 🎥 Video Demo

This attached video demo explains the working of this project visually.
[Watch the demo](https://link_to_your_video)

## 💻 Installation Steps

Follow these steps to set up the project locally:

1. **Clone the repository**  
```bash
git clone https://123thirumal/JEFF---Smart-Meeting-Summarizer.git
cd repo
```
2. **Create a Deepgram API Key**  
- Sign up or log in at [Deepgram](https://deepgram.com/)  
- Generate an API key and save it securely.

3. **Create a Gemini API Key**  
- Go to [Google Gemini Studio](https://studio.google.com/)  
- Generate an API key for your project.

4. **Create Google Drive API**  
- Go to [Google Cloud Console](https://console.cloud.google.com/)  
- Enable Google Drive API and create a project.

5. **Create OAuth Credentials**  
- In Google Cloud Console, create OAuth 2.0 credentials.  
- Download `token.json` after completing the OAuth setup.

6. **Create a folder in Google Drive**  
- Make a folder to store audio files.  
- Give **editor access** to the OAuth user created in step 5.

7. **Create a `.env` file** in the project root with the following variables:  
GEMINI_API_KEY=your_gemini_api_key  
DEEPGRAM_API_KEY=your_deepgram_api_key  
GDRIVE_FOLDER_ID=your_gdrive_folder_id

8. **Store `token.json`**  
- Place `token.json` inside the `gdrive_api` folder in your project.

9. **Run the backend server**  
Run `uvicorn --reload main:app` from your project folder.

10. **Run the frontend**  
Navigate to your frontend folder and start it (for example, with React: `npm install` then `npm start`).

Your project should now be running locally with all APIs connected.

