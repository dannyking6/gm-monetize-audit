const fs = require('fs');
const src = fs.readFileSync('sdk.js','utf8');
const declEnd = src.indexOf('];') + 2;
const decl = src.slice(0, declEnd);
// rename the var to arr so it's visible
const renamed = decl.replace(/^var\s+_\$_[0-9a-f]+/, 'var arr');
eval(renamed);
fs.writeFileSync('strings.json', JSON.stringify(arr));
console.log('strings:', arr.length);
