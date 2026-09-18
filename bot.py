import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import aiohttp

#pega o token no .env
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
ITAD_API_KEY = os.getenv('ITAD_API_KEY')

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

    #trava de segurança. se o render esquecer de carregar a var de ambiente ele avisa no chat e retorna
    if not ITAD_API_KEY:
        await ctx.send("Erro: A Chave API do IsThereAnyDeal não foi configurada.")
        return

    #isso aqui é um aviso pra quem usou o bot saber que ele ta executando a tarefa
    await ctx.send(f"Buscando ofertas para **{nome_jogo}**...")


    #cria uma sessao http
    async with aiohttp.ClientSession() as session:
        #busca da url
        url_busca = f"https://api.isthereanydeal.com/games/search/v1?key={ITAD_API_KEY}&title={nome_jogo}"

        #acessa a pagina e retorna um json
        async with session.get(url_busca) as resposta:
            if resposta.status != 200:
                await ctx.send("Erro ao conectar com a API")
                return
            dados = await resposta.json()

        #se dados nao tiver nada na lista significa que o jogo nao foi encontrado
        if not dados:
            await ctx.send("Jogo não foi encontrado.")
            return

        #pega o 1o jogo da busca
        jogo = dados[0]
        game_id = jogo['id']
        game_title = jogo['title']

        #busca ofertas em brl
        precosURL = f"https://api.isthereanydeal.com/games/prices/v3?key={ITAD_API_KEY}&country=BR"

        #eh enviado o id que foi descoberto amteriormente demtrp do pacote json=[game_id], pedindo
        #os precos da regiao esoclhida(nesse caso foi o brasil)
        async with session.post(precosURL, json=[game_id]) as respostaPreco:
            dados_precos = await respostaPreco.json()

        if not dados_precos or not dados_precos[0].get('deals'):
            await ctx.send(f"Nenhuma oferta ativa encontrada no Brasil para **{game_title}**")
            return

        #filtra apenas a parte das promocoes
        deals = dados_precos[0]['deals']

        #isso daqui foi uma gambiarra pra puxar a imagem do jogo do cheapshark
        url_imagem = f"https://www.cheapshark.com/api/1.0/games?title={nome_jogo}&limit=1"

        USER_EMAIL = os.getenv('USER_EMAIL')
        autentificador = {'User-Agent': f'SteamDealsBot/1.0 ({USER_EMAIL})'}

        async with session.get(url_imagem, headers=autentificador) as respostaIMG:
            dados_img = await respostaIMG.json()

        linkIMG = None
        if dados_img:
            linkIMG = dados_img[0]['thumb']


        embed = discord.Embed(
            title=f"Ofertas: {game_title}",
            description="Preços atualizados(Nuuvem, Steam, Epic, etc):",
            color=discord.Color.dark_blue()
        )

        if linkIMG:
            embed.set_image(url=linkIMG)


        for deal in deals[:5]:
            loja = deal['shop']['name']
            preco_atual = deal['price']['amount']
            preco_normal = deal['regular']['amount']
            desconto = deal.get('cut', 0)
            url_loja = deal['url']

            info_preco = f"**R${preco_atual:.2f}** "
            if desconto > 0:
                info_preco+=f"~~R${preco_normal:.2f}~~ (-{desconto}%)"

            embed.add_field(
                name=f"{loja}",
                value=f"{info_preco}\n[Ir para a loja]({url_loja})",
                inline=False
            )
        await ctx.send(embed=embed)



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