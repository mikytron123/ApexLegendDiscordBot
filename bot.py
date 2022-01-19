import discod
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
from dateutil import parser
from keep_alive import keep_alive
#load_dotenv()
import os
TOKEN = os.getenv('DISCORD_TOKEN')
guild_ids = []

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or("$"))

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

bot = Bot()

class Scroller(discord.ui.View):
    def __init__(self,links) -> None:
        super().__init__(timeout=10)
        self.count = 0
        self.links = links
    @discord.ui.button(style=discord.ButtonStyle.gray,emoji="⬅️")
    async def left(self,button,interaction):
        self.count = max(0,self.count-1)
        await interaction.response.edit_message(content=self.links[self.count])

    @discord.ui.button(style=discord.ButtonStyle.gray,emoji="➡️")
    async def right(self,button,interaction):
        self.count = min(len(self.links)-1,self.count+1)
        await interaction.response.edit_message(content=self.links[self.count])



@bot.slash_command(name="ping",
             description="Ping bot",guild_ids=guild_ids)
async def ping(ctx):
    await ctx.send(f'Pong! in {round(bot.latency *1000, 3)}ms')

@bot.slash_command(name="news",
description="Fetches news from Apex Legends EA website",
guild_ids=guild_ids)
async def news(ctx):
    
    def get_links2():
        URL = "https://www.ea.com/games/apex-legends/news#news"
        URL2 = "https://www.ea.com/games/apex-legends/news#game-updates"
        page = requests.get(URL)
        page2 = requests.get(URL2)

        soup = BeautifulSoup(page.content,"html.parser")
        soup2 = BeautifulSoup(page2.content,"html.parser")

        links = []
        dates = []
        links2 = []
        dates2 = []
        for tag in soup.find_all('ea-tile'):
            dates.append(parser.parse(tag.find_all('div')[-1].contents[0]))
            links.append("https://www.ea.com" +tag.find_all('a')[0]['href'])

        for tag2 in soup2.find_all('ea-tile'):
            dates2.append(parser.parse(tag2.find_all('div')[-1].contents[0]))
            links2.append("https://www.ea.com" +tag2.find_all('a')[0]['href'])

        if dates[0] <= dates2[0]:
            return links2
        else:
            return links

    links2 = get_links2()
    #await ctx.defer()
    view = Scroller(links2)
    msg = await ctx.respond(content = links2[0], view=view)
    timeout = await view.wait()
    if timeout:
      if isinstance(msg,discord.WebhookMessage):
        await msg.edit(view=None)
      elif isinstance(msg,discord.Interaction):
        await msg.edit_original_message(view=None)

@bot.slash_command(name="media",
             description="This command fetches Apex Legends media from EA website",guild_ids=guild_ids)
async def media(ctx):
    await ctx.defer()
    
    def get_links():
        URL = "https://www.ea.com/games/apex-legends/media"
        page = requests.get(URL)

        soup = BeautifulSoup(page.content,"html.parser")
        links = []
        for tag in soup.find_all('ea-tile')[1:]:
            try:
                links.append("https://www.ea.com" +tag['link-url'])
            except Exception as e:
                continue
        return links

    links = get_links()
    #await ctx.defer()
    view = Scroller(links)
    msg = await ctx.respond(content = links[0], view=view)
    timeout = await view.wait()
    if timeout:
      if isinstance(msg,discord.WebhookMessage):
        await msg.edit(view=None)
      elif isinstance(msg,discord.Interaction):
        await msg.edit_original_message(view=None)


keep_alive()
bot.run(TOKEN)
