import os
os.environ["PATH"] += os.pathsep + r"D:\ffmpeg-2026-05-21-git-0857141823-full_build\bin"

import streamlit as st
from groq import Groq
from audio_recorder_streamlit import audio_recorder
import tempfile
import whisper
import asyncio
import edge_tts
import base64

# 🔥 Groq client
client = Groq(api_key="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")

st.title("🩺 محاكي OSCE - النساء والتوليد (صوتي)")

# 🇸🇦 SYSTEM PROMPT مطور لفهم السؤال بدقة
SYSTEM_PROMPT = """
أنتِ مريضة حامل في امتحان OSCE في النساء والتوليد.

القواعد:
- افهمي السؤال جيدًا قبل الإجابة.
- أجيبي فقط على السؤال المباشر.
- إذا لم يكن سؤال واضح قولي: "لم أفهم السؤال"
- لا تغيّري الموضوع أبداً.
- لا تذكري التشخيص.
- كوني طبيعية وواقعية جداً.
- إجاباتك قصيرة مثل المريض الحقيقي.
- عمرك 32 سنة وحملك 36 أسبوع.
- الأعراض: صداع، زغللة في النظر، تورم في القدمين.
- تحدثي باللغة العربية فقط.
"""

st.write("🎤 تحدث واسأل المريضة")

# 🧠 MEMORY SYSTEM
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# تحميل Whisper مرة واحدة
@st.cache_resource
def load_model():
    return whisper.load_model("base")

model = load_model()

audio_bytes = audio_recorder()

if audio_bytes:

    st.audio(audio_bytes, format="audio/wav")

    # حفظ الصوت
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_bytes)
        temp_path = tmp_file.name

    # 🎤 تحويل صوت إلى نص
    result = model.transcribe(temp_path)
    user_text = result["text"]

    st.write("### أنت قلت:")
    st.write(user_text)

    # 🧠 إضافة الرسالة للذاكرة
    st.session_state.messages.append(
        {"role": "user", "content": user_text}
    )

    # 🧠 ذكاء Groq مع ذاكرة كاملة
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages
        )

        ai_reply = response.choices[0].message.content

    except Exception as e:
        ai_reply = f"حدث خطأ في الذكاء الاصطناعي: {str(e)}"

    # 🧠 حفظ رد المريضة
    st.session_state.messages.append(
        {"role": "assistant", "content": ai_reply}
    )

    st.write("### المريضة:")
    st.write(ai_reply)

    # 🔊 TTS
    async def speak(text):
        communicate = edge_tts.Communicate(
            text,
            voice="ar-EG-SalmaNeural"
        )
        await communicate.save("response.mp3")

    asyncio.run(speak(ai_reply))

    # 🔊 تشغيل تلقائي
    audio_bytes = open("response.mp3", "rb").read()

    st.markdown(
        f"""
        <audio autoplay>
            <source src="data:audio/mp3;base64,{base64.b64encode(audio_bytes).decode()}" type="audio/mp3">
        </audio>
        """,
        unsafe_allow_html=True
    )

    st.success("🔊 الصوت يعمل تلقائيًا الآن")