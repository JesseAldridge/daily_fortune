import os, json

import openai


with open('personalities/penguin.txt') as f:
  lines = f.read().splitlines()

with open(os.path.expanduser('~/open_ai.json')) as f:
  openai.api_key = json.loads(f.read()).get('api_key')

lines.append('Jesse#123: hello')
lines.append('penguin: ')

response = openai.Completion.create(
  engine="davinci",
  prompt='\n'.join(lines),
  temperature=0.9,
  max_tokens=200,
  top_p=1,
  frequency_penalty=0.5,
  presence_penalty=0.6,
  stop=["\n"]
)

print('response:', response)
