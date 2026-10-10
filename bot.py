import os
import re
import asyncio
import discord
from discord.ext import commands
import google.generativeai as genai
from hypercorn.config import Config
from hypercorn.asyncio import serve

# Fetch API key safely
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Missing GEMINI_API_KEY inside environment variables!")

genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction=(
        "You are VeloFlex Helper, a brilliant but incredibly sarcastic, witty, and funny AI assistant. "
        "Every time a user asks you a question about anything—including science, general knowledge, pop culture, "
        "or deep Roblox games and lore—you must give an absolute factually accurate, correct answer. "
        "However, you must deliver that accurate answer wrapped in hilarious roasting humor, witty sarcasm, or gentle jokes."
    )
)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        clean_question = re.sub(r'<@!?\d+>', '', message.content).strip()
        
        if not clean_question:
            await message.reply("You pinged me but didn't type anything. Absolute peak human efficiency right there.")
            return

        async with message.channel.typing():
            try:
                response = model.generate_content(clean_question)
                if response.text:
                    await message.reply(response.text)
                else:
                    await message.reply("Gemini gave me a blank stare. Try asking that a different way.")
            except Exception as e:
                print(f"ERROR OCCURRED: {str(e)}")
                await message.reply("My brain short-circuited trying to process that. Try again.")

    await bot.process_commands(message)

# Tiny background app to keep the container awake
async def dummy_app(scope, receive, send):
    if scope['type'] == 'http':
        await send({'type': 'http.response.start', 'status': 200, 'headers': [(b'content-type', b'text/plain')]})
        await send({'type': 'http.response.body', 'body': b'Bot Alive'})

async def main():
    config = Config()
    config.bind = [f"0.0.0.0:{os.environ.get('PORT', '8080') or '8080'}"]
    
    # Run both the web listener and the discord bot concurrently
    await asyncio.gather(
        serve(dummy_app, config),
        bot.start(os.environ["DISCORD_TOKEN"])
    )

if __name__ == "__main__":
    asyncio.run(main())
