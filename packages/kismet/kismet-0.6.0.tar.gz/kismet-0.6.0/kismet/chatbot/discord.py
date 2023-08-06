from os import getenv
from discord import Client

from kismet.core import process_markdown, process_messages

token = getenv("DISCORD_TOKEN", "")
clientid = getenv("DISCORD_CLIENTID", "0")
permissions = getenv("DISCORD_PERMISSIONS", "377957238848")

oauth2_template = (
    "https://discordapp.com/oauth2/authorize?scope=bot&client_id=%s&permissions=%s"
)
oauth2_url = oauth2_template % (clientid, permissions)
print("Use the following URL to invite:")
print(oauth2_url)


# Define client
client = Client()

def replace_mentions(string: str):
    return string.replace("<@" + str(client.user.id) + ">", "Kismet")


@client.event
async def on_message(event):
    if event.author == client.user:
        return
    else:
        response = process_markdown(event.content, "{0.author.mention}".format(event))
        if response:
            await event.channel.send(response)
        channel = event.channel
        history = [message async for message in channel.history(limit=16)]
        reply = process_messages(history)
        if reply:
            await event.channel.send(reply)


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")


client.run(token)
