import os, json

import discord

class ChatBot:
  async def admin_message(self, channel, msg):
    await channel.send(f'*admin*: {msg}')

class MyClient(discord.Client):
  def __init__(self, *a, **kw):
    discord.Client.__init__(self, *a, **kw)
    self.chat_bot = ChatBot()

  async def on_ready(self):
    for guild in self.guilds:
      print('guild:', guild)
      for channel in guild.channels:
        print('channel:', channel)
        if hasattr(channel, 'send'):
          await self.chat_bot.admin_message(channel, 'testing')

def main():
  with open(os.path.expanduser('~/discord.json')) as f:
    discord_config = json.loads(f.read())

  client = MyClient()
  client.run(discord_config['bot_token'])

if __name__ == '__main__':
  main()
