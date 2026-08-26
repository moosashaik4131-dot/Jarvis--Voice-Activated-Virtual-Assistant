import speech_recognition as sr
import webbrowser
import pyttsx3
import musiclib
import requests

recognizer=sr.Recognizer()
newsapi="39ba03c580144d1e87aa315cd7435c4e"

def speak(text):
    engine = pyttsx3.init()
    engine.setProperty("rate",170)
    engine.setProperty("volume",1)
    engine.say(text)
    engine.runAndWait()
    del engine
    

def ask_ai(prompt):
    try:

        system_prompt = f"""
You are Jarvis, a smart voice assistant.

Rules:
- Reply in a natural conversational tone.
- Keep answers short (2-4 sentences).
- Do not use bullet points.
- Do not use numbering.
- Do not repeat the user's question.
- If the answer is long, summarize it.
- If the user greets you, greet them back.

User: {prompt}

Jarvis:
"""

        response = requests.post(
            "http://127.0.0.1:11434/api/generate",
            json={
                "model": "llama3.2:latest",
                "prompt": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 120
                }
            },
            timeout=120
        )

        if response.status_code == 200:
            answer = response.json()["response"].strip()
            return answer 
        else:
            return "Sorry sir, I couldn't generate a response."

    except Exception as e:
        return f"Error: {e}"
    
def processcommand(c):
    if "open google" in c.lower():
        webbrowser.open("https://google.com")
    elif "open youtube" in c.lower():
        webbrowser.open("https://youtube.com")
    elif "open chatgpt" in c.lower():
        webbrowser.open("https://chatgpt.com")
    elif c.lower().startswith("play"):
        song=c.lower().split(" ")[1]
        link=musiclib.music[song]
        webbrowser.open(link)
    elif any(word in c for word in ["news", "headline", "headlines"]):
        speak("Here are today's top headlines.")
        r=requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={newsapi}")
        print(r.status_code)
        print(r.text)
        if r.status_code == 200:
            data = r.json()
            articles = data.get("articles",[])
            for article in articles[:5]:
               headline = article["title"].split(" - ")[0]
               print(headline)
               speak(headline)
    else:
        speak("Let me think.")
        answer = ask_ai(c)
        print("Jarvis:", answer)
        speak(answer)

if __name__=="__main__":
    speak("How can i help you")
    while True:
        #listen wake word "jarvis"
        #obtain from microphone
        r = sr.Recognizer()
        r.energy_threshold = 300
        r.dynamic_energy_threshold = True
        r.pause_threshold = 0.8
        print("Recognizing....")
        try:
            with sr.Microphone() as source:
               print("Listening....")
               r.adjust_for_ambient_noise(source, duration=1)
               audio = r.listen(source,timeout=2,phrase_time_limit=1)
            word=r.recognize_google(audio)
            
            if any(w in word.lower() for w in ["hello", "jarvis", "hey jarvis"]):
                speak("yes sir")
                with sr.Microphone() as source:
                   print("Jarvis active....")
                   r.adjust_for_ambient_noise(source, duration=1)
                   audio = r.listen(source,timeout=5,phrase_time_limit=8)
                   command=r.recognize_google(audio)
                   command = command.lower().strip()
                   print(f"Recognized command: '{command}'")
                   processcommand(command)
        except Exception as e:
            print("error; {0}".format(e))
