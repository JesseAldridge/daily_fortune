const fs = require('fs');

const chardet = require('chardet');
const Iconv = require('iconv').Iconv;

function readFileSyncGuessEncoding(path) {
  const encoding = chardet.detectFileSync(path)
  const content = fs.readFileSync(path);
  const iconv = new Iconv(encoding, 'UTF-8');
  const buffer = iconv.convert(content);
  return buffer.toString('utf8');
}

readFileSyncGuessEncoding('/usr/share/games/fortune/hitchhiker')
