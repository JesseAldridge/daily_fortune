const fs = require('fs');
const ChildProcess = require('child_process');

const expand_home_dir = require('expand-home-dir')
const Discord = require('discord.js');
const chardet = require('chardet');
const iconv = require('iconv');

const config_path = expand_home_dir('~/discord.json')
const config = JSON.parse(fs.readFileSync(config_path))


const client = new Discord.Client();

function send_message_loop() {
  client.guilds.cache.forEach((guild) => {
    const channel = guild.channels.cache.find(ch => ch.name === 'general');
    // Do nothing if the channel wasn't found on this server
    if (!channel)
      return;

    const result = ChildProcess.spawnSync('fortune', []);
    const raw_buffer = result.output[1];
    const encoding = chardet.detect(raw_buffer);
    const converter = new iconv.Iconv(encoding, 'UTF-8');
    const utf8_buffer = converter.convert(raw_buffer);
    channel.send('```\n' + utf8_buffer + '\n```');
  })

  setTimeout(send_message_loop, 1000 * 60 * 60 * 24);
}

client.on('ready', () => {
  console.log(`Logged in as ${client.user.tag}!`);
  send_message_loop();
});

client.login(config.bot_token);
