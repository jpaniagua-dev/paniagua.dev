/**
 * Fail if any scroll-animated element never becomes visible.
 *
 *   node tools/anim-check.mjs
 *
 * Scroll-driven animations declared with `animation-fill-mode: both` hold
 * their `from` state until the element enters its range. Get the range wrong
 * and the element stays at opacity 0 forever: the page looks fine in the
 * editor, and a section is simply missing in the browser.
 *
 * This walks the page, brings each animated element to the middle of the
 * viewport, and asserts it actually reaches full opacity. It is the automated
 * version of the mistake that shipped a blank hero once already.
 */
import { chromium } from 'playwright';

const URL = process.argv[2] ?? 'http://127.0.0.1:8787/';
const ANIMATED = ['.rise', '.settle-type', '.row-in', '.word-in', '.swell', '.parallax', '.draw'];

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
await page.goto(URL, { waitUntil: 'networkidle' });
await page.waitForTimeout(600);

const handles = await page.$$(ANIMATED.join(', '));
console.log(`${handles.length} élément(s) animé(s) trouvé(s)`);

const failures = [];

for (const [index, handle] of handles.entries()) {
  await handle.evaluate((el) => el.scrollIntoView({ block: 'center', behavior: 'instant' }));
  await page.waitForTimeout(90);

  const state = await handle.evaluate((el) => {
    const anims = el.getAnimations();
    return {
      opacity: parseFloat(getComputedStyle(el).opacity),
      // The check that matters. An element with no running animation looks
      // identical to a finished one, which is exactly how a page that never
      // animated once passed review.
      running: anims.length,
      scrollDriven: anims.filter((a) => a.timeline && a.timeline !== document.timeline).length,
      tag: el.tagName.toLowerCase(),
      cls: (el.className || '').toString().split(' ').slice(0, 2).join('.'),
      text: (el.textContent || '').trim().slice(0, 36),
    };
  });

  if (state.scrollDriven === 0) {
    failures.push(`#${index} ${state.tag}.${state.cls} AUCUNE animation liée au défilement "${state.text}"`);
  } else if (!(state.opacity > 0.9)) {
    failures.push(`#${index} ${state.tag}.${state.cls} reste à opacity=${state.opacity} "${state.text}"`);
  }
}

if (failures.length) {
  console.log(`\n${failures.length} élément(s) restent invisibles au centre du viewport :`);
  for (const line of failures) console.log(`  ${line}`);
} else {
  console.log('Tous sont pilotés par le défilement et atteignent leur état final.');
}

// The marquee must still travel: a scroll-driven loop that never moves is a
// dead element rather than a restrained one.
await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
await page.waitForTimeout(150);
const before = await page.$eval('.marquee', (el) => el.getBoundingClientRect().left);
await page.evaluate(() => window.scrollTo({ top: document.body.scrollHeight, behavior: 'instant' }));
await page.waitForTimeout(250);
const after = await page.$eval('.marquee', (el) => el.getBoundingClientRect().left);
const travelled = Math.round(before - after);
console.log(`\nBandeau : ${travelled}px parcourus entre le haut et le bas de la page`);
if (travelled < 50) failures.push('marquee did not move');

await browser.close();
process.exit(failures.length ? 1 : 0);
