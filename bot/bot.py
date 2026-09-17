import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import aiohttp

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


@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def batman(ctx):
    await ctx.send("Buscando dados do Batman...")

    url = "https://www.cheapshark.com/api/1.0/games?title=batman"

    email = os.getenv("USER_EMAIL")
    autentificador = {'User-Agent': 'SteamDealsBot/1.0 ({email})'}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=autentificador) as resposta:
            dados = await resposta.json()

    print("Resposta da API:", dados)

    if isinstance(dados,list) and len(dados) > 0:
        primeiro_jogo = dados[0]
        nome = primeiro_jogo['external']
        preco = primeiro_jogo['cheapest']

        await ctx.send(f"{nome}\n Menor preço encontrado: {preco}")
    else:
        await ctx.send("Não foi possível encontrar o jogo.")

bot.run(TOKEN)