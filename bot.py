import discord
from discord.ext import commands, tasks
import datetime
import requests

# Crie as constantes da chave api e do discord

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

reminders = []

def get_weather(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=pt_br'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return f"{data['name']}: {data['weather'][0]['description'].capitalize()} com temperatura de {data['main']['temp']}°C"
    else:
        return "Cidade não encontrada."

@bot.command(name='lembrete')
async def set_reminder(ctx, time: int, *, message: str):
    remind_time = datetime.datetime.now() + datetime.timedelta(seconds=time)
    reminders.append((remind_time, message, ctx.channel.id))
    await ctx.send(f"Lembrete definido para {time} segundos a partir de agora: {message}")

@bot.command(name='lembretes')
async def list_reminders(ctx):
    if not reminders:
        await ctx.send("Nenhum lembrete ativo.")
    else:
        response = "Lembretes ativos:\n"
        for reminder in reminders:
            response += f"- {reminder[1]} em {reminder[0]}\n"
        await ctx.send(response)

@bot.command(name='tempo')
async def weather(ctx, *, location: str):

    if ',' in location:
        city, state = map(str.strip, location.split(','))
        city_state = f"{city},{state}"
    else:
        city_state = location

    weather_info = get_weather(city_state)
    await ctx.send(weather_info)

@tasks.loop(seconds=10)
async def check_reminders():
    now = datetime.datetime.now()
    for reminder in reminders:
        if now >= reminder[0]:
            channel = bot.get_channel(reminder[2])
            await channel.send(f"Lembrete: {reminder[1]}")
            reminders.remove(reminder)

@bot.event
async def on_ready():
    check_reminders.start()
    print(f'Bot {bot.user.name} está online!')

bot.run(TOKEN)