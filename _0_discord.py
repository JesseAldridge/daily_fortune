import os, json

import discord

class MyClient(discord.Client):
  def __init__(self, ChatBotClass, *a, **kw):
    discord.Client.__init__(self, *a, **kw)
    self.ChatBotClass = ChatBotClass

  async def on_ready(self):
    for guild in self.guilds:
      print('guild:', guild)
      for channel in guild.channels:
        print('channel:', channel)
        if hasattr(channel, 'send'):
          self.chat_bot = self.ChatBotClass()
          await self.chat_bot.init(channel, self)
          return

  async def on_message(self, message):
    await self.chat_bot.on_message(message)

def main(ChatBot):
  with open(os.path.expanduser('~/discord.json')) as f:
    discord_config = json.loads(f.read())

  client = MyClient(ChatBot)
  client.run(discord_config['bot_token'])

def test():
  class ChatBot:
    def __init__(self, channel, client):
      self.channel = channel
      self.client = client

    async def on_message(slef, message):
      print('message:', message.content)

  main(ChatBot)

if __name__ == '__main__':
  test()
