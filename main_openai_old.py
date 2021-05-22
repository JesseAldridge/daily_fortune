import os, json, random, glob, textwrap

import discord, openai


class Personality:
  def __init__(self, name):
    self.name = name

    with open(os.path.join('personalities', f'{name}.txt')) as f:
      self.prompt_lines = f.read().strip().splitlines()

    with open(os.path.join('personalities', f'{name}.json')) as f:
      self.params = json.loads(f.read())

class ChatBot:
  def __init__(self):
    with open(os.path.expanduser('~/open_ai.json')) as f:
      openai.api_key = json.loads(f.read()).get('api_key')

    self.personality = None
    self.recent_messages = []

    self.params = {
      'chime_in_rate': 0.4,
      'temperature': 0.9,
      'frequency_penalty': 0.2,
      'presence_penalty': 0.6,
      'change_personality_rate': 0.1,
    }

    self.name_to_personality = {}
    for path in glob.glob(os.path.join('personalities', '*.txt')):
      with open(path) as f:
        name = os.path.splitext(os.path.basename(path))[0]
        self.name_to_personality[name] = Personality(name)

  def randomize(self, channel):
    for key in vars.keys():
      if key == 'change_personality_rate':
        continue
      vars[key] = random.random()
    set_random_personality()

  def set_personality(self, bot_name):
    self.personality = personality = self.name_to_personality.get(bot_name)
    if not personality:
      return None
    self.recent_messages = personality.prompt_lines
    self.params.update(personality.params)
    print('set personality to:', self.bot_name)
    return personality

  def set_random_personality(self):
    new_name = random.choice(list(self.name_to_personality.keys()))
    self.set_personality(new_name)

def launch_discord_client():
  with open(os.path.expanduser('~/discord.json')) as f:
    discord_config = json.loads(f.read())

  client = discord.Client()
  client.run(discord_config['bot_token'])

@client.event
async def on_ready(*a, **kw):
  print('on ready:', a, kw)
  for guild in client.guilds:
    print('guild:', guild)
    for channel in guild.channels:
      print('channel:', channel)
      if hasattr(channel, 'send'):
        await chatbot.set_random_personality(channel)
        await admin_message(channel, 'bot launched')
        await debug_dump(channel)

async def debug_dump(channel):
  await admin_message(channel, f'```bot_name: {g.bot_name}\n{json.dumps(vars, indent=2)}```')

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
      ,randomize
      ,set name <name>
      ,set <variable> <value>
      variables: {list(vars.keys())}
      ```
    '''))
  elif message.content == ',reset':
    set_personality(g.bot_name)
    await admin_message_(f'bot reset')
  elif message.content == ',debug':
    await debug_dump(message.channel)
  elif message.content == ',randomize':
    await randomize(message.channel)
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
      if random.random() < vars.get('randomize_rate'):
        await randomize(message.channel)
      await chime_in(message.channel, message)

async def set_variable(message):
  async def admin_message_(msg_str):
    await admin_message(message.channel, msg_str)

  var, val_str = message.content.split(',set ', 1)[1].rsplit(' ', 1)
  var = '_'.join(var.split())
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
