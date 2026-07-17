import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const baseUrl = "https://viggomeesters.com";
const cliArgs = process.argv.slice(2);
const unknownArgs = cliArgs.filter((arg) => arg !== "--update");
if (unknownArgs.length > 0) {
  console.error(`Unknown SEO audit argument(s): ${unknownArgs.join(", ")}`);
  process.exit(2);
}
const updateBaseline = cliArgs.includes("--update");

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
    else if (predicate(rel)) files.push(rel.replace(/^\.\//, ""));
  }
  return files;
}

function routeForIndex(file) {
  if (file === "index.html") return "/";
  return `/${path.dirname(file).replaceAll(path.sep, "/")}/`;
}

function textFromHtml(html) {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&[a-z0-9#]+;/gi, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function attr(html, regex) {
  const match = html.match(regex);
  return match ? match[1].trim() : "";
}

function all(html, regex) {
  return [...html.matchAll(regex)].map((match) => match[1].trim());
}

function isNoindex(html) {
  return [...html.matchAll(/<meta\b[^>]*>/gi)].some(
    ([tag]) => /\bname=["']robots["']/i.test(tag) && /\bcontent=["'][^"']*\bnoindex\b/i.test(tag),
  );
}

function classify(route) {
  if (route === "/") return "homepage";
  if (route === "/guides/" || [
    "/cli-agents-guide/",
    "/database-types-agent-first-systems/",
    "/jsonl-agent-first-data-structures/",
    "/foci-fear-of-choosing-incorrectly/",
  ].includes(route)) return "guides_articles";
  if (route.startsWith("/agent-workflow/") || route === "/agent-workflow-loop/") return "agent_workflow";
  if (route.startsWith("/personal-knowledge-system/") || route === "/agent-brain/" || route === "/raycast-life-os/") return "personal_knowledge_system";
  if (route.startsWith("/tech-stack/") || route === "/uses/") return "tech_stack";
  if (route.startsWith("/skills/")) return "skills_registry";
  if (route.startsWith("/projects/") || [
    "/sap-agent-context/",
    "/mega-vault-viewer/",
    "/obsidian-plugins/",
    "/jsonl-vault-spike/",
    "/vault-layer/",
  ].includes(route)) return "project_pages";
  if (["/beste-kattenvoer/", "/beste-kattenbrokken/"].includes(route)) return "seo_evergreen";
  if (route === "/trendwatch/" || route === "/tech-news/") return "signal_dashboards";
  if ([
    "/methodologies/",
    "/helicopter-to-detail/",
    "/knowledge-pyramid/",
    "/funnel-analysis/",
    "/source-backed-synthesis/",
    "/proof-first-delivery/",
    "/vault-first-operating-model/",
  ].includes(route)) return "methodologies";
  return "other";
}

function sitemapData() {
  const xml = read("sitemap.xml");
  const entries = [...xml.matchAll(/<url>\s*<loc>([^<]+)<\/loc>\s*<lastmod>([^<]+)<\/lastmod>\s*<priority>([^<]+)<\/priority>\s*<\/url>/g)].map((m) => ({
    loc: m[1],
    lastmod: m[2],
    priority: Number(m[3]),
  }));
  return entries;
}

const publicPages = walk(".", (file) => file.endsWith(".html"))
  .filter((file) => file === "index.html" || file.endsWith("/index.html"))
  .sort();
const sitemapEntries = sitemapData();
const sitemapByLoc = new Map(sitemapEntries.map((entry) => [entry.loc, entry]));
const titleMap = new Map();
const descMap = new Map();
const rows = [];
const issues = [];

for (const file of publicPages) {
  const html = read(file);
  const route = routeForIndex(file);
  const url = `${baseUrl}${route}`;
  const title = attr(html, /<title>([\s\S]*?)<\/title>/i);
  const description = attr(html, /<meta\s+name=["']description["']\s+content=["']([\s\S]*?)["']/i);
  const canonical = attr(html, /<link\s+rel=["']canonical["']\s+href=["']([^"']+)["']/i);
  const h1s = all(html, /<h1\b[^>]*>([\s\S]*?)<\/h1>/gi).map((value) => textFromHtml(value));
  const text = textFromHtml(html);
  const words = text ? text.split(/\s+/).length : 0;
  const jsonLdCount = all(html, /<script\s+type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi).length;
  const ogUrl = attr(html, /<meta\s+property=["']og:url["']\s+content=["']([\s\S]*?)["']/i);
  const hasOgTitle = /<meta\s+property=["']og:title["']/i.test(html);
  const hasOgDescription = /<meta\s+property=["']og:description["']/i.test(html);
  const hasOgImage = /<meta\s+property=["']og:image["']/i.test(html);
  const hasTwitterCard = /<meta\s+name=["']twitter:card["']/i.test(html);
  const hasAnalytics = html.includes('/_vercel/insights/script.js');
  const sitemap = sitemapByLoc.get(url);
  const noindex = isNoindex(html);
  const cluster = classify(route);

  if (title) titleMap.set(title, [...(titleMap.get(title) || []), route]);
  if (description) descMap.set(description, [...(descMap.get(description) || []), route]);

  const pageIssues = [];
  if (!title) pageIssues.push("missing_title");
  if (!noindex && title && title.length < 25) pageIssues.push("short_title");
  if (!noindex && title && title.length > 65) pageIssues.push("long_title");
  if (!noindex && !description) pageIssues.push("missing_description");
  if (!noindex && description && description.length < 80) pageIssues.push("short_description");
  if (!noindex && description && description.length > 170) pageIssues.push("long_description");
  if (canonical !== url) pageIssues.push("canonical_mismatch");
  if (h1s.length !== 1) pageIssues.push(`h1_count_${h1s.length}`);
  if (!noindex && words < 250 && !route.startsWith("/skills/")) pageIssues.push("thin_under_250_words");
  if (!noindex && !sitemap) pageIssues.push("missing_sitemap_entry");
  if (noindex && sitemap) pageIssues.push("noindex_in_sitemap");
  if (!hasAnalytics) pageIssues.push("missing_analytics_script");
  if (!noindex && !hasOgTitle) pageIssues.push("missing_og_title");
  if (!noindex && !hasOgDescription) pageIssues.push("missing_og_description");
  if (!noindex && !hasOgImage) pageIssues.push("missing_og_image");
  if (!noindex && ogUrl && ogUrl !== canonical) pageIssues.push("og_url_mismatch");
  if (!noindex && !hasTwitterCard) pageIssues.push("missing_twitter_card");

  rows.push({
    file,
    route,
    cluster,
    url,
    title,
    titleLength: title.length,
    description,
    descriptionLength: description.length,
    h1: h1s[0] || "",
    h1Count: h1s.length,
    words,
    jsonLdCount,
    lastmod: sitemap?.lastmod || "",
    priority: sitemap?.priority ?? null,
    hasOgTitle,
    hasOgDescription,
    hasOgImage,
    hasTwitterCard,
    hasAnalytics,
    noindex,
    issues: pageIssues,
  });

  for (const issue of pageIssues) issues.push({ route, file, cluster, issue });
}

for (const [title, routes] of titleMap.entries()) {
  if (routes.length > 1) for (const route of routes) issues.push({ route, file: rows.find((r) => r.route === route)?.file, cluster: classify(route), issue: "duplicate_title" });
}
for (const [description, routes] of descMap.entries()) {
  if (routes.length > 1) for (const route of routes) issues.push({ route, file: rows.find((r) => r.route === route)?.file, cluster: classify(route), issue: "duplicate_description" });
}

const byCluster = {};
for (const row of rows) {
  byCluster[row.cluster] ??= { pages: 0, issues: 0, thin: 0, missingOgImage: 0, missingJsonLd: 0 };
  byCluster[row.cluster].pages += 1;
  byCluster[row.cluster].issues += row.issues.length;
  if (row.issues.includes("thin_under_250_words")) byCluster[row.cluster].thin += 1;
  if (row.issues.includes("missing_og_image")) byCluster[row.cluster].missingOgImage += 1;
  if (row.jsonLdCount === 0) byCluster[row.cluster].missingJsonLd += 1;
}

const issueCounts = issues.reduce((acc, item) => {
  acc[item.issue] = (acc[item.issue] || 0) + 1;
  return acc;
}, {});

const priorityPages = rows
  .filter((row) => !row.noindex && !row.route.startsWith("/skills/"))
  .map((row) => ({
    route: row.route,
    cluster: row.cluster,
    words: row.words,
    titleLength: row.titleLength,
    descriptionLength: row.descriptionLength,
    jsonLdCount: row.jsonLdCount,
    issues: row.issues,
    score: row.issues.length + (row.words < 250 ? 3 : 0) + (row.jsonLdCount === 0 ? 1 : 0),
  }))
  .sort((a, b) => b.score - a.score || a.route.localeCompare(b.route))
  .slice(0, 40);

const result = {
  generatedAt: "current working tree",
  baseUrl,
  summary: {
    publicPages: publicPages.length,
    sitemapEntries: sitemapEntries.length,
    issueTypes: Object.keys(issueCounts).length,
    totalIssueOccurrences: issues.length,
    clusters: byCluster,
    issueCounts,
  },
  issues,
  priorityPages,
  pages: rows,
};

const topIssues = Object.entries(issueCounts).sort((a, b) => b[1] - a[1]);
const clusterRows = Object.entries(byCluster).sort((a, b) => b[1].issues - a[1].issues);
const md = [
  "# SEO Baseline — viggomeesters.com",
  "",
  `Generated: ${result.generatedAt}`,
  "",
  "## Summary",
  "",
  `- Public pages: ${publicPages.length}`,
  `- Sitemap entries: ${sitemapEntries.length}`,
  `- Issue occurrences: ${issues.length}`,
  "",
  "## Top issue types",
  "",
  "| Issue | Count |",
  "|---|---:|",
  ...topIssues.map(([issue, count]) => `| ${issue} | ${count} |`),
  "",
  "## Clusters",
  "",
  "| Cluster | Pages | Issues | Thin | Missing OG image | Missing JSON-LD |",
  "|---|---:|---:|---:|---:|---:|",
  ...clusterRows.map(([cluster, data]) => `| ${cluster} | ${data.pages} | ${data.issues} | ${data.thin} | ${data.missingOgImage} | ${data.missingJsonLd} |`),
  "",
  "## Priority non-skill pages",
  "",
  "| Route | Cluster | Words | JSON-LD | Issues |",
  "|---|---|---:|---:|---|",
  ...priorityPages.slice(0, 25).map((row) => `| ${row.route} | ${row.cluster} | ${row.words} | ${row.jsonLdCount} | ${row.issues.join(", ")} |`),
  "",
  "## Next loop recommendation",
  "",
  "1. Fix site-wide social metadata/structured-data rules where safe.",
  "2. Start with homepage and Guides/Articles because they shape crawl paths and search snippets.",
  "3. Treat evergreen SEO pages separately with current-source verification before claim changes.",
  "",
].join("\n");

const reportDir = path.join(root, "reports", "seo");
const baselineJson = path.join(reportDir, "baseline.json");
const baselineMarkdown = path.join(reportDir, "baseline.md");

if (updateBaseline) {
  fs.mkdirSync(reportDir, { recursive: true });
  fs.writeFileSync(baselineJson, `${JSON.stringify(result, null, 2)}\n`);
  fs.writeFileSync(baselineMarkdown, md);
  console.log(`SEO baseline updated: ${publicPages.length} pages, ${issues.length} issue occurrences.`);
  console.log("Wrote reports/seo/baseline.json and reports/seo/baseline.md");
  process.exit(0);
}

if (!fs.existsSync(baselineJson)) {
  console.error("SEO check failed: reports/seo/baseline.json is missing; run npm run check:seo:update after review.");
  process.exit(1);
}

let baseline;
try {
  baseline = JSON.parse(fs.readFileSync(baselineJson, "utf8"));
} catch {
  console.error("SEO check failed: reports/seo/baseline.json is invalid JSON.");
  process.exit(1);
}

const issueKey = (item) => `${item.route}\t${item.issue}`;
const baselineIssues = Array.isArray(baseline.issues)
  ? baseline.issues
  : (baseline.pages || []).flatMap((page) =>
      (page.issues || []).map((issue) => ({ route: page.route, issue })),
    );
const allowedIssueKeys = new Set(baselineIssues.map(issueKey));
const regressions = issues.filter((item) => !allowedIssueKeys.has(issueKey(item)));

if (regressions.length > 0) {
  console.error(`SEO check failed with ${regressions.length} new issue(s):`);
  for (const item of regressions) console.error(`- ${item.route}: ${item.issue}`);
  console.error("Fix the regressions, or review and run npm run check:seo:update intentionally.");
  process.exit(1);
}

console.log(
  `SEO check passed: ${publicPages.length} pages, ${issues.length} known issue occurrence(s), 0 regressions.`,
);
