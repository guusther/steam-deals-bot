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
async def buscar(ctx, *, nome_jogo):
    await ctx.send(f"Buscando dados do {nome_jogo}...")

    #pega o link da api
    url = f"https://www.cheapshark.com/api/1.0/games?title={nome_jogo}"


    USER_EMAIL = os.getenv('USER_EMAIL')
    autentificador = {'User-Agent': f'SteamDealsBot/1.0 ({USER_EMAIL})'}

    #pega os dados da api e joga num json
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=autentificador) as resposta:
            dados = await resposta.json()

    #segurança pro bot nao quebrar
    if isinstance(dados,list) and len(dados) > 0:
        for jogo in dados[:3]:
            nome = jogo['external']
            preco = jogo['cheapest']

            print(f"Jogo: {nome} || Preço: {preco}")
            print("=============")

            await ctx.send(f"{nome}\nMenor preço encontrado: {preco}\n")
    else:
        await ctx.send("Jogo não encontrado.")
        
bot.run(TOKEN)