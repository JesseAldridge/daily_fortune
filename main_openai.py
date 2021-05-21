import os, json, random, glob

import discord, openai


with open(os.path.expanduser('~/discord.json')) as f:
  discord_config = json.loads(f.read())

client = discord.Client()

with open(os.path.expanduser('~/open_ai.json')) as f:
  openai.api_key = json.loads(f.read()).get('api_key')

with open('prompt_qa.txt') as f:
  PROMPT_QA = f.read()

PERSONALITY_TO_MESSAGE = {}
for path in glob.glob(os.path.join('personalities/*.txt')):
  with open(path) as f:
    personality_name = os.splitext(os.path.basename(path))[0]
    PERSONALITY_TO_MESSAGE[personality_name] = f.read()

class g:
  recent_messages = []
  bot_name = 'Jane#69420'

@client.event
async def on_message(message):
  print('on message')

  author = g.bot_name if 'daily fortune#' in str(message.author) else message.author

  recent_messages = g.recent_messages
  recent_messages.append(f'{author}: {message.content}')
  recent_messages = recent_messages[-20:]

  if message.author == client.user:
    return

  if message.content.strip().endswith('?'):
    await answer_question(message)
  elif message.content == ',reboot':
    g.recent_messages = []
  elif message.content.startswith(',setname'):
    bot_name = message.content.split()[-1]
    g.bot_name = f'{bot_name}#{int(random.random() * 1000)}'
    if bot_name in PERSONALITY_TO_MESSAGE:
      g.recent_messages.append(f'{g.bot_name}: {PERSONALITY_TO_MESSAGE[bot_name]}')
  else:
    roll = random.random()
    print('roll:', roll)
    if roll < .4:
      await chime_in(recent_messages, message)

async def answer_question(message):
  prompt_str = f'{PROMPT_QA}\nQ: {message.content}\nA:'

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
  recent_bot_messages = []
  for message_str in recent_messages:
    if message_str.startswith(g.bot_name):
      recent_bot_messages.append(message_str)

  if(len(recent_bot_messages) >= 2 and recent_bot_messages[-1] == recent_bot_messages[-2]):
    recent_messages = [msg for msg in recent_messages if msg != recent_bot_messages[-1]]

  prompt = '\n'.join(recent_messages) + f'\n{g.bot_name}: '
  print('prompt:', prompt)

  response = openai.Completion.create(
    engine="davinci",
    prompt=prompt,
    temperature=0.9,
    max_tokens=100,
    top_p=1,
    frequency_penalty=0.0,
    presence_penalty=0.6,
    stop=["\n"]
  )

  print('response:', response)

  response_text = response.choices[0].text
  if response_text:
    await message.channel.send(response_text)


client.run(discord_config['bot_token'])
