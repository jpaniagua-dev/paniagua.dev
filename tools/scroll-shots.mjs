import { chromium } from 'playwright';
import { mkdirSync } from 'node:fs';

const [url, name, outDir] = process.argv.slice(2);
mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});
await page.waitForTimeout(3500);

const height = await page.evaluate(() => document.body.scrollHeight);
console.log(`${name}: hauteur ${height}px`);

const stops = [0, 0.12, 0.26, 0.42, 0.62, 0.8];
for (const [i, ratio] of stops.entries()) {
  await page.evaluate((y) => window.scrollTo({ top: y, behavior: 'instant' }), Math.round(height * ratio));
  await page.waitForTimeout(700);
  await page.screenshot({ path: `${outDir}/${name}-${i}.png` });
}
await browser.close();
