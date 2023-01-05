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
        'Fun fact about the stock market',
        'Fun fact about summarization',
        'Fun fact about web scraping',
        'Fun fact about cognition',
        'Fun fact about information management',
        'Fun fact about computer science',
        'Fun fact about information',
        'Fun fact about learning',
        'Fun fact about psychology',
        'Fun fact about data',
        'Fun fact about machine learning',
        'Fun fact about wikipedia',
        'Fun fact about twitter',
      ])

      if random.random() < .5:
        prompt = f'{base_prompt}:'
      else:
        prompt = f'{base_prompt} (utterly deranged and untrue):'

      response = openai.Completion.create(
        engine="text-davinci-003",
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
    fortune_loop.start()

def main():
  _0_discord.main(ChatBot)

if __name__ == '__main__':
  main()
