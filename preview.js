/**
 * preview.js
 * Opens all case-study pages across 4 device sizes in a headed Chromium browser.
 * Each tab = one page at a specific viewport so you can review responsiveness.
 *
 * Usage:   node preview.js
 * Options: node preview.js --file case-study-2-publish.html   (single file)
 *          node preview.js --device mobile                     (mobile only)
 */

const { chromium } = require('playwright');
const path = require('path');
const fs   = require('fs');

const DIR = __dirname;

const DEVICES = [
  { label: 'Desktop  (1440)',  width: 1440, height: 900  },
  { label: 'Laptop   (1024)',  width: 1024, height: 768  },
  { label: 'Tablet   (768)',   width: 768,  height: 1024 },
  { label: 'Mobile   (390)',   width: 390,  height: 844  },
  { label: 'Small    (360)',   width: 360,  height: 780  },
];

// Parse --file and --device flags
const args     = process.argv.slice(2);
const fileArg  = args.indexOf('--file');
const devArg   = args.indexOf('--device');
const fileFilter = fileArg  !== -1 ? args[fileArg  + 1] : null;
const devFilter  = devArg   !== -1 ? args[devArg   + 1] : null;

const files = fs
  .readdirSync(DIR)
  .filter(f => f.startsWith('case-study-') && f.endsWith('.html'))
  .filter(f => !fileFilter || f === fileFilter)
  .sort();

const devices = DEVICES.filter(d =>
  !devFilter || d.label.toLowerCase().includes(devFilter.toLowerCase())
);

if (files.length === 0) {
  console.error('No matching HTML files found.');
  process.exit(1);
}

(async () => {
  const browser = await chromium.launch({ headless: false });

  let tabCount = 0;
  let firstPage = null;

  for (const file of files) {
    const url = 'file:///' + path.join(DIR, file).replace(/\\/g, '/');

    for (const device of devices) {
      const ctx  = await browser.newContext({ viewport: { width: device.width, height: device.height } });
      const page = await ctx.newPage();
      await page.goto(url);
      // Set tab title
      await page.evaluate(
        ([label, fname]) => { document.title = `${label} — ${fname}`; },
        [device.label, file]
      );
      tabCount++;
      if (!firstPage) firstPage = page;
      console.log(`  [${tabCount}] ${device.label}  |  ${file}`);
    }
  }

  if (firstPage) await firstPage.bringToFront();

  console.log(`\n✓ ${tabCount} tab(s) open. Close the browser when done.\n`);
  console.log('TIP: Use  node preview.js --file case-study-2-publish.html  to preview one file.');
  console.log('     Use  node preview.js --device mobile                   to show mobile only.\n');

  browser.on('disconnected', () => process.exit(0));
})();
