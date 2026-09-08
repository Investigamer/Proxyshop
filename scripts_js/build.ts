import { readdir, readFile, rename, rm, writeFile } from "fs/promises";
// import { format, parse } from "path";

const distPath = "dist_js/";
const awaitInjectionLocator = /\sphotoshop_[0-9]+.core.executeAsModal\(/g;

// TypeScript doesn't allow top level await when transpiling to CommonJS,
// but that is the combination we need with UXP scripts, so we have to
// add the awaits after tsc transpilation.
async function fixUXPScript(path: string) {
  const content = await readFile(path, "utf-8");
  const matches = content.match(awaitInjectionLocator);
  if (matches) {
    const lastIndex = content.lastIndexOf(matches[matches.length - 1]);
    await writeFile(
      path,
      content.slice(0, lastIndex) + " await" + content.slice(lastIndex),
    );
  }
  // await rename(path, format({ ...parse(path), base: "", ext: ".psjs" }));
}

async function build() {
  const operations: Promise<unknown>[] = [];

  for (let pth of await readdir(distPath)) {
    pth = distPath + pth;
    if (pth.endsWith(".psjs")) operations.push(rm(pth));
    else if (pth.endsWith(".js")) operations.push(fixUXPScript(pth));
  }

  await Promise.all(operations);
}

await build();
