import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const baseUrl = "https://viggomeesters.com";
const errors = [];

function read(file) {
  return fs.readFileSync(path.join(root, file), "utf8");
}

function exists(file) {
  return fs.existsSync(path.join(root, file));
}

function walk(dir, predicate, files = []) {
  for (const name of fs.readdirSync(path.join(root, dir))) {
    if (name === ".git" || name === ".vercel" || name === "node_modules") continue;
    const rel = path.join(dir, name);
    const stat = fs.statSync(path.join(root, rel));
    if (stat.isDirectory()) walk(rel, predicate, files);
    else if (predicate(rel)) files.push(rel);
  }
  return files;
}

function routeForIndex(file) {
  if (file === "index.html") return "/";
  return `/${path.dirname(file).replaceAll(path.sep, "/")}/`;
}

function canonicalForRoute(route) {
  return `${baseUrl}${route}`;
}

function assert(condition, message) {
  if (!condition) errors.push(message);
}

const htmlFiles = walk(".", (file) => file.endsWith(".html")).map((file) =>
  file.replace(/^\.\//, ""),
);
const publicPages = htmlFiles
  .filter((file) => file === "index.html" || file.endsWith("/index.html"))
  .sort();
const variantPages = htmlFiles.filter((file) => /^variant-.*\.html$/.test(file)).sort();

for (const file of htmlFiles) {
  const html = read(file);
  for (const match of html.matchAll(/\b(?:href|src)=["']([^"']+)["']/g)) {
    const raw = match[1];
    if (/^(https?:|mailto:|data:|#)/.test(raw)) continue;

    const clean = raw.split("#")[0].split("?")[0];
    if (!clean) continue;

    const target = clean.startsWith("/")
      ? path.join(root, clean)
      : path.join(root, path.dirname(file), clean);
    const ok =
      fs.existsSync(target) ||
      fs.existsSync(path.join(target, "index.html")) ||
      fs.existsSync(`${target}.html`);

    assert(ok, `${file}: broken local reference ${raw}`);
  }
}

for (const file of publicPages) {
  const route = routeForIndex(file);
  const expected = canonicalForRoute(route);
  const html = read(file);
  assert(
    html.includes(`<link rel="canonical" href="${expected}">`),
    `${file}: missing canonical ${expected}`,
  );
}

const sitemap = read("sitemap.xml");
const sitemapLocs = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((match) => match[1]);
const expectedLocs = publicPages.map((file) => canonicalForRoute(routeForIndex(file)));

for (const loc of expectedLocs) {
  assert(sitemapLocs.includes(loc), `sitemap.xml: missing ${loc}`);
}

for (const loc of sitemapLocs) {
  assert(expectedLocs.includes(loc), `sitemap.xml: unexpected ${loc}`);
}

for (const file of variantPages) {
  const loc = `${baseUrl}/${file}`;
  const cleanLoc = loc.replace(/\.html$/, "");
  assert(!sitemapLocs.includes(loc), `sitemap.xml: variant page should not be indexed ${loc}`);
  assert(!sitemapLocs.includes(cleanLoc), `sitemap.xml: variant page should not be indexed ${cleanLoc}`);
}

const robots = read("robots.txt");
assert(robots.includes("Sitemap: https://viggomeesters.com/sitemap.xml"), "robots.txt: missing sitemap");
assert(robots.includes("Disallow: /variant-"), "robots.txt: variants are not disallowed");

const vercel = JSON.parse(read("vercel.json"));
assert(vercel.cleanUrls === true, "vercel.json: cleanUrls must be true");
assert(Array.isArray(vercel.redirects), "vercel.json: redirects must be configured");
for (const host of ["www.viggomeesters.com", "viggomeesters.nl", "www.viggomeesters.nl"]) {
  assert(
    vercel.redirects.some(
      (redirect) =>
        redirect.destination === "https://viggomeesters.com/:path*" &&
        redirect.has?.some(
          (condition) =>
            condition.type === "host" &&
            condition.value === host,
        ),
    ),
    `vercel.json: missing redirect from ${host} to viggomeesters.com`,
  );
}
assert(
  vercel.headers?.some(
    (entry) =>
      entry.source === "/variant-:path(.*)" &&
      entry.headers?.some((header) => header.key === "X-Robots-Tag" && header.value.includes("noindex")),
  ),
  "vercel.json: variants need X-Robots-Tag noindex",
);
assert(exists("og-image.png"), "missing og-image.png");
assert(exists("profile.jpg"), "missing profile.jpg");

if (errors.length > 0) {
  console.error(`Site check failed with ${errors.length} issue(s):`);
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}

console.log(`Site check passed: ${publicPages.length} public pages, ${variantPages.length} variants checked.`);
