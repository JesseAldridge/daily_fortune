var Iconv = require('iconv').Iconv;
var fs = require('fs');

function readFileSyncGuessEncoding(path) {
  const encoding = chardet.detectFileSync(path)
  var content = fs.readFileSync(path);
  var iconv = new Iconv(encoding, 'UTF-8');
  var buffer = iconv.convert(content);
  return buffer.toString('utf8');
}

readFileSyncGuessEncoding('/usr/share/games/fortune/hitchhiker')
