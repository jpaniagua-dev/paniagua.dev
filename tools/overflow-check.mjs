import { chromium } from 'playwright';
const base = process.argv[2] ?? 'http://127.0.0.1:8787';
const ROUTES = ['/', '/fr/'];
const b = await chromium.launch();
let failures = 0;
for (const route of ROUTES)
for (const w of [390, 768, 1024, 1440, 1920]) {
  const p = await b.newPage({ viewport: { width: w, height: 900 } });
  await p.goto(base + route, { waitUntil: 'networkidle' });
  await p.waitForTimeout(800);
  const res = await p.evaluate((vw) => {
    const clipped = (el) => {
      for (let n = el.parentElement; n; n = n.parentElement) {
        const o = getComputedStyle(n);
        if (o.overflowX === 'hidden' || o.overflowX === 'clip') return true;
      }
      return false;
    };
    const out = [];
    for (const el of document.querySelectorAll('body *')) {
      const r = el.getBoundingClientRect();
      if (r.width === 0 || clipped(el)) continue;
      if (r.right > vw + 1 || r.left < -1) {
        out.push(`${el.tagName.toLowerCase()}.${(el.className||'').toString().split(' ')[0]} [${Math.round(r.left)}..${Math.round(r.right)}]`);
      }
    }
    return { out: out.slice(0, 5), scroll: document.documentElement.scrollWidth };
  }, w);
  const ok = res.out.length === 0 && res.scroll <= w + 1;
  if (!ok) failures++;
  console.log(`${route.padEnd(5)} ${String(w).padStart(4)}px : ${ok ? 'aucun débordement' : res.out.join(' | ') + ` (scrollWidth ${res.scroll})`}`);
  await p.close();
}
await b.close();
process.exit(failures ? 1 : 0);
