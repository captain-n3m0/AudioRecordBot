import discord
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Enter your Google Drive credentials
creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/drive'])

# Define the default command prefix
default_prefix = "!"

# Function to upload file to Google Drive
def upload_to_drive(file_name):
    try:
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': file_name}
        media = discord.File(file_name).read()
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print('File ID: %s' % file.get('id'))
        return f"https://drive.google.com/file/d/{file.get('id')}"
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

# Create a Discord client
client = discord.Client()

# When the bot is ready, print a message to the console
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

# When a message is sent in the channel, join the voice channel and record the discussion
@client.event
async def on_message(message):
    # Check if the message starts with the command prefix
    if message.content.startswith(command_prefix):
        # Split the message into command and arguments
        command = message.content.split()[0][len(command_prefix):].lower()
        args = message.content.split()[1:]
        # Check if the command is to change the prefix
        if command == "prefix" and len(args) == 1:
            # Update the command prefix and notify the user
            global command_prefix
            command_prefix = args[0]
            await message.channel.send(f"The command prefix has been changed to '{command_prefix}'")
        # Check if the command is to start recording
        elif command == "record":
            # Get the voice channel the user is in
            voice_channel = message.author.voice.channel
            # Join the voice channel
            vc = await voice_channel.connect()
            # Start recording
            vc.start_recording(f'{message.author.name}_discussion.opus')
            # Wait for 60 seconds
            await asyncio.sleep(60)
            # Stop recording and disconnect from the voice channel
            vc.stop_recording()
            await vc.disconnect()
            # Upload the recorded discussion to Google Drive
            file_link = upload_to_drive(f'{message.author.name}_discussion.opus')
            # Send the Google Drive link to the chat
            await message.channel.send(f'{message.author.mention}, here is the link to the recorded discussion: {file_link}')
        # Check if the command is to list the available commands
        elif command == "help":
            # Send a message with the available commands and their functions
            help_message = "Here are the available commands:\n" \
                            f"{command_prefix}prefix [new prefix] - Change the command prefix\n" \
                            f"{command_prefix}record - Join the voice channel and record the discussion\n" \
                            f"{command_prefix}help - List the available commands and their functions"
            await message.channel.send(help_message)

# Set the initial command prefix
command_prefix = default_prefix

# Run the bot
client.run('YOUR_DISCORD_BOT_TOKEN')
