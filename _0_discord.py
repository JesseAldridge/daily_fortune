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

def main(ChatBot):
  with open(os.path.expanduser('~/discord.json')) as f:
    discord_config = json.loads(f.read())

  print('creating client...')
  client = MyClient(ChatBot)
  client.run(discord_config['bot_token'])

def test():
  class ChatBot:
    def __init__(self, channel, client):
      self.channel = channel
      self.client = client

  main(ChatBot)

if __name__ == '__main__':
  test()
