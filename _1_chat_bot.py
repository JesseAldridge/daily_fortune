import os, json, glob, random, textwrap

import openai

import _0_discord


class Personality:
  def __init__(self, name):
    self.name = name

    with open(os.path.join('personalities', f'{name}.txt')) as f:
      self.prompt_lines = f.read().strip().splitlines()

    with open(os.path.join('personalities', f'{name}.json')) as f:
      self.params = json.loads(f.read())

class ChatBot:
  def __init__(self, channel, client):
    self.channel = channel
    self.client = client

    with open(os.path.expanduser('~/open_ai.json')) as f:
      openai.api_key = json.loads(f.read()).get('api_key')

    self.personality = None
    self.recent_messages = []

    self.params = {
      'chime_in_rate': 1,
      'temperature': 0.9,
      'frequency_penalty': 0.2,
      'presence_penalty': 0.6,
      'change_personality_rate': 0.1,
      'max_tokens': 200,
      'top_p': 1,
      'stop': ["\n"],
    }

    unmodifiable_params = ('max_tokens', 'stop')
    self.modifiable_params = [k for k in self.params.keys() if k not in unmodifiable_params]

    self.name_to_personality = {}
    for path in glob.glob(os.path.join('personalities', '*.txt')):
      with open(path) as f:
        name = os.path.splitext(os.path.basename(path))[0]
        self.name_to_personality[name] = Personality(name)

    self.set_random_personality()

  def set_personality(self, name):
    self.personality = personality = self.name_to_personality.get(name)
    if not personality:
      return None
    self.recent_messages = personality.prompt_lines
    self.params.update(personality.params)
    print('set personality to:', name)
    return personality

  def set_random_personality(self):
    personality_names = list(self.name_to_personality.keys())
    print('personality_names:', personality_names)
    new_name = random.choice(personality_names)
    self.set_personality(new_name)

  async def on_message(self, message):
    msg_str = message.content
    print('on message:', msg_str)

    author = str(message.author)
    if 'daily fortune#' in author:
      author = self.get_bot_name()

    if not msg_str.startswith(',') and not msg_str.startswith('*admin*:'):
      if msg_str.startswith('$ ') and len(msg_str) > 2:
        msg_str = msg_str[2:]
      self.recent_messages.append(f'{author}: {msg_str}')
      self.recent_messages = self.recent_messages[-20:]

    if message.author == self.client.user:
      return

    if msg_str == ',debug':
      await self.debug_dump()
    elif msg_str == ',help':
      await self.admin_message(textwrap.dedent(f'''
        ```
        ,debug
        ,set name <name>
        ,set <variable> <value>
        variables: {list(self.modifiable_params)}
        ```
      '''))
    elif msg_str.startswith(',set name'):
      bot_name = msg_str.split()[-1]
      is_found = self.set_personality(bot_name) is not None
      await self.admin_message(f'set bot name to {bot_name}; personality found: {is_found}')
    elif msg_str.startswith(',set '):
      await self.set_variable(msg_str)
    elif self.should_chime_in(msg_str):
      print('chiming in...')
      await self.chime_in()
      if random.random() < self.params['change_personality_rate']:
        self.set_random_personality()

  def should_chime_in(self, msg_str):
    if msg_str.strip().endswith('?'):
      return True
    if msg_str.strip().startswith('$ '):
      return True
    return random.random() < self.params['chime_in_rate']

  async def set_variable(self, msg_str):
    var, val_str = msg_str.split(',set ', 1)[1].rsplit(' ', 1)
    var = '_'.join(var.split())

    if var not in self.modifiable_params:
      await self.admin_message(f'invalid variable: {var}')
      return

    try:
      val = float(val_str)
    except ValueError:
      await self.admin_message(f'invalid value (should be a number between 0 and 1)')
    if not(val >= 0 and val <= 1):
      await self.admin_message(f'invalid value (should be a number between 0 and 1)')
      return
    if var not in self.params:
      await self.admin_message(f'unrecognized variable name')
      return

    self.params[var] = val
    await self.admin_message(f'set {var} to {val}')

  async def chime_in(self):
    prompt = '\n'.join(self.recent_messages) + f'\n{self.get_bot_name()}:'
    print('prompt:', prompt)

    response = openai.Completion.create(
      engine="davinci",
      prompt=prompt,
      temperature=self.params['temperature'],
      max_tokens=self.params['max_tokens'],
      top_p=self.params['top_p'],
      frequency_penalty=self.params['frequency_penalty'],
      presence_penalty=self.params['presence_penalty'],
      stop=self.params['stop'],
    )

    print('response:', response)

    response_text = response.choices[0].text
    if response_text:
      await self.channel.send(response_text)

  def get_bot_name(self):
    return self.personality.name if self.personality else 'Jane#8278'

  async def debug_dump(self):
    params_str = json.dumps(self.params, indent=2)
    await self.admin_message(f'```bot_name: {self.get_bot_name()}\n{params_str}```')

  async def admin_message(self, msg):
    await self.channel.send(f'*admin*: {msg}')

def main():
  _0_discord.main(ChatBot)

if __name__ == '__main__':
  main()
