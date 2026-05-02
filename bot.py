import asyncio
import speech_recognition as sr
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import edge_tts
import os
from groq import Groq

TOKEN = "8503403019:AAF-_hE_ar5EDNl2LTSQR3YlK-mDRN7B2FA"
import os
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
VOICE = "az-AZ-BanuNeural"

bot = Bot(token=TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_KEY)

SYSTEM_PROMPT = "Sən Carvis adında mehriban Azərbaycanlı köməkçisən. Qısa, səmimi, dialoqla cavab ver. 1-2 cümlə."

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.reply("Salam, mən Carvis. Səsli danış, cavab verim.")

@dp.message(F.voice)
async def voice_handler(message: types.Message):
    await message.reply("Düşünürəm...")
    try:
        file_id = message.voice.file_id
        file = await bot.get_file(file_id)
        await bot.download_file(file.file_path, "voice.ogg")
        print("1. Səs yükləndi")

        os.system("ffmpeg -i voice.ogg -ar 16000 -ac 1 voice.wav -y")
        print("2. WAV-a çevrildi")

        r = sr.Recognizer()
        with sr.AudioFile("voice.wav") as source:
            audio = r.record(source)
        user_text = r.recognize_google(audio, language="az-AZ")
        print(f"3. Sən dedin: {user_text}")

        print("4. Groq cavab yazır...")
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            max_tokens=100
        )
        gpt_text = response.choices[0].message.content
        print(f"5. Groq cavab: {gpt_text}")
        await message.reply(gpt_text)

        print("6. Səsə çevirirəm...")
        communicate = edge_tts.Communicate(gpt_text, VOICE)
        await communicate.save("cavab.mp3")
        os.system("ffmpeg -i cavab.mp3 -c:a libopus cavab.ogg -y")
        await message.answer_voice(types.FSInputFile("cavab.ogg"))
        print("7. Səs göndərildi")

    except Exception as e:
        print(f"XƏTA TUTULDU: {e}")
        await message.reply(f"Xəta: {e}")

    for f in ["voice.ogg", "voice.wav", "cavab.mp3", "cavab.ogg"]:
        if os.path.exists(f): os.remove(f)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("Bot işə düşdü... Groq + Banu aktivdir")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())