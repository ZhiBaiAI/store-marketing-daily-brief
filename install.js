#!/usr/bin/env node

const fs = require("fs");
const os = require("os");
const path = require("path");

const skillName = "store-marketing-daily-brief";
const sourceDir = __dirname;
const args = new Set(process.argv.slice(2));
const force = args.has("--force") || args.has("-f");

function defaultSkillsRoot() {
  const codexHome = process.env.CODEX_HOME || path.join(os.homedir(), ".codex");
  return path.join(codexHome, "skills");
}

function parseDestRoot() {
  const argv = process.argv.slice(2);
  const destIndex = argv.indexOf("--dest");
  if (destIndex >= 0 && argv[destIndex + 1]) {
    return path.resolve(argv[destIndex + 1]);
  }
  return defaultSkillsRoot();
}

function shouldSkip(name) {
  return new Set([".git", "node_modules", "package-lock.json"]).has(name);
}

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    if (shouldSkip(entry.name)) continue;
    const srcPath = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else if (entry.isFile()) {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

const skillsRoot = parseDestRoot();
const targetDir = path.join(skillsRoot, skillName);

if (fs.existsSync(targetDir)) {
  if (!force) {
    console.error(`Skill already exists: ${targetDir}`);
    console.error("Run again with --force to replace it.");
    process.exit(1);
  }
  fs.rmSync(targetDir, { recursive: true, force: true });
}

fs.mkdirSync(skillsRoot, { recursive: true });
copyDir(sourceDir, targetDir);

console.log(`Installed ${skillName} to ${targetDir}`);
console.log("Restart your agent app to pick up the new skill.");
