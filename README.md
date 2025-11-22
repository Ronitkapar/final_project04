# 🎬 AI Video Storyteller (Stock Footage Edition)

An automated video essay generator that turns PDF/Text documents into cinematic videos using AI.

## ✨ Features

*   **AI Script Generation:** Uses **Google Gemini** to analyze text and create engaging scripts.
*   **Stock Footage:** Automatically fetches relevant, high-quality videos from **Pexels**.
*   **Realistic Voiceovers:** Uses **Edge TTS** for natural-sounding narration.
*   **Smart Editing:** Assembles clips with **MoviePy**, including auto-generated subtitles.
*   **Deployment Ready:** Configured for easy hosting on **Render**.

## 🛠️ Tech Stack

*   **Python 3.10+**
*   **Streamlit** (Frontend)
*   **Google Gemini API** (LLM)
*   **Pexels API** (Video Assets)
*   **MoviePy** (Video Editing)
*   **Edge TTS** (Audio)

## 🚀 Quick Start

1.  **Clone the repo:**
    ```bash
    git clone https://github.com/Nimish-Sharma-dev/FINAL-PROJECT.git
    cd FINAL-PROJECT
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up keys:**
    Create a `.env` file:
    ```env
    GOOGLE_API_KEY=your_gemini_key
    PEXELS_API_KEY=your_pexels_key
    ```

4.  **Run the app:**
    ```bash
    streamlit run app.py
    ```

## 📦 Deployment

This project is ready for **Render**.
See [walkthrough.md](walkthrough.md) for a step-by-step deployment guide.
