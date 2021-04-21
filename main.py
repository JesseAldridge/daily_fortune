import os, json, random

import discord, openai


with open(os.path.expanduser('~/discord.json')) as f:
  discord_config = json.loads(f.read())

client = discord.Client()

with open(os.path.expanduser('~/open_ai.json')) as f:
  openai.api_key = json.loads(f.read()).get('api_key')

with open('prompt_qa.txt') as f:
  PROMPT_QA = f.read()

class g:
  recent_messages = []

@client.event
async def on_message(message):
  print('on message')

  if message.author == client.user:
    return

  recent_messages = g.recent_messages
  recent_messages.append(message.content)
  recent_messages = recent_messages[-10:]

  if message.content.strip().endswith('?'):
    await answer_question(message)
  elif random.random() < .2:
    await chime_in(recent_messages, message)

async def answer_question(message):
  prompt_str = f'{PROMPT_QA}\nQ: {message.content}\nA:'

  print('prompt:', prompt_str)

  response = openai.Completion.create(
    engine="davinci",
    prompt=prompt_str,
    temperature=0,
    max_tokens=100,
    top_p=1,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    stop=["\n"],
  )
  await message.channel.send(response.choices[0].text)

async def chime_in(recent_messages, message):
  response = openai.Completion.create(
    engine="davinci",
    prompt='\n'.join(recent_messages),
    temperature=0.9,
    max_tokens=20,
    top_p=1,
    frequency_penalty=0.0,
    presence_penalty=0.6,
    stop=["\n"]
  )
  await message.channel.send(response.choices[0].text)


client.run(discord_config['bot_token'])
