from os import getenv
from discord import Client, Message as DiscordMessage

from kismet.core import process_markdown, process_messages
from kismet.types import Message

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

def convert_message(message: DiscordMessage):
    return Message(
        message_id=message.id,
        author_id=message.author.id,
        created_at=message.created_at,
        edited_at=message.edited_at,
        reply_id=message.reference.message_id if message.reference else None,
        content=message.content,
    )

@client.event
async def on_message(event):
    if event.author == client.user:
        return
    else:
        response = process_markdown(event.content)
        if response:
            await event.reply(response)
        channel = event.channel
        history = [convert_message(message) async for message in channel.history(limit=16)]
        reply = process_messages(history, client.user.id)
        if reply:
            await event.channel.send(reply)


@client.event
async def on_ready():
    print("Logged in as")
    print(client.user.name)
    print(client.user.id)
    print("------")


client.run(token)
