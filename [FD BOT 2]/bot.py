import discord
from discord.ext import commands, tasks
import configparser
import asyncio

config = configparser.ConfigParser()
config.read('config.ini')

TOKEN = config['FD']['token']
ADMIN_ROLE_ID = int(config['FD']['admin_role_id'])
BANNED_WORDS = config['FD']['banned_words'].split(',')
RULES_CHANNEL_ID = int(config['FD']['rules_channel_id'])
POLL_CHANNEL_ID = int(config['FD']['poll_channel_id'])
PARTNER_SERVER_ID = int(config['FD']['partner_server_id'])

intents = discord.Intents.default()
intents.members = True
intents.messages = True  
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'{bot.user} is verbonden met Discord!')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    for word in BANNED_WORDS:
        if word in message.content.lower():
            await message.channel.send(f"{message.author.mention}, gelieve geen ongepaste taal te gebruiken!")
            await asyncio.sleep(1)
            await message.delete()
            async for previous_message in message.channel.history(limit=1):
                await previous_message.delete()
                break

    if "http" in message.content or "discord.gg/" in message.content:
        await message.channel.send(f"{message.author.mention}, het plaatsen van links is hier niet toegestaan!")
        await asyncio.sleep(1)
        await message.delete()
        async for previous_message in message.channel.history(limit=1):
            await previous_message.delete()
            break

    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Ongeldige opdracht.")


@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(embed=discord.Embed(description=f'{member} is verbannen.', color=discord.Color.red()))


@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(embed=discord.Embed(description=f'{user} is geunbanned.', color=discord.Color.green()))
            return


@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(embed=discord.Embed(description=f'{member} is gekickt.', color=discord.Color.orange()))


@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def purge(ctx, limit: int):
    await ctx.channel.purge(limit=limit + 1)
    await ctx.send(embed=discord.Embed(description=f'{limit} berichten zijn verwijderd.', color=discord.Color.blue()))


@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def regels(ctx):
    channel = bot.get_channel(RULES_CHANNEL_ID)

    embed = discord.Embed(title="Regels", description="Voer de regels hier in.", color=0x00ff00)
    embed.add_field(name="Rule 1", value="Vul dit zelf in.", inline=False)
    embed.add_field(name="Rule 2", value="Vul dit zelf in.", inline=False)
    embed.add_field(name="Rule 3", value="Vul dit zelf in.", inline=False)

    await channel.send(embed=embed)


@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def poll(ctx, *, poll_message: str):
    channel = bot.get_channel(POLL_CHANNEL_ID)

    title, question = poll_message.split("|", 1)
    title = title.strip()
    question = question.strip()

    embed = discord.Embed(title=title, description=question, color=0xffd700)
    message = await channel.send(embed=embed)
    await message.add_reaction('✅')
    await message.add_reaction('❌')


@bot.event
async def on_guild_join(guild):
    channel = discord.utils.get(guild.text_channels, position=0)

    embed = discord.Embed(title="Credits", color=0xFF5733)
    embed.add_field(name="Made for", value="[fdscripts](https://discord.gg/fdscripts)", inline=False)
    embed.add_field(name="Made by", value="Petrichor2_", inline=False)

    await channel.send(embed=embed)


@bot.command()
async def credit(ctx):
    embed = discord.Embed(title="Credits", color=0xFF5733)
    embed.add_field(name="Made for", value="[fdscripts](https://discord.gg/fdscripts)", inline=False)
    embed.add_field(name="Made by", value="Petrichor2_", inline=False)


    await ctx.send(embed=embed)

@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def partner(ctx, *, text: str):
    await ctx.send(text)

@bot.command()
@commands.has_role(ADMIN_ROLE_ID)
async def product(ctx, *, text: str):
    if '|' in text:
        title, description = map(str.strip, text.split('|', 1))
    else:
        title, description = "Product", text

    embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
    await ctx.send(embed=embed)

bot.run(TOKEN)
