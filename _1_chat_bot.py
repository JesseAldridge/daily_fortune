import os, json, glob, random, textwrap, threading, asyncio, subprocess, sys

import chardet, nltk
from discord.ext import tasks

sys.path.append(os.path.expanduser('~/Dropbox/openai_wrapper'))
import openai_wrapper

import _0_discord


with open('words.txt') as f:
  words = f.read().strip().splitlines()

class ChatBot:
  async def init(self, channel, client):
    self.channel = channel
    self.client = client

    @tasks.loop(seconds=60 * 60 * 24)
    async def fortune_loop():
      prompt = (
        f'Fun fact about a random, esoteric topic, inspired by the word "{random.choice(words)}". ' +
        "User 20 words or fewer."
      )

      response_str = openai_wrapper.openai_call(prompt)

      print('response:', response_str)
      if 'test' not in sys.argv:
        await self.channel.send(response_str)
    fortune_loop.start()

def main():
  _0_discord.main(ChatBot)

if __name__ == '__main__':
  main()
