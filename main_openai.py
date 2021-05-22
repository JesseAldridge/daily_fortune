import os, json, random, glob, textwrap

import discord, openai


with open(os.path.expanduser('~/discord.json')) as f:
  discord_config = json.loads(f.read())

client = discord.Client()

with open(os.path.expanduser('~/open_ai.json')) as f:
  openai.api_key = json.loads(f.read()).get('api_key')

with open('prompt_qa.txt') as f:
  PROMPT_QA = f.read()

class g:
  bot_name = None
  recent_messages = []

vars = {
  # 'chime_in_rate': 0.4,
  # 'temperature': 0.9,
  # 'frequency_penalty': 0.2,
  # 'presence_penalty': 0.6,
  # 'change_personality_rate': 0.1,
  'chime_in_rate': random.random(),
  'temperature': random.random(),
  'frequency_penalty': random.random(),
  'presence_penalty': random.random(),
  'change_personality_rate': random.random(),
}

PERSONALITY_TO_MESSAGES = {}
for path in glob.glob(os.path.join('personalities', '*.txt')):
  with open(path) as f:
    personality_name = os.path.splitext(os.path.basename(path))[0]
    PERSONALITY_TO_MESSAGES[personality_name] = f.read().strip().splitlines()

def set_personality(bot_name):
  g.bot_name = bot_name
  g.recent_messages = PERSONALITY_TO_MESSAGES.get(bot_name) or g.recent_messages
  print('set personality to:', g.bot_name)
  return bot_name in PERSONALITY_TO_MESSAGES

def set_random_personality():
  set_personality(random.choice(list(PERSONALITY_TO_MESSAGES.keys())))

set_random_personality()

@client.event
async def on_ready(*a, **kw):
  print('on ready:', a, kw)
  for guild in client.guilds:
    print('guild:', guild)
    for channel in guild.channels:
      print('channel:', channel)
      if hasattr(channel, 'send'):
        await admin_message(channel, 'bot rebooted')
        await admin_message_(f'```bot_name: {g.bot_nme}\n{json.dumps(vars, indent=2)}```')

@client.event
async def on_message(message):
  print('on message:', message.content)

  async def admin_message_(msg_str):
    await admin_message(message.channel, msg_str)

  author = g.bot_name if 'daily fortune#' in str(message.author) else message.author

  if not message.content.startswith(',') and not message.content.startswith('*admin*:'):
    g.recent_messages.append(f'{author}: {message.content}')
    g.recent_messages = g.recent_messages[-20:]

  if message.author == client.user:
    return

  if message.content == ',help':
    await admin_message_(textwrap.dedent(f'''
      ```
      ,reset
      ,debug
      ,set name <name>
      ,set <variable> <value>
      variables: {list(vars.keys())}
      ```
    '''))
  elif message.content == ',reset':
    set_personality(g.bot_name)
    await admin_message_(f'bot reset')
  elif message.content == ',debug':
    await admin_message_(f'```bot_name: {g.bot_nme}\n{json.dumps(vars, indent=2)}```')
  elif message.content.startswith(',set name'):
    bot_name = message.content.split()[-1]
    is_found = set_personality(bot_name)
    await admin_message_(f'set bot name to {g.bot_name}; personality found: {is_found}')
    if not is_found:
      g.bot_name += f'#{int(random.random() * 1000)}'
  elif message.content.startswith(',set '):
    await set_variable(message)
  else:
    if random.random() < vars.get('chime_in_rate'):
      if random.random() < vars.get('change_personality_rate'):
        set_random_personality()
      await chime_in(message.channel, message)

async def set_variable(message):
  async def admin_message_(msg_str):
    await admin_message(message.channel, msg_str)

  var, val_str = message.content.split(',set ', 1)[1].rsplit(' ', 1)
  try:
    val = float(val_str)
  except ValueError:
    await admin_message_(f'invalid value (should be a number between 0 and 1)')
  if not(val >= 0 and val <= 1):
    await admin_message_(f'invalid value (should be a number between 0 and 1)')
    return
  if var not in vars:
    await admin_message_(f'unrecognized variable name')
    return

  vars[var] = val
  await admin_message_(f'set {var} to {val}')

async def chime_in(channel, message):
  prompt = '\n'.join(g.recent_messages) + f'\n{g.bot_name}: '
  print('prompt:', prompt)

  response = openai.Completion.create(
    engine="davinci",
    prompt=prompt,
    temperature=vars.get('temperature'),
    max_tokens=200,
    top_p=1,
    frequency_penalty=vars.get('frequency_penalty'),
    presence_penalty=vars.get('presence_penalty'),
    stop=["\n"]
  )

  print('response:', response)

  response_text = response.choices[0].text
  if response_text:
    await channel.send(response_text)

async def admin_message(channel, msg):
  await channel.send(f'*admin*: {msg}')

client.run(discord_config['bot_token'])
