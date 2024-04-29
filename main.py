import discord
import discord.ext
from discord.ext import tasks
from discord import app_commands
from discord.ext import commands
import random
import list
import time
from datetime import datetime, timedelta
import pytz
from pytz import timezone
import asyncio


# INTENTS LIST
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = discord.Client(command_prefix=',', intents=intents)
tree = app_commands.CommandTree(client)

forum_channel = 1234393911309635687
qotd_log_channel = 1234426737941549076
current_day = 0

async def randomQuestionPicker():
    global choice
    choice = random.choice(list.Questions)
    if choice:
        return choice

@tasks.loop(hours=1)
async def send_question():
    current_time = datetime.now(pytz.timezone('Asia/Singapore'))
    print(current_time)

    if current_time.hour == 6:
       day = str(current_day + 1)
       thread_name = ("DAY: "+day)
       chosen_question = await randomQuestionPicker()
       list.Questions.remove(chosen_question)
       channel = client.get_channel(forum_channel)
       thread = await channel.create_thread(name=thread_name, content=chosen_question)

@tree.command(name="create")
async def create(ctx):
    day = str(current_day + 1)
    thread_name = ("DAY: "+day)
    chosen_question = await randomQuestionPicker()
    list.Questions.remove(chosen_question)

    channel = client.get_channel(forum_channel)
    thread = await channel.create_thread(name=thread_name, content=chosen_question)


# ON READY, START BOT
class decide(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self,interaction: discord.Interaction,button: discord.ui.Button):
        list.Questions.append(interaction.message.content)
        await interaction.response.defer()
        formulated_status_message = str(interaction.message.content + "\n***STATUS***: ACCEPTED")
        await interaction.edit_original_response(content=formulated_status_message,view=None)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction,button: discord.ui.Button):
        await interaction.response.defer()
        formulated_status_message = str(interaction.message.content + "\n***STATUS***: DECLINED")
        await interaction.edit_original_response(content=formulated_status_message,view=None)

@tree.command(name="qotd")
async def qotd(interaction: discord.Interaction, question: str):
    if question:
        asker = interaction.user.name
        formulated_question = "```"+question+"```"+"\nAsked by: "+asker

        log_channel = client.get_channel(qotd_log_channel)
        view = decide()
        await log_channel.send(content=(formulated_question),view=view)

@client.event
async def on_ready():
    print("Bot is Ready!")
    client.loop.create_task(send_question())

@tree.command(name="sync", description="owner only")
async def sync(interaction: discord.Interaction):
   await tree.sync()
   print("synced")


client.run(list.client_token)