// usage: node render.mjs <fromFrame> <toFrame> <outDir>   (frames at 30fps, toFrame exclusive)
// local install first (Mac), then the cloud container's global copy
const { chromium } = await import('playwright').catch(() => import('/opt/node-tools/node_modules/playwright/index.mjs'));
import fs from 'node:fs';
import path from 'node:path';

const dir = path.dirname(new URL(import.meta.url).pathname);
const [from, to, out] = [+process.argv[2], +process.argv[3], process.argv[4]];
fs.mkdirSync(out, { recursive: true });
const TL = fs.readFileSync(path.join(dir, 'timeline.json'), 'utf8');

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
await page.addInitScript(`window.TL = ${TL};`);
await page.goto('file://' + path.join(dir, 'index.html'));
await page.evaluate(() => document.fonts.ready);
for (let f = from; f < to; f++) {
  await page.evaluate(t => window.renderAt(t), f / 30);
  await page.screenshot({ path: path.join(out, `f${String(f).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 94 });
}
await browser.close();
