import os, json, random, glob

import discord, openai


with open(os.path.expanduser('~/discord.json')) as f:
  discord_config = json.loads(f.read())

client = discord.Client()

with open(os.path.expanduser('~/open_ai.json')) as f:
  openai.api_key = json.loads(f.read()).get('api_key')

with open('prompt_qa.txt') as f:
  PROMPT_QA = f.read()

DEFAULT_BOT_NAME = 'penguin'

class g:
  recent_messages = []
  bot_name = f'{DEFAULT_BOT_NAME}#69420'
  chime_in_rate = 0.4

PERSONALITY_TO_MESSAGE = {}
for path in glob.glob(os.path.join('personalities', '*.txt')):
  with open(path) as f:
    personality_name = os.path.splitext(os.path.basename(path))[0]
    PERSONALITY_TO_MESSAGE[personality_name] = f.read()

g.recent_messages.append(f'{g.bot_name}: {PERSONALITY_TO_MESSAGE[DEFAULT_BOT_NAME]}')

@client.event
async def on_ready(*a, **kw):
  print('on ready:', a, kw)
  for guild in client.guilds:
    print('guild:', guild)
    for category_channel in guild.channels:
      print('category channel:', category_channel)
      for channel in category_channel.channels:
        print('channel:', channel)
        admin_message(channel, '*bot rebooted*')

@client.event
async def on_message(message):
  print('on message')

  async def admin_message_(msg_str):
    await admin_message(message.channel, msg_str)

  author = g.bot_name if 'daily fortune#' in str(message.author) else message.author

  recent_messages = g.recent_messages

  if not message.content.startswith(','):
    recent_messages.append(f'{author}: {message.content}')
    recent_messages = recent_messages[-20:]

  if message.author == client.user:
    return

  # if message.content.strip().endswith('?'):
  #   await answer_question(message)
  if message.content == ',clear messages':
    g.recent_messages = []
    await admin_message_(f'recent messages cleared')
  elif message.content.startswith(',set name'):
    bot_name = message.content.split()[-1]
    g.bot_name = f'{bot_name}#{int(random.random() * 1000)}'
    is_found = False
    if bot_name in PERSONALITY_TO_MESSAGE:
      is_found = True
      g.recent_messages.append(f'{g.bot_name}: {PERSONALITY_TO_MESSAGE[bot_name]}')
    await admin_message_(f'set bot name to {g.bot_name}; personality found: {is_found}')
  elif message.content.startswith(',set chime in rate'):
    try:
      g.chime_in_rate = float(message.content.split()[-1])
    except ValueError:
      pass
    else:
      await admin_message_(message, f'set chime in rate to {g.chime_in_rate}')
  else:
    roll = random.random()
    print('roll:', roll)
    if roll < g.chime_in_rate:
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
  await admin_message(message, response.choices[0].text)

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
    await admin_message(response_text)

async def admin_message(channel, msg):
  await channel.send(f'admin: *{msg}*')

client.run(discord_config['bot_token'])
