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
      if random.random() < .5:
        prompt = 'Fun fact about mushrooms (silly and untrue):'
      else:
        prompt = 'Fun fact about mushrooms:'

      response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=self.params['temperature'],
        max_tokens=self.params['max_tokens'],
        top_p=self.params['top_p'],
        frequency_penalty=self.params['frequency_penalty'],
        presence_penalty=self.params['presence_penalty'],
      )

      print('response:', response)

      message = response.choices[0].text.strip() or ''
      await self.channel.send(message)
    fortune_loop.start()

def main():
  _0_discord.main(ChatBot)

if __name__ == '__main__':
  main()
