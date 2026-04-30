/**
 * preview.js
 * Opens case-study HTML pages across multiple device sizes in headed Chromium.
 *
 * Usage:
 *   node preview.js                                          — all case-study-*.html × 5 devices
 *   node preview.js --file unified-data-management-with-graphql.html
 *   node preview.js --device mobile                         — all files at 390px only
 */

const { chromium } = require('playwright');
const path = require('path');
const fs   = require('fs');

const DIR = __dirname;

const DEVICES = [
  { label: 'Desktop (1440)',  width: 1440, height: 900  },
  { label: 'Laptop  (1024)',  width: 1024, height: 768  },
  { label: 'Tablet   (768)',  width: 768,  height: 1024 },
  { label: 'Mobile   (390)',  width: 390,  height: 844  },
  { label: 'Small    (360)',  width: 360,  height: 780  },
];

const args       = process.argv.slice(2);
const fileArg    = args.indexOf('--file');
const devArg     = args.indexOf('--device');
const fileFilter = fileArg !== -1 ? args[fileArg + 1] : null;
const devFilter  = devArg  !== -1 ? args[devArg  + 1] : null;

const files = fs
  .readdirSync(DIR)
  .filter(f => f.endsWith('.html'))
  .filter(f => fileFilter ? f === fileFilter : f.startsWith('case-study-'))
  .sort();

const devices = DEVICES.filter(d =>
  !devFilter || d.label.toLowerCase().includes(devFilter.toLowerCase())
);

if (files.length === 0) {
  console.error('No matching HTML files found in', DIR);
  process.exit(1);
}

(async () => {
  const browser = await chromium.launch({
    headless: false,
    args: ['--disable-web-security'],   // allows local file:// cross-origin access
  });

  let tabCount  = 0;
  let firstPage = null;

  for (const file of files) {
    const url = 'file:///' + path.join(DIR, file).replace(/\\/g, '/');

    for (const device of devices) {
      const ctx  = await browser.newContext({
        viewport:         { width: device.width, height: device.height },
        bypassCSP:        true,
      });
      const page = await ctx.newPage();

      try {
        // domcontentloaded is reliable for local HTML files; 'load' can abort
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });
        await page.evaluate(
          ([label, fname]) => { document.title = `${label} — ${fname}`; },
          [device.label, file]
        );
      } catch (err) {
        console.warn(`  ⚠  Could not load ${file} at ${device.label}: ${err.message}`);
      }

      tabCount++;
      if (!firstPage) firstPage = page;
      console.log(`  [${tabCount}] ${device.label}  |  ${file}`);
    }
  }

  if (firstPage) {
    try { await firstPage.bringToFront(); } catch (_) {}
  }

  console.log(`\n✓ ${tabCount} tab(s) open. Close the browser when done.\n`);
  console.log('Tips:');
  console.log('  node preview.js --file unified-data-management-with-graphql.html');
  console.log('  node preview.js --device mobile');
  console.log('  node preview.js              (all case-study pages)\n');

  browser.on('disconnected', () => process.exit(0));
})();
