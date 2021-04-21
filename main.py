import os, json, random

import discord, openai


with open(os.path.expanduser('~/discord.json')) as f:
  discord_config = json.loads(f.read())

client = discord.Client()

with open(os.path.expanduser('~/open_ai.json')) as f:
  openai.api_key = json.loads(f.read()).get('api_key')

class g:
  recent_messages = []

@client.event
async def on_message(message):
  print('on message')

  # if message.author == client.user:
  #   return

  recent_messages = g.recent_messages
  recent_messages.append(message.content)
  recent_messages = recent_messages[-10:]

  if random.random() < .1:
    print('responding...')
    response = openai.Completion.create(
      engine="davinci",
      prompt='\n'.join(recent_messages),
      temperature=0.9,
      max_tokens=20,
      top_p=1,
      frequency_penalty=0.0,
      presence_penalty=0.6,
      # stop=["\n", " Human:", " AI:"]
    )
    await message.channel.send(response.choices[0].text)

client.run(discord_config['bot_token'])
