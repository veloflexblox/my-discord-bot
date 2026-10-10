import os
import discord
from discord.ext import commands
import google.generativeai as genai

# Fetch the key and ensure it isn't blank
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("The bot cannot find your GEMINI_API_KEY. Make sure it is saved in your Railway variables!")

# Configure the SDK explicitly
genai.configure(api_key=api_key)

# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="You are a brilliant but incredibly sarcastic and funny AI. Every time a user asks you a question, you must give a highly accurate, correct factual answer, but deliver it with roasting humor, jokes, or witty sarcasm."
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
        clean_question = message.content.replace(f'<@外交{bot.user.id}>', '').strip()
        
        if not clean_question:
            await message.reply("You @'d me but didn't say anything. Typical human behavior.")
            return

        async with message.channel.typing():
            try:
                response = model.generate_content(clean_question)
                await message.reply(response.text)
            except Exception as e:
                await message.reply("My brain short-circuited trying to process that. Try again.")

    await bot.process_commands(message)

bot.run(os.environ["DISCORD_TOKEN"])
