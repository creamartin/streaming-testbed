const puppeteer = require('puppeteer-core');
const mkdirp = require('mkdirp');
const fs = require('fs');
const chalk = require('chalk');
const program = require('commander');
const shell = require('shelljs')
/***********************************************************/
const bandwidth_shaper = require("./adaptation_performance.json");
const host = 'caddy-testbed.com';
const path = '/dash_client.html';
const urls =
{
  'CADDY_HTTP1_1_NO_SSL':'http://'+host+':8080'+path,
  'CADDY_HTTP1_1':'https://'+host+':445'+path,
  'CADDY_HTTP2':'https://'+host+':444'+path,
  'CADDY_HTTP_OVER_QUIC':'https://'+host+':443'+path
};

const STRATEGIES = ["abrDynamic","abrThroughput","abrBola"];
let STRATEGY;
program
.option('-c, --cycles <cycles>', 'Number of runs')
.option('-p, --probes <probes>', 'Number of probes per run')
.option('-i, --interval <interval>', 'Interval at which to collect probes')
.option('-t, --timeout <timeout>', 'timeout for connection to stop in milliseconds')
.parse(process.argv);

const CYCLES = program.cycles ? parseInt(program.cycles) : 10,
PROBES = program.probes ? parseInt(program.probes) : 100,
INTERVAL = program.interval ? parseInt(program.interval) : 1000,
TIMEOUT = program.timeout ? parseInt(program.timeout) : 10000;

const browserConfig = {
  executablePath: '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome',
  headless: false,
  defaultViewport: { //--window-size in args
    width: 1280,
    height: 882
  },
  args: [
    '--user-data-dir=/tmp/chrome',
    '--no-proxy-server',
    '--enable-quic',
    '--quic-host-whitelist=caddy-testbed.com:443 caddy-testbed.com:443',
    '--origin-to-force-quic-on=caddy-testbed.com:443',
     '--disk-cache-size=1',
     '--media-cache-size=1'
  ]
};
/***********************************************************/
//STARTING POINT
(async function () {
    for(let n = 0; n < STRATEGIES.length; n++)
    {
      STRATEGY = STRATEGIES[n];
      for (const [scheme, url] of Object.entries(urls)) {
        for (let i = 1; i <= CYCLES; i++) {
          log(chalk.black.inverse('Running test on '+ scheme +'cycle ' + i + '/' + CYCLES));
          const result = await run(i, scheme, url);
          const delay = d => new Promise(r => setTimeout(r, d));
          await delay(TIMEOUT);
        }
      }
    }
}
());

async function run(runIndex,scheme,url) {
  let availableBandwidth,latency = 0;
  let bandwidthShaper = JSON.parse(JSON.stringify(bandwidth_shaper));
  let stallEvents = [],
  bufferEmptyEvents = [],
  bufferLevels = [],
  availableBandwidths = [],
  calculatedBitrates = [],
  reportedBitrates = [],
  liveLatencies = [],
  startUpTime = "-1",
  connectionTime = "-1",
  qualityChanges,
  stallDuration;

  const browser = await puppeteer.launch(browserConfig);
  const page = await browser.newPage();
  // NETWORK
  const client = await page.target().createCDPSession();
  await client.send('Network.enable');
  async function setBandwidth(download) {

  if (shell.exec('./apply_network.sh ' + download).code !== 0) {
    shell.echo('Error: Git commit failed');
    shell.exit(1);
  }
    /*
    await client.send('Network.emulateNetworkConditions', {
    offline: false,
    latency: latency,
    downloadThroughput: download * 1024 / 8, // kb/s
    uploadThroughput: download * 1024 / 8
  });
  */
  availableBandwidth = download;
}

//setBandwidth(bandwidthShaper[0].kBits);
await page.goto(url+"?abrStrategy="+STRATEGY);
const delay = d => new Promise(r => setTimeout(r, d));
async function timer(i = 0) {
  //bandwith-shaping
  if (bandwidthShaper.length && i * INTERVAL / 1000 >= bandwidthShaper[0].time) {
    console.log("bandwidth@"+ bandwidthShaper[0].kBits +"Kbits/");
    await setBandwidth(bandwidthShaper[0].kBits);
    bandwidthShaper.shift();
}
const stalEl = await page.$("#bufferEmpty")
const stallEvent = await (await stalEl.getProperty('textContent')).jsonValue();
stallEvents = stallEvent;
const bufEl = await page.$("#bufferLevel");
const bufferLevel = await (await bufEl.getProperty('textContent')).jsonValue();
const repEl = await page.$("#reportedBitrate");
const reportedBitrate = await (await repEl.getProperty('textContent')).jsonValue();
const calEl = await page.$("#calculatedBitrate");
const calculatedBitrate = await (await calEl.getProperty('textContent')).jsonValue();
const livEl = await page.$("#liveLatency");
const liveLatency = await (await livEl.getProperty('textContent')).jsonValue();
const staEl = await page.$("#startUpTime");
const startUp = await (await staEl.getProperty('textContent')).jsonValue();
startUpTime = startUp || -1;
const conEl = await page.$("#connectionTime");
const connectStart = await (await conEl.getProperty('textContent')).jsonValue();
connectionTime = connectStart || -1;
const stalDur = await page.$("#bufferEmptyEvents")
const sDs = await (await stalDur.getProperty('textContent')).jsonValue();
stallDurations= sDs || null;
const qChanges = await page.$("#qualityChanges")
const qCs = await (await qChanges.getProperty('textContent')).jsonValue();
qualityChanges = qCs;

bufferLevels.push(bufferLevel || "0");
availableBandwidths.push(availableBandwidth);
reportedBitrates.push(reportedBitrate.trim() || "0");
calculatedBitrates.push(calculatedBitrate || "0");
liveLatencies.push(liveLatency || "0");
if (i >= PROBES) {
  return;
}
await delay(INTERVAL)
return timer(i + 1)
}

await timer().then(() => {
  let path = './data/'+ STRATEGY  + '/' + scheme;
  let json = {};
  json["connectionTime"] = connectionTime;
  json["startUpTime"] = startUpTime;
  json["stallEvents"] = stallEvents;
  //stallDurations = stallDurations ? stallDurations.trim().split(" ") : "0" ;
  //json["stallDurations"] = stallDurations;
  //json["qualityChanges"] = qualityChanges.trim() || "0";
  json["bufferLevels"] = bufferLevels;
  json["availableBandwidths"] = availableBandwidths;
  json["reportedBitrates"] = reportedBitrates;
  json["calculatedBitrates"] = calculatedBitrates;
  //json["liveLatencies"] = liveLatencies;

  try {
    fs.promises.mkdir(path, {recursive: true})
    .then(x => fs.promises.writeFile(path+'/run_' + runIndex + '.json', JSON.stringify(json, null, 4)))
    .then(log(chalk.bold.green('✓\n')));
  } catch (err) {
    log(chalk.bold.red('✗\n'))
    console.log(err.message)
  }
  browser.close();
});
}

function log(string) {
  process.stderr.write(string);
}
