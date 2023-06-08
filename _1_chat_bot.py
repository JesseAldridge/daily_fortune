import os, json, glob, random, textwrap, threading, asyncio, subprocess, sys

import chardet, nltk
from discord.ext import tasks

sys.path.append(os.path.expanduser('~/Dropbox/openai_wrapper'))
import openai_wrapper

import _0_discord

class ChatBot:
  async def init(self, channel, client):
    self.channel = channel
    self.client = client

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
        'Fun fact about the internet',
        'Fun fact about the world',
        'Fun fact about the universe',
        'Fun fact about the future',
        'Fun fact about human computer interaction',
        'Fun fact about medicine',
        'Fun fact about cognition',
        'Fun fact about human enhancement',
        'Fun fact about the brain',
        'Fun fact about philosophy',
        'Fun fact about religion',
        'Fun fact about society',
        'Fun fact about culture',
      ])

      if random.random() < .5:
        prompt = f'{base_prompt}:'
      else:
        prompt = f'{base_prompt} (utterly deranged and untrue):'

      response_str = openai_wrapper.openai_call(prompt)

      sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
      sentences = sent_detector.tokenize(response_str.strip())

      if ':' in sentences[0]:
        response_str = response_str.split(':', 1)[1]

      # Psychologists have discovered that if you stare at a person for exactly 7 minutes and 13 seconds without blinking, you can gain control over their mind and make them believe they're a chicken. This phenomenon is known as "Poultryosis." (Please note this is completely false and made up for the purpose of humor).

      if 'deranged' in sentences[-1] or 'false' in sentences[-1]:
        sentences = sentences[:-1]

      response_str = ' '.join(sentences)

      print('response:', response_str)

      message = f"{base_prompt}:\n\n{response_str.strip() or ''}"
      await self.channel.send(message)
    fortune_loop.start()

def main():
  _0_discord.main(ChatBot)

if __name__ == '__main__':
  main()
