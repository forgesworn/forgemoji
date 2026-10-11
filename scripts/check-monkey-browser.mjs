// Focused browser evidence for the compact component-authored Monkey.
import { chromium } from 'playwright';
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
const root = new URL('../', import.meta.url);
const out = new URL('review/vectors/monkey-compact/', root);
const browser = await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
const evidence={browser:'Installed Google Chrome',sizes:[32,64,192,512,1024],errors:[],renders:[],compactionMaximumChannelError:0};
try {
 const page=await browser.newPage({viewport:{width:1200,height:1200},deviceScaleFactor:1});
 page.on('pageerror',e=>evidence.errors.push(e.message));
 const svg=await readFile(new URL('svg/monkey.svg',root),'utf8');
 const raw=await readFile(new URL('unoptimised.svg',out),'utf8');
 for(const size of evidence.sizes) {
  const result=await page.evaluate(async ({svg,raw,size})=>{
   const render=async text=>{const im=new Image();im.src='data:image/svg+xml;base64,'+btoa(text);await im.decode();const c=document.createElement('canvas');c.width=c.height=size;c.getContext('2d').drawImage(im,0,0,size,size);return c.getContext('2d').getImageData(0,0,size,size).data};
   const a=await render(svg),b=await render(raw);let max=0,visible=0;
   for(let i=0;i<a.length;i++){max=Math.max(max,Math.abs(a[i]-b[i]));if(i%4===3&&a[i]>32)visible++;}
   const pixel=(x,y)=>Array.from(a.slice((Math.round(y*size/192)*size+Math.round(x*size/192))*4,(Math.round(y*size/192)*size+Math.round(x*size/192))*4+4));
   return {size,visible,max,leftEar:pixel(16,101),rightEar:pixel(174,101),skin:pixel(96,91)};
  },{svg,raw,size});
  assert(result.visible>size*size*.1);assert(result.skin[0]>220);assert(result.leftEar[0]>150);assert(result.rightEar[0]>150);
  evidence.renders.push(result);evidence.compactionMaximumChannelError=Math.max(evidence.compactionMaximumChannelError,result.max);
 }
 await page.goto(new URL('comparison.html',out).href);
 await page.screenshot({path:fileURLToPath(new URL('chrome-comparison.png',out)),fullPage:true});
 for(const bg of ['#fff','#18212b']) {
  await page.setContent(`<body style="margin:0;background:${bg}"><img width="512" height="512" src="data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}"></body>`);
  await page.locator('img').screenshot({path:fileURLToPath(new URL(bg==='#fff'?'chrome-light.png':'chrome-dark.png',out))});
 }
 assert.deepEqual(evidence.errors,[]);
 await writeFile(new URL('chrome-checks.json',out),JSON.stringify(evidence,null,2)+'\n');
 console.log(JSON.stringify(evidence));
} finally { await browser.close(); }
