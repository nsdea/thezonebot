import movienight, music

import os
import dotenv
import socket
import discord
import asyncio
import datetime

from discord.ext import commands
from discord.app import Option
from discordTogether import DiscordTogether

dotenv.load_dotenv()  # initialize virtual environment

COLOR = 0x6e00ff
TESTING_MODE = True
PREFIX = '/'

client = commands.Bot(command_prefix='z/', intents=discord.Intents.all())
togetherControl = DiscordTogether(client)

async def status_task():
    while True:
        await client.change_presence(activity=discord.Game(f'Fortnite'))
        await asyncio.sleep(10)

@client.event
async def on_ready():
    print('ONLINE as', client.user)
    client.loop.create_task(status_task())

@client.event
async def on_command_error(ctx, error):
    return
    # error: 'error message'
    error_messages = {
        commands.ExtensionError: 'Es gab ein Problem in einer Erweiterung ("cog").',
        commands.CheckFailure: 'Es gab ein Problem mit der Überprüfung, ob etwas ausgeführt werden soll.',
        commands.UserInputError: 'Überprüfe bitte deine Eingabe.',
        commands.CommandNotFound: f'Befehl nicht gefunden. Benutze **`{PREFIX}help`** für eine Befehlsliste.',
        commands.MissingRequiredArgument: f'Du hast ein Befehlsargument vergessen, benutze **`{PREFIX}help {ctx.message.content.replace(PREFIX, "").split()[0]}`** für Hilfe.',
        commands.TooManyArguments: f'Du hast zu viele Argumente eingegeben, benutze **`{PREFIX}help {ctx.message.content.replace(PREFIX, "").split()[0]}`** für Hilfe.',
        commands.Cooldown: 'Bitte warte, du kannst diesen Befehl erst später ausführen.',
        commands.NoPrivateMessage: 'Dies Funktioniert nicht in DM-Kanälen.',
        commands.MissingPermissions: 'Du brauchst leider folgende Berechtigung(en), um das zu tun:',
        commands.BotMissingPermissions: 'Ich brauche folgende Berechtigung(en), um das zu tun:',
        commands.BadArgument: f'Es gab ein Problem mit dem Konvertieren der Argumente, benutze den folgenden Befehl für Hilfe: **`{PREFIX}help {ctx.message.content.replace(PREFIX, "").split()[0]}`**',
    }

    error_msg = 'Unbekannter Fehler.'

    # create the error message using the dict above
    for e in error_messages.keys():
        if isinstance(error, e):
            error_msg = error_messages[e]

    # other errors:
    # - too long
    if 'Invalid Form Body' in str(error): error_msg = 'Ich kann leider nicht die Nachricht senden, weil sie zu lang gewesen wäre.'

    # - bug
    if 'Command raised an exception' in str(error): error_msg = 'Huch, es gab ein Problem mit dem Code.'

    # add detailed info
    if isinstance(error, commands.MissingPermissions) or isinstance(error, commands.BotMissingPermissions):
        error_msg += f'\n**`{", ".join(error.missing_perms)}`**\n'

    # add full error description formatted as a code text
    error_msg += '\n\n**Konsole:**\n```\n' + str(error) + '\n```'

    # create a cool embed
    embed = discord.Embed(
        title='Command Error',
        description=error_msg,
        color=0xFF0000
    )

    # send it
    await ctx.send(embed=embed)
    if TESTING_MODE or error_msg == 'Unbekannter Fehler.': raise error  # if this is a testing system, show the full error in the console

@client.slash_command()
async def movienight(
    ctx,
    date: Option(str, 'Uhrzeit (und ggf. Datum)'),
    topic: Option(str, 'Thema', required=False, default='YouTube Together'),
):

    invite_link = await togetherControl.create_link(ctx.author.voice.channel.id, 'youtube', max_age=604800)
    await ctx.send(embed=discord.Embed(title='Hier klicken:',  description=invite_link))
    
@client.slash_command()
async def commandinfo(
    ctx,
    name: Option(str, 'Ein spezifischer Befehl:')
):
    await ctx.send('Dies ist in der Beta.')
    return
    if name:
        for c in client.commands:
            if name.lower() == c.name or name.lower() in list(c.aliases):
                text = f'''
        **Information:** {c.help if c.help else ' - '}
        **Argumente:** {c.usage if c.usage else ' - '}
        **Aliasse:** {', '.join(c.aliases) if c.aliases else ' - '}
        '''
                embed = discord.Embed(
                    title='Command ' + c.name, color=COLOR, description=text)
                await ctx.send(embed=embed)
                return

        embed = discord.Embed(title='Command not found', color=COLOR,
                              description='This command does not exist...')
        await ctx.send(embed=embed)
        return

    def sortkey(x):
        return x.name

    categories = {
        '⚙️': 'Hauptsystem',
        '📃': 'Info',
        '🔧': 'Tools',
        '🔒': 'Admin-Tools',
        '🎮': 'Spiel & Spaß',
        '🔩': 'Andere'}

    # ok, somehow I managed to get this to work, don't ask me how, but it WORKS
    text = ''
    for category in categories.keys():
        text += f'\n{category} **{categories[category]}**\n'
        for command in sorted(client.commands, key=sortkey):
            if command.help.startswith(category):
                if command.aliases:
                    text += f'{command.name} *({"/".join(command.aliases)})*\n'
                else:
                    text += f'{command.name}\n'
                continue
            
    embed = discord.Embed(title='Befehle', color=COLOR, description=text)
    embed.set_footer(
        text=f'Benutze {PREFIX}help <command> für mehr Info über einen bestimmten Befehl.')
    await ctx.send(embed=embed)

# load cogs
# credit: https://youtu.be/vQw8cFfZPx0
# for filename in os.listdir(os.getcwd() + '/src/cogs/'):
#     if filename.endswith('.py'):
#         client.load_extension(f'cogs.{filename[:-3]}')

client.add_cog(music.Music(client))

client.run(os.getenv('DISCORD_TOKEN'))  # run bot with the token set in the .env file