import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

#pega o token no .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#ativa o pacote padrao de eventos do dc. basicamente diz ao server que o bot quer
#receber maioria das notificações comuns
intents = discord.Intents.default()

#ativa uma privileged intent chamada conteudo da mensagem, fazendo com que o bot 
#consiga ler o texto escrito pelos usuários. eh necessario ter isso pra ele ler 
#comandos como '!ajuda', por exemplo.
intents.message_content = True


#cria o bot e define que ele vai responder a comandos com prefixo '!'
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'O bot {bot.user.name} está online.')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower() == "oi":
        await message.channel.send(f"Olá, {message.author.name}")

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

bot.run(TOKEN)