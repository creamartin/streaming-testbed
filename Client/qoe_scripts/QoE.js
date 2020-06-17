const puppeteer = require('puppeteer-core');
const mkdirp = require('mkdirp');
const fs = require('fs');
const getDirName = require('path').dirname;
const chalk = require('chalk');
const program = require('commander');
/***********************************************************/
const DATA_PATH = '../data/qoe'
const host = 'caddy-testbed.com',
host2 = 'litespeed.testbed.com';
const path = '/dash_client.html';
const urls =
{
  'CADDY_HTTP_OVER_QUIC':'https://'+host+':443'+path,
  'CADDY_HTTP2':'https://'+host+':444'+path,
  'CADDY_HTTP1_1_NO_SSL':'http://'+host+':8080'+path,
  'CADDY_HTTP1_1':'https://'+host+':445'+path
};

program
.option('-c, --cycles <cycles>', 'Number of runs')
.option('-p, --probes <probes>', 'Number of probes per run')
.option('-i, --interval <interval>', 'Interval at which to collect probes')
.option('-s, --strategy <strategy>', '0 = Dynamic, 1 = Throughput, 2 = Bola')
.option('-n, --network <network>', 'e.g. "3G" - string and valid filename')
.parse(process.argv);

const CYCLES = program.cycles ? parseInt(program.cycles) : 10,
PROBES = program.probes ? parseInt(program.probes) : 100,
INTERVAL = program.interval ? parseInt(program.interval) : 1000,
NETWORK = program.network ? program.network.replace(/[^a-z0-9]/gi, '_') : "undefined",
GRACE = 10000; // ms between runs
let   STRATEGY;
let _strategy = program.strategy ? parseInt(program.strategy) : 0
if(_strategy == 1)
STRATEGY = "abrThroughput";
else if (_strategy == 2)
STRATEGY = "abrBola";
else
STRATEGY = "abrDynamic";


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
    //'--quic-host-whitelist=caddy-testbed.com:443 caddy-testbed.com:443',
    //'--origin-to-force-quic-on=caddy-testbed.com:443',
     '--disk-cache-size=1',
     '--media-cache-size=1'
  ]
};

/***********************************************************/

//STARTING POINT
(async function () {
  for (const [scheme, url] of Object.entries(urls)) {
    for (let i = 1; i <= CYCLES; i++) {
      log(chalk.black.inverse('Running test on '+ scheme +', cycle ' + i + '/' + CYCLES));
      const result = await run(i, scheme, url);
      const delay = d => new Promise(r => setTimeout(r, d));
      await delay(GRACE);
    }
  }
}
());

async function run(runIndex,scheme,url) {
  let stallEvents,
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

await page.goto(url+"?abrStrategy="+STRATEGY);
const delay = d => new Promise(r => setTimeout(r, d));
async function timer(i = 0) {

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
//availableBandwidths.push(availableBandwidth);
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
  let path = DATA_PATH + '/' + STRATEGY + '/'+ NETWORK + '/' + scheme;
  let json = {};
  json["connectionTime"] = connectionTime;
  json["startUpTime"] = startUpTime;
  json["stallEvents"] = stallEvents;
  stallDurations = stallDurations ? stallDurations.trim().split(" ") : "0" ;
  json["stallDurations"] = stallDurations;
  json["qualityChanges"] = qualityChanges.trim() || "0";
  json["bufferLevels"] = bufferLevels;
  //json["availableBandwidths"] = availableBandwidths;
  json["reportedBitrates"] = reportedBitrates;
  json["calculatedBitrates"] = calculatedBitrates;
  json["liveLatencies"] = liveLatencies;

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
