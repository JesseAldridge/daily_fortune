import os, json, glob, random, textwrap, threading, asyncio, subprocess

import openai, chardet
from discord.ext import tasks

import _0_discord


class ChatBot:
  async def init(self, channel, client):
    self.channel = channel
    self.client = client

    with open(os.path.expanduser('~/open_ai.json')) as f:
      openai.api_key = json.loads(f.read()).get('api_key')

    @tasks.loop(seconds=60 * 60 * 24)
    async def fortune_loop():
      base_prompt = random.choice([
        'Fun fact',
        'Fun fact about the stock market',
        'Fun historical fact',
        'Fun fact about mushrooms',
        'Fun fact about the human body',
        'Fun fact about the universe',
      ])

      if random.random() < .5:
        prompt = f'{base_prompt}:'
      else:
        prompt = f'{base_prompt} (utterly deranged and untrue):'

      response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=1,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
      )

      print('response:', response)

      message = f"{base_prompt}:\n\n{response.choices[0].text.strip() or ''}"
      await self.channel.send(message)
      await self.channel.send(f'/imagine {message}')
    fortune_loop.start()

def main():
  _0_discord.main(ChatBot)

if __name__ == '__main__':
  main()
