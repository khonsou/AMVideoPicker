const fs = require('fs');
const path = require('path');
const sharp = require('sharp');
const assets = path.join(__dirname,'report_assets');
async function main(){
  for(const file of fs.readdirSync(assets).filter(x=>x.endsWith('.svg'))){
    const src=path.join(assets,file);
    const dst=path.join(assets,file.replace(/\.svg$/,'.png'));
    await sharp(src,{density:120}).png({compressionLevel:9}).toFile(dst);
    console.log(path.basename(dst));
  }
}
main().catch(err=>{console.error(err);process.exit(1);});
