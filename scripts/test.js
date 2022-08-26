const puppeteer = require('puppeteer');

const USERNAME = process.env.SPOTIFY_USERNAME;
const PASSWORD = process.env.SPOTIFY_PASSWORD;


(async () => {
  const browser = await puppeteer.launch({});

  console.log("visit the home page");
  const page = await browser.newPage({});
  await page.goto("https://spotify-word.cloud", {
    waitUntil: 'networkidle2'
  });

  console.log("login");
  await page.click('a[href="/login"]');
  await page.waitForTimeout(10000);

  console.log("type in the credentials");
  await page.type('input[id="login-username"]', USERNAME);
  await page.type('input[id="login-password"]', PASSWORD);

  await page.click('button[id="login-button"]');
  await page.waitForTimeout(10000);

  console.log("visit the history page"); 
  await page.goto("https://spotify-word.cloud/history", {
    waitUntil: 'networkidle2'
  });

  await browser.close();
})();