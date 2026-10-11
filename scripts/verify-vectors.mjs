import { chromium } from 'playwright';
import { readFile, writeFile, mkdir, mkdtemp, rm } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { inflateSync } from 'node:zlib';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
const root = new URL('../', import.meta.url);
const manifest = JSON.parse(await readFile(new URL('manifest.json', root), 'utf8'));
const review = new URL('review/vectors/', root);
await mkdir(review, { recursive: true });
const temporary = await mkdtemp(join(tmpdir(), 'forgemoji-vector-check-'));
const evidence = { rendered: [], renderedSizes: [32,192,512], pageErrors: [], externalRequests: [], categoryCounts: {}, handTones: [], mirroredMaterialChecks: [], browser: 'Installed Google Chrome', mobileWidth: 390 };
function rgbaPng(data) {
  const width = data.readUInt32BE(16), height = data.readUInt32BE(20);
  assert.equal(data[24], 8); assert.equal(data[25], 6, 'RGBA rasterisation');
  const chunks=[];
  for(let offset=8;offset<data.length;) { const length=data.readUInt32BE(offset),kind=data.subarray(offset+4,offset+8).toString();if(kind==='IDAT')chunks.push(data.subarray(offset+8,offset+8+length));offset+=length+12; }
  const packed=inflateSync(Buffer.concat(chunks)),stride=width*4,pixels=Buffer.alloc(height*stride);
  const paeth=(a,b,c)=>{const p=a+b-c,pa=Math.abs(p-a),pb=Math.abs(p-b),pc=Math.abs(p-c);return pa<=pb&&pa<=pc?a:pb<=pc?b:c};
  for(let y=0;y<height;y++)for(let x=0;x<stride;x++) {
    const index=y*stride+x,filter=packed[y*(stride+1)],a=x>=4?pixels[index-4]:0,b=y?pixels[index-stride]:0,c=y&&x>=4?pixels[index-stride-4]:0;
    pixels[index]=(packed[y*(stride+1)+1+x]+[0,a,b,Math.floor((a+b)/2),paeth(a,b,c)][filter])&255;
  }
  return {width,height,pixels};
}
try {
  for (const art of manifest.vectorArtwork) {
    const output=join(temporary,`${art.slug}.png`);
    execFileSync('rsvg-convert',['--width','192','--height','192','--output',output,fileURLToPath(new URL(art.file,root))]);
    const {width,height,pixels}=rgbaPng(await readFile(output));
    assert.equal(width,192);assert.equal(height,192);
    let visible=0;
    for(let y=0;y<192;y++)for(let x=0;x<192;x++) {
      const alpha=pixels[(y*192+x)*4+3];if(alpha>32)visible++;
      if(x<8||x>=184||y<8||y>=184)assert.equal(alpha,0,`${art.slug}: transparent padding`);
    }
    assert(visible>1000,`${art.slug}: readable nonempty artwork`);
    const holes={'key':[149,40],'doughnut':[96,96]};
    if(holes[art.slug]) {
      const [x,y]=holes[art.slug];assert.equal(pixels[(y*192+x)*4+3],0,`${art.slug}: opening must remain transparent`);
    }
    for(const size of [32,512]) {
      execFileSync('rsvg-convert',['--width',String(size),'--height',String(size),'--output',output,fileURLToPath(new URL(art.file,root))]);
      const render=rgbaPng(await readFile(output));assert.equal(render.width,size);assert.equal(render.height,size);
      let opaque=0;
      for(let i=3;i<render.pixels.length;i+=4)if(render.pixels[i]>32)opaque++;
      assert(opaque>size*size*.02,`${art.slug}: empty at ${size}px`);
    }
    evidence.rendered.push({slug:art.slug,visiblePixels:visible});
  }
  console.log(`Rendered and checked ${evidence.rendered.length} SVGs with librsvg.`);
  const browser=await chromium.launch({executablePath:process.env.FORGEMOJI_CHROME||'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
  try {
    const page=await browser.newPage({viewport:{width:1440,height:1100},deviceScaleFactor:1});
    // Chrome and librsvg differ on diffuse lighting in reflected groups.
    // Check actual painted pixels; successful image decoding misses a black
    // material surface. Data URLs let the canvas inspect our local SVG safely.
    for(const base of ['thumbs-down','thanks'])for(let tone=0;tone<=5;tone++) {
      const slug=base+(tone?`-tone${tone}`:'');
      const data=(await readFile(new URL(`svg/${slug}.svg`,root))).toString('base64');
      const pixels=await page.evaluate(async ({base,data})=>{
        const image=new Image();image.src='data:image/svg+xml;base64,'+data;await image.decode();
        const canvas=document.createElement('canvas');canvas.width=canvas.height=192;
        const context=canvas.getContext('2d');context.drawImage(image,0,0,192,192);
        const points=base==='thanks'?[[79,95],[113,95]]:[[95,70],[129,78]];
        return points.map(([x,y])=>[...context.getImageData(x,y,1,1).data]);
      },{base,data});
      for(const [red,green,blue,alpha] of pixels){assert(alpha>245,`${slug}: material coverage`);assert(red>35,`${slug}: mirrored skin must retain its colour`)}
      evidence.mirroredMaterialChecks.push({slug,pixels});
    }
    page.on('pageerror',e=>evidence.pageErrors.push(e.message));
    page.on('request',r=>{if(/^https?:/.test(r.url()))evidence.externalRequests.push(r.url())});
    const decode=()=>page.evaluate(()=>Promise.all([...document.querySelectorAll('main img')].map(img=>{img.loading='eager';return img.decode()})));
    await page.goto(new URL('vector-review.html',root).href);
    assert.equal(await page.locator('.tile').count(),163);
    await decode();
    await page.locator('#view').click();
    for(const category of [...new Set(manifest.definitions.map(d=>d.category))]) {
      await page.selectOption('#category',category);
      await decode();
      evidence.categoryCounts[category]=await page.locator('.tile').count();
      await page.screenshot({path:fileURLToPath(new URL(`${category.toLowerCase()}.png`,review)),fullPage:true});
    }
    await page.selectOption('#category','Hands');
    for(let tone=0;tone<=5;tone++) {
      await page.selectOption('#tone',String(tone));await decode();
      assert.equal(await page.locator('.tile').count(),6);
      evidence.handTones.push(tone);
    }
    await page.selectOption('#category','');await page.selectOption('#tone','0');
    await page.locator('#search').fill('Happy');
    await page.locator('[data-slug="happy"] .inspect').click();
    await page.locator('#detail-svg').evaluate(img=>img.decode());
    for(const opacity of ['0','50','100']) {await page.locator('#blend').fill(opacity);assert.equal(await page.locator('#overlay-svg').evaluate(img=>Number(img.style.opacity)),Number(opacity)/100)}
    await page.locator('#inspect .close').click();
    await page.selectOption('#tone','all');
    for(const name of ['jumping-spider','sacred-stone','fs-forgesworn','star-eyes','thinking','fox','thumbs-up-tone5','shocked','mask','bandage','panda','rainbow','beer','apple','burger','doughnut','cookie','popcorn','cheers','key','rocket','camera','celebrate','peace-tone1','clap','tiger','lion','cow','chicken','monkey','duck','whale','octopus','turtle','bee','rose','star','banana','strawberry','watermelon','lemon','avocado','fries','pizza','cake','coffee','ice-cream','gamepad','football','trophy']) {
      await page.locator('#search').fill('');await page.selectOption('#category','');
      await page.locator(`[data-slug="${name}"] .inspect`).click();
      await page.locator('#detail-svg').evaluate(img=>img.decode());
      await page.locator('#inspect').screenshot({path:fileURLToPath(new URL(`${name}-detail.png`,review))});
      await page.locator('#inspect .close').click();
    }
    await page.locator('#search').fill('');await page.selectOption('#category','Nature');await page.selectOption('#tone','0');
    await page.locator('#theme').click();await decode();
    await page.screenshot({path:fileURLToPath(new URL('nature-light.png',review)),fullPage:true});
    await page.goto(new URL('index.html',root).href);
    assert.equal(await page.locator('#format').inputValue(),'svg');
    assert.equal(await page.locator('.tile').count(),133);
    await page.selectOption('#tone','3');await page.getByRole('button',{name:'Thumbs up',exact:true}).click();
    assert.equal(await page.locator('#unicode').textContent(),'👍🏽');
    assert.match(await page.locator('#selected').getAttribute('src'),/^svg\/thumbs-up-tone3\.svg\?v=[a-f0-9]{12}$/);
    await page.selectOption('#format','png');
    assert.match(await page.locator('#selected').getAttribute('src'),/^png\/thumbs-up-tone3\.png\?v=[a-f0-9]{12}$/);
    await page.selectOption('#format','svg');
    for(const width of [1440,390]) {
      await page.setViewportSize({width,height:844});
      for(const size of ['32','64','256','512']) {
        await page.selectOption('#size',size);
        assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Picker must fit');
      }
    }
    await page.goto(new URL('vector-review.html',root).href);
    await page.locator('#view').click();
    for(const theme of ['dark','light']) {
      if(theme==='light')await page.locator('#theme').click();
      for(const size of ['32','64']) {
        await page.selectOption('#size',size);await decode();
        await page.screenshot({path:fileURLToPath(new URL(`all-${size}-${theme}.png`,review)),fullPage:true});
      }
    }
    await page.locator('#view').click();
    await page.locator('#search').fill('fox');
    for(const size of ['32','128','512','1024']) {
      await page.selectOption('#size',size);await decode();
      assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Comparison must fit mobile');
    }
    await page.locator('[data-slug="fox"] .inspect').click();
    await page.screenshot({path:fileURLToPath(new URL('mobile-inspect.png',review)),fullPage:true});
    assert(await page.locator('#inspect').evaluate(dialog=>dialog.scrollWidth<=dialog.clientWidth),'Dialog must fit mobile');
    assert.deepEqual(evidence.pageErrors,[]);assert.deepEqual(evidence.externalRequests,[]);
  } finally {await browser.close()}
  await writeFile(new URL('checks.json',review),JSON.stringify(evidence,null,2)+'\n');
  console.log('Verified all browser images, categories, six hand tones, overlay controls, PNG/SVG switching and mobile layouts. No page errors or external requests.');
} finally {await rm(temporary,{recursive:true,force:true})}
