import os
import discord
from discord.ext import commands
from google import genai
from google.genai import types
import threading
import http.server
import socketserver

# 1. DUMMY WEB SERVER FOR RENDER (Keeps the service alive for free)
def run_dummy_server():
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Bot is alive!")

    port = int(os.environ.get("PORT", 10000))
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Dummy server running on port {port}")
        httpd.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# 2. YOUR DISCORD BOT LOGIC
gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        clean_prompt = message.content.replace(f'<@{bot.user.id}>', '').strip()
        if not clean_prompt:
            await message.channel.send("You mentioned me, but you didn't say anything!")
            return

        async with message.channel.typing():
            try:
                response = gemini_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=clean_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction="You are a funny, sarcastic, but factually accurate Discord bot.",
                        max_output_tokens=300,
                    ),
                )
                await message.reply(response.text)
            except Exception as e:
                print(f"Error: {e}")
                await message.reply("My brain just glitched. Try again!")

    await bot.process_commands(message)

bot.run(os.environ.get("DISCORD_BOT_TOKEN"))
