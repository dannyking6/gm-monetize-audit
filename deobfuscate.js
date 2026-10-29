const fs = require('fs');
const src = fs.readFileSync('sdk.js','utf8');
const arr = JSON.parse(fs.readFileSync('strings.json','utf8'));
const m = src.match(/^var\s+(_\$_[0-9a-f]+)/);
const name = m[1].replace(/\$/g, '\\$');
let out = src.replace(new RegExp(name + '\\[(\\d+)\\]', 'g'), (_, i) => JSON.stringify(arr[+i]));
out = out.replace(/^var\s+_\$[0-9a-f]+\s*=\s*\[.*?\];\n?/s, '// [string table removed]\n');
fs.writeFileSync('sdk.deobf.js', out);
console.log('ok, opphbh present:', out.includes('opphbh'));
