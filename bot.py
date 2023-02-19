import discord
from discord.ext import commands
import json
import os
from discord import ui
from typing import Literal

EmbedColour = 0x00ff00

config = json.load(open(os.path.join(os.path.dirname(__file__), 'config.json')))
intents = discord.Intents.all()

if config["Status Type (Playing, Watching, Listening) Default is Playing"] == "Listening":
	activity=discord.Activity(type=discord.ActivityType.listening, name=config["Status"])
elif config["Status Type (Playing, Watching, Listening) Default is Playing"] == "Watching":
	activity=discord.Activity(type=discord.ActivityType.watching, name=config["Status"])
elif config["Status Type (Playing, Watching, Listening) Default is Playing"] == "Playing":
	activity=discord.Game(name=config["Status"])
else:
	activity=discord.Game(name=config["Status"])

class Bot(commands.Bot):
	def __init__(self):
		super().__init__(command_prefix=config["Prefix"], intents=intents, activity=activity)
	
	async def setup_hook(self):
		bot.tree.copy_global_to(guild=discord.Object(id=int(config["Guild ID"])))
		await bot.tree.sync(guild=discord.Object(id=int(config["Guild ID"])))
		self.add_view(SelectAppView())

bot = Bot()
bot.remove_command('help')

if config["Enable Help Command"] == "true":
	@bot.hybrid_command(name = "help", description = "Help. Made by Murder#0845", with_app_command=True)
	async def sendpanel(ctx):
		embed = discord.Embed(title = "Application bot help", description = f"""
		**Commands:**
		{config["Prefix"]}sendpanel `panel`
		{config["Prefix"]}reply `@member` `message`

		**Slash commands:**
		This bot supports slash commands! 
		You can use them by typing `/` in the chat, and selecting which command you want to use!
		""", color=EmbedColour)
		embed.set_footer(text = "Made by Murder#0845")
		await ctx.reply(embed=embed)

@bot.event
async def on_ready():
	print(f"Bot is logged in as {bot.user}")
	print("Made by Murder#0845")
	print("--------------------------------")

async def log(title, description, color):
	if config["Enable Logging"] == "true" or config["Enable Logging"] == True:
		embed = discord.Embed(title=title, description=description, color=color)
		channel = bot.get_channel(int(config["Log Channel ID"]))
		await channel.send(embed=embed)

async def get_input():
	while True:
		msg = await bot.wait_for("message")
		if msg.author != bot.user:
			return msg.content

class SendOrDeny(discord.ui.View):
	def __init__(self, member, panel, embed):
		super().__init__()
		self.member = member
		self.panel = panel
		self.embed = embed
	
	@discord.ui.button(label="Send", style=discord.ButtonStyle.green)
	async def send(self, button, interaction):
		channel = bot.get_channel(int(config["Application Response Channel ID"]))
		await channel.send(embed=self.embed)
		await button.response.send_message(embed = discord.Embed(description = "Sent!", color=0x00ff00), ephemeral=True)
		self.stop()
		return
	
	@discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
	async def cancel(self, button, interaction):
		await button.response.send_message(embed = discord.Embed(description = "Cancelled application."))
		self.stop()
		return


class cancel(discord.ui.View):
	def __init__(self):
		super().__init__()
	
	@discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
	async def cancel(self, button, interaction):
		await button.response.send_message(embed = discord.Embed(description = "Cancelled application."))
		self.stop()
		return

class SelectApp(discord.ui.Select):
	def __init__(self):
		options = []
		for application in config["Applications"]:
			options.append(discord.SelectOption(label=application))
	
		super().__init__(placeholder="Select an application", min_values=1, max_values=1, options=options, custom_id="select_app")

	async def callback(self, interaction: discord.Interaction):
		questions = config["Applications"][self.values[0]]
		await interaction.response.send_message(embed = discord.Embed(description = "Check your DM's with me!"), ephemeral=True)
		await interaction.user.send(embed = discord.Embed(title = f"Application for {self.values[0]}", description = "Please answer the questions below, simply by typing your answer! To cancel, press the `Cancel` button below."), view = cancel())
		questionans = []
		for question in questions:
			await interaction.user.send(embed = discord.Embed(description=question))
			msg = await get_input()
			questionans.append(msg)

		userappembed = discord.Embed(title = "Application overview")
		logappembed = discord.Embed(title = f"Application `{self.values[0]}` from {interaction.user.name}#{interaction.user.discriminator}", color = discord.Color.green())

		for i in range(len(questions)):
				logappembed.add_field(name = questions[i], value = questionans[i], inline = False)
				userappembed.add_field(name = questions[i], value = questionans[i], inline = False)


		
		userappembed.set_footer(text = f"Made by Murder#0845")
		logappembed.set_footer(text = f"Made by Murder#0845")

		await interaction.user.send(embed = userappembed, view = SendOrDeny(interaction.user, "name", logappembed))

class SelectAppView(discord.ui.View):
	def __init__(self):
		super().__init__(timeout=None)
		self.add_item(SelectApp())

@commands.has_role(int(config["Staff Role ID"]))
@bot.hybrid_command(name = "sendpanel", description = "Send a panel! Made by Murder#0845", with_app_command=True)
async def sendpanel(ctx):
	embed = discord.Embed(title = config["Embed"]["Title"], description = config["Embed"]["Description"])
	embed.set_footer(text = "Made by Murder#0845")
	await ctx.reply(embed=discord.Embed(description = "Panel sent!"), ephemeral = True)
	await ctx.send(embed=embed,view = SelectAppView())
	await log("Panel", f"A panel has been sent to {ctx.channel.mention}", 0x00ff00)

@commands.has_role(int(config["Staff Role ID"]))
@bot.hybrid_command(name = "reply", description = "Reply to a user through the bot! Made by Murder#0845", with_app_command=True)
async def sendpanel(ctx, member: discord.Member, message: str, colour: Literal["Red", "Green", "Blue"] = None):
	if colour == "Red":
		colour = 0xff0000
	elif colour == "Green":
		colour = 0x00ff00
	elif colour == "Blue":
		colour = 0x0000ff
	else:
		colour = 0x010000

	embed = discord.Embed(title = f"Message sent from {ctx.author.display_name}", description = message, color = colour)
	embed.set_footer(text = f"Made by Murder#0845")
	await member.send(embed = embed)

	await ctx.reply(embed = discord.Embed(title = f"Sent message to {member.display_name}", description = f"`{message}`", color = 0x00ff00), ephemeral=True)

@bot.event
async def on_command_error(ctx, error):
	print(error)
	if isinstance(error, commands.CommandOnCooldown):
		await ctx.reply(embed=discord.Embed(description = f"Please wait {error.retry_after:.2f} seconds before using this command again. Cooldowns are in place to prevent spamming in case unauthorised users get access to run this command on accident or through other means.", color = 0xff0000), ephemeral=True)
		return
	if isinstance(error, commands.MissingRole):
		await ctx.reply(embed=discord.Embed(description = f"You do not have permission to use this command.", color = 0xff0000), ephemeral=True)
		return
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.reply(embed=discord.Embed(description = f"Please provide all required arguments.", color = 0xff0000), ephemeral=True)
		return
	if isinstance(error, commands.BadArgument):
		await ctx.reply(embed=discord.Embed(description = f"Please provide a valid argument.", color = 0xff0000), ephemeral=True)
		return
	if isinstance(error, commands.CommandNotFound):
		await ctx.reply(embed=discord.Embed(description = f"Command not found.", color = 0xff0000), ephemeral=True)
		return
	if isinstance(error, commands.BotMissingPermissions):
		await ctx.reply(embed=discord.Embed(description = f"Bot is missing permissions.", color = 0xff0000), ephemeral=True)
		return
	if isinstance(error, commands.MissingPermissions):
		await ctx.reply(embed=discord.Embed(description = f"You are missing permissions.", color = 0xff0000), ephemeral=True)
		return
	if isinstance(error, commands.CommandInvokeError):
		await ctx.reply(embed=discord.Embed(description = f"An error has occured.", color = 0xff0000), ephemeral=True)
		return
	if isinstance(error, commands.CheckFailure):
		await ctx.reply(embed=discord.Embed(description = f"You do not have permission to use this command.", color = 0xff0000), ephemeral=True)
		return
	if isinstance(error, commands.CommandError):
		await ctx.reply(embed=discord.Embed(description = f"An error has occured.", color = 0xff0000), ephemeral=True)
		return
	if isinstance(error, commands.UserInputError):
		await ctx.reply(embed=discord.Embed(description = f"Please provide a valid argument.", color = 0xff0000), ephemeral=True)
		return
	if isinstance(error, commands.DisabledCommand):
		await ctx.reply(embed=discord.Embed(description = f"This command is disabled.", color = 0xff0000), ephemeral=True)
		return

bot.run(config["Bot Token"])
