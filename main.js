const fs = require('fs');
const ChildProcess = require('child_process');

const expand_home_dir = require('expand-home-dir')
const Discord = require('discord.js');
const chardet = require('chardet');
const iconv = require('iconv');

const config_path = expand_home_dir('~/discord.json')
const config = JSON.parse(fs.readFileSync(config_path))


const client = new Discord.Client();

client.on('ready', () => {
  console.log(`Logged in as ${client.user.tag}!`);
  send_message_loop();
});


client.on('message', msg => {
  response = openai.Completion.create(
    engine="davinci",
    prompt=msg.content,
    temperature=0.9,
    max_tokens=150,
    top_p=1,
    frequency_penalty=0.0,
    presence_penalty=0.6,
    // stop=["\n", " Human:", " AI:"]
  )
});


client.login(config.bot_token);
