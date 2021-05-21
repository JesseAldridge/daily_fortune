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
  bot_name = DEFAULT_BOT_NAME
  chime_in_rate = 0.4

PERSONALITY_TO_MESSAGES = {}
for path in glob.glob(os.path.join('personalities', '*.txt')):
  with open(path) as f:
    personality_name = os.path.splitext(os.path.basename(path))[0]
    PERSONALITY_TO_MESSAGES[personality_name] = f.read().strip().splitlines()

def reset_personality():
  g.recent_messages = PERSONALITY_TO_MESSAGES[g.bot_name]
  return g.bot_name in PERSONALITY_TO_MESSAGES

reset_personality()

@client.event
async def on_ready(*a, **kw):
  print('on ready:', a, kw)
  for guild in client.guilds:
    print('guild:', guild)
    for channel in guild.channels:
      print('channel:', channel)
      if hasattr(channel, 'send'):
        await admin_message(channel, 'bot rebooted')

@client.event
async def on_message(message):
  print('on message:', message.content)

  async def admin_message_(msg_str):
    await admin_message(message.channel, msg_str)

  author = g.bot_name if 'daily fortune#' in str(message.author) else message.author

  recent_messages = g.recent_messages

  if not message.content.startswith(',') and not message.content.startswith('admin:'):
    recent_messages.append(f'{author}: {message.content}')
    recent_messages = recent_messages[-20:]

  if message.author == client.user:
    return

  if message.content == ',help':
    await admin_message_('```,reset\n,set name <name>\n,set chime in rate <rate>```')
  elif message.content == ',reset':
    g.recent_messages = []
    reset_personality()
    await admin_message_(f'bot reset')
  elif message.content.startswith(',set name'):
    bot_name = message.content.split()[-1]
    g.bot_name = bot_name
    is_found = reset_personality()
    await admin_message_(f'set bot name to {g.bot_name}; personality found: {is_found}')
    if not is_found:
      g.bot_name += f'#{int(random.random() * 1000)}'
  elif message.content.startswith(',set chime in rate'):
    try:
      g.chime_in_rate = float(message.content.split()[-1])
    except ValueError:
      pass
    else:
      await admin_message_(f'set chime in rate to {g.chime_in_rate}')
  else:
    roll = random.random()
    print('roll:', roll)
    if roll < g.chime_in_rate:
      await chime_in(message.channel, recent_messages, message)

async def chime_in(channel, recent_messages, message):
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
    max_tokens=200,
    top_p=1,
    frequency_penalty=0.0,
    presence_penalty=0.6,
    stop=["\n"]
  )

  print('response:', response)

  response_text = response.choices[0].text
  if response_text:
    await channel.send(response_text)

async def admin_message(channel, msg):
  await channel.send(f'admin: *{msg}*')

client.run(discord_config['bot_token'])
