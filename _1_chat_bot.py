import os, json, glob, random

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
    print('on message:', message.content)

    author = self.personality.name if 'daily fortune#' in str(message.author) else message.author

    if not message.content.startswith(',') and not message.content.startswith('*admin*:'):
      self.recent_messages.append(f'{author}: {message.content}')
      self.recent_messages = self.recent_messages[-20:]

    if message.author == self.client.user:
      return

    if message.content == ',debug':
      await debug_dump(message.channel)
    elif message.content.startswith(',set name'):
      bot_name = message.content.split()[-1]
      is_found = self.set_personality(bot_name) is not None
      await self.admin_message(f'set bot name to {bot_name}; personality found: {is_found}')
      if not is_found:
        self.bot_name += f'#{int(random.random() * 1000)}'
    elif message.content.startswith(',set '):
      await self.set_variable(message.content)
    elif self.should_chime_in(message.content):
      await self.chime_in(message)
      if random.random() < self.params['change_personality_rate']:
        self.set_random_personality()

  def should_chime_in(self, msg_str):
    if self.personality.name == 'answer' and msg_str.strip().endswith('?'):
      return True
    return random.random() < self.params['chime_in_rate']

  async def set_variable(self, msg_str):
    var, val_str = msg_str.split(',set ', 1)[1].rsplit(' ', 1)
    var = '_'.join(var.split())
    try:
      val = float(val_str)
    except ValueError:
      await self.admin_message(f'invalid value (should be a number between 0 and 1)')
    if not(val >= 0 and val <= 1):
      await self.admin_message(f'invalid value (should be a number between 0 and 1)')
      return
    if var not in vars:
      await self.admin_message(f'unrecognized variable name')
      return

    self.params[var] = val
    await self.admin_message(f'set {var} to {val}')

  async def chime_in(self, message):
    prompt = '\n'.join(self.recent_messages) + f'\n{self.personality.name}:'
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

  async def debug_dump(self):
    name = self.personality.name
    params_str = json.dumps(self.params, indent=2)
    await self.admin_message(f'```bot_name: {name}\n{params_str}```')

  async def admin_message(self, msg):
    await self.channel.send(f'*admin*: {msg}')

def main():
  _0_discord.main(ChatBot)

if __name__ == '__main__':
  main()
