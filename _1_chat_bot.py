import os, json, glob, random, textwrap

import openai

import _0_discord


class Personality:
  def __init__(self, name):
    self.name = name

    with open(os.path.join('personalities', f'{name}.txt')) as f:
      self.personality_lines = f.read().strip().splitlines()
    self.recent_messages = list(self.personality_lines)

    with open(os.path.join('personalities', f'{name}.json')) as f:
      self.params = json.loads(f.read())

  async def get_response(self):
    prompt = '\n'.join(self.recent_messages) + f'\n{self.name}:'
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

    return response.choices[0].text

class ChatBot:
  async def init(self, channel, client):
    self.channel = channel
    self.client = client
    self.throttle_count = 20
    self.last_personality_name = None

    with open(os.path.expanduser('~/open_ai.json')) as f:
      openai.api_key = json.loads(f.read()).get('api_key')

    self.personality = None
    self.recent_messages = []

    self.name_to_personality = {}
    for path in glob.glob(os.path.join('personalities', '*.txt')):
      with open(path) as f:
        name = os.path.splitext(os.path.basename(path))[0]
        self.name_to_personality[name] = Personality(name)

    await self.admin_message('bot launched')

  async def on_message(self, message):
    msg_str = message.content
    print('on message:', msg_str)
    print('message author:', message.author)

    author = str(message.author).rsplit('#', 1)[0]
    if '**: ' in msg_str:
      author, msg_str = (s.strip() for s in msg_str.split('**: ', 1))
      author = author.split('**', 1)[1]
      self.throttle_count -= 1

    personalities = list(self.name_to_personality.values())

    self.recent_messages.append(f'{author}: {msg_str}')
    self.recent_messages = self.recent_messages[-100:]
    for personality in personalities:
      personality.recent_messages = (personality.personality_lines + self.recent_messages)[:-30]

    if self.throttle_count <= 0:
      return

    personality = self.name_to_personality[random.choice(('penguin', 'cranky', 'navy_seal'))]
    response_str = await personality.get_response()
    if response_str:
      await self.channel.send(f'**{personality.name}**: {response_str}')

  async def admin_message(self, msg):
    await self.channel.send(f'*admin*: {msg}')

def main():
  _0_discord.main(ChatBot)

if __name__ == '__main__':
  main()
