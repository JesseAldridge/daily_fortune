import os, json, glob, random, textwrap, threading, asyncio, subprocess

import openai, chardet
from discord.ext import tasks

import _0_discord

def openai_call(request_string):
  errors = (openai.error.RateLimitError, openai.error.ServiceUnavailableError,
            openai.error.APIError, openai.error.Timeout, ConnectionResetError)
  delay = 1

  for i in range(10):
    try:
      completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{
          "role": "user",
          "content": request_string
        }]
      )

      return completion['choices'][0]['message']['content']

    except errors as e:
      print(f"Error: {e}")
      print(f"Waiting for {delay} seconds before retrying...")
      time.sleep(delay)

      delay *= 2

  raise Exception("Failed to get a response from ChatGPT after 10 attempts.")


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

      response = openai_call(prompt)

      print('response:', response)

      message = f"{base_prompt}:\n\n{response.strip() or ''}"
      await self.channel.send(message)
    fortune_loop.start()

def main():
  _0_discord.main(ChatBot)

if __name__ == '__main__':
  main()
