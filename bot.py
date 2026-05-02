import asyncio
import os
import speech_recognition as sr
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import edge_tts
from groq import Groq

# Railway Variables-dan key-ləri götür
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
VOICE = "az-AZ-BanuNeural"

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN tapılmadı. Railway Variables yoxla")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY tapılmadı. Railway Variables yoxla")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = "Sən Carvis adında mehriban Azərbaycanlı köməkçisən. Qısa, səmimi, dialoq şəklində cavab ver."

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Salam, mən Carvis. Səsli mesaj göndər, cavab verim.")

@dp.message(F.voice)
async def voice_handler(message: types.Message):
    msg = await message.reply("Düşünürəm...")
    try:
        # 1. Səs faylını yüklə
        file = await bot.get_file(message.voice.file_id)
        await bot.download_file(file.file_path, "voice.ogg")

        # 2. Səsi mətnə çevir
        r = sr.Recognizer()
        with sr.AudioFile("voice.ogg") as source:
            audio = r.record(source)
        text = r.recognize_google(audio, language="az-AZ")

        # 3. Groq-a göndər
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            model="llama-3.1-8b-instant",
        )
        reply_text = chat_completion.choices[0].message.content

        # 4. Cavabı səsləndir
        communicate = edge_tts.Communicate(reply_text, VOICE)
        await communicate.save("reply.mp3")

        await message.answer_voice(types.FSInputFile("reply.mp3"), caption=reply_text)
        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"Xəta baş verdi: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
