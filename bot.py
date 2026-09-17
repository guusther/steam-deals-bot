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

async def cotacaoDolar():
    url = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resposta:
            dados = await resposta.json()
            
            usd_data = dados.get('USDBRL', {})
            return float(usd_data.get('bid', 5.50))

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

        cotacao = await cotacaoDolar()

        for jogo in dados[:3]:
            nome = jogo['external']
            precoUSD = float(jogo['cheapest'])
            precoBRL = precoUSD * cotacao

            steamID = jogo.get('steamAppID')

            preco_steam_oficial = "Indisponível na Steam BR"

            if steamID:
                steamURL = f"https://store.steampowered.com/api/appdetails?appids={steamID}&cc=br"
                async with aiohttp.ClientSession() as session_steam:
                    async with session_steam.get(steamURL) as resposta_steam:
                        dados_steam = await resposta_steam.json()

                info_jogo = dados_steam.get(str(steamID), {})
                if info_jogo.get('success') and 'data' in info_jogo:
                    data = info_jogo['data']

                    if data.get('is_free'):
                        preco_steam_oficial = "Gratuito"
                    elif 'price_overview' in data:
                        preco_steam_oficial = data['price_overview']['final_formatted']
                        
            dealId = jogo['cheapestDealID']
            linkId = f"https://www.cheapshark.com/redirect?dealID={dealId}"

            print(f"Jogo: {nome} || Preço: {precoBRL}")
            print("=============")

            embed = discord.Embed(
                title=nome, description=f"Menor preço encontrado: **R${precoBRL:.2f}** (**${precoUSD:.2f}**) || Preço na Steam: **{preco_steam_oficial}**"
                , color=discord.Color.dark_blue(), url=linkId
            )

            embed.set_image(url=jogo['thumb'])
            await ctx.send(embed=embed)
    else:
        await ctx.send("Jogo não encontrado.")


import os
import asyncio
from aiohttp import web

# 1. Endpoint simples para o Render verificar que o serviço está ativo
async def handle_ping(request):
    return web.Response(text="Bot de ofertas operacional!")

# 2. Servidor web dummy na porta dinâmica do Render
async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.getenv('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# 3. Execução paralela do servidor web e do bot do Discord
async def main():
    await start_web_server()
    await bot.start(TOKEN)

if __name__ == '__main__':
    asyncio.run(main())