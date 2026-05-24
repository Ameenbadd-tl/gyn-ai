import os
os.environ["PATH"] += os.pathsep + r"D:\ffmpeg-2026-05-21-git-0857141823-full_build\bin"

import streamlit as st
from groq import Groq
from audio_recorder_streamlit import audio_recorder
import tempfile
import asyncio
import edge_tts
import base64

# =========================
# 🔥 PAGE CONFIG (مهم للموبايل)
# =========================
st.set_page_config(
    page_title="OSCE Simulator",
    layout="centered"
)

# =========================
# 🔥 GROQ CLIENT (آمن)
# =========================
client = Groq(api_key=os.environ["GROQ_API_KEY"])

st.title("🩺 محاكي OSCE - النساء والتوليد (صوتي)")

# =========================
# 🇸🇦 SYSTEM PROMPT
# =========================
SYSTEM_PROMPT = """
أنتِ مريضة حامل في امتحان OSCE في النساء والتوليد.

القواعد:
- افهمي السؤال جيدًا قبل الإجابة.
- أجيبي فقط على السؤال المباشر.
- إذا لم يكن سؤال واضح قولي: "لم أفهم السؤال"
- لا تذكري التشخيص.
- كوني طبيعية وواقعية جداً.
- إجاباتك قصيرة مثل المريض الحقيقي.
- عمرك 32 سنة وحملك 36 أسبوع.
- الأعراض: صداع، زغللة في النظر، تورم في القدمين.
- تحدثي باللغة العربية فقط.
"""

st.write("🎤 تحدث واسأل المريضة")

# =========================
# 🧠 MEMORY
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# =========================
# 🎤 RECORD AUDIO
# =========================
audio_bytes = audio_recorder()

if audio_bytes:

    st.audio(audio_bytes, format="audio/wav")

    # =========================
    # 🔊 SAVE AUDIO
    # =========================
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_bytes)
        temp_path = tmp_file.name

    # =========================
    # 🧠 GROQ TRANSCRIPTION (بديل Whisper)
    # =========================
    with open(temp_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-large-v3"
        )

    user_text = transcription.text

    st.write("### أنت قلت:")
    st.write(user_text)

    # =========================
    # 🧠 ADD USER MESSAGE
    # =========================
    st.session_state.messages.append(
        {"role": "user", "content": user_text}
    )

    # =========================
    # 🧠 AI RESPONSE
    # =========================
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages
        )

        ai_reply = response.choices[0].message.content

    except Exception as e:
        ai_reply = f"خطأ في الذكاء الاصطناعي: {str(e)}"

    st.session_state.messages.append(
        {"role": "assistant", "content": ai_reply}
    )

    st.write("### المريضة:")
    st.write(ai_reply)

    # =========================
    # 🔊 TEXT TO SPEECH
    # =========================
    async def speak(text):
        communicate = edge_tts.Communicate(
            text,
            voice="ar-EG-SalmaNeural"
        )
        await communicate.save("response.mp3")

    asyncio.run(speak(ai_reply))

    # =========================
    # 🔊 AUTO PLAY AUDIO
    # =========================
    audio_bytes = open("response.mp3", "rb").read()

    st.markdown(
        f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{base64.b64encode(audio_bytes).decode()}" type="audio/mp3">
        </audio>
        """,
        unsafe_allow_html=True
    )

    st.success("🔊 الصوت يعمل تلقائيًا")