import os
import re
import discord
from discord.ext import commands
import google.generativeai as genai

# Fetch API key safely
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Missing GEMINI_API_KEY inside environment variables!")

# Configure using stable initialization method
genai.configure(api_key=api_key)

# Setup model parameters with strict behavioral constraints
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
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
    # Ignore messages sent by the bot itself
    if message.author == bot.user:
        return

    # Check if the bot was explicitly @mentioned
    if bot.user.mentioned_in(message):
        # Completely strip out any hidden Discord mention ID tags (<@000000>) so Gemini receives raw plain text
        clean_question = re.sub(r'<@!?\d+>', '', message.content).strip()
        
        if not clean_question:
            await message.reply("You pinged me but didn't type anything. Absolute peak human efficiency right there.")
            return

        async with message.channel.typing():
            try:
                # Use standard generation call
                response = model.generate_content(clean_question)
                
                if response.text:
                    await message.reply(response.text)
                else:
                    await message.reply("Gemini gave me a blank stare. Try asking that a different way.")
            except Exception as e:
                # If an error happens, print it directly to your Railway logs so we can see exactly what broke
                print(f"ERROR OCCURRED: {str(e)}")
                await message.reply("My brain short-circuited trying to process that. Try again.")

    await bot.process_commands(message)

bot.run(os.environ["DISCORD_TOKEN"])
