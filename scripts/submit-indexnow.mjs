import https from "node:https";
import fs from "node:fs";

const host = "viggomeesters.com";
const keyFile = "indexnow-key.txt";
const key = fs.readFileSync(new URL(`../${keyFile}`, import.meta.url), "utf8").trim();
const keyLocation = `https://${host}/${keyFile}`;
const sitemap = fs.readFileSync(new URL("../sitemap.xml", import.meta.url), "utf8");
const urls = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((match) => match[1]);

const payload = JSON.stringify({
  host,
  key,
  keyLocation,
  urlList: urls,
});

const request = https.request({
  hostname: "api.indexnow.org",
  path: "/indexnow",
  method: "POST",
  headers: {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(payload),
  },
}, (response) => {
  let body = "";
  response.setEncoding("utf8");
  response.on("data", (chunk) => body += chunk);
  response.on("end", () => {
    console.log(JSON.stringify({
      statusCode: response.statusCode,
      urlCount: urls.length,
      keyLocation,
      response: body.trim(),
    }, null, 2));
    if (![200, 202].includes(response.statusCode)) process.exit(1);
  });
});

request.on("error", (error) => {
  console.error(error);
  process.exit(1);
});

request.write(payload);
request.end();
