// One-off dev script: rasterizes the SVG brand mark into the PWA icon set.
// Run with: node scripts/generate-icons.mjs
import { mkdir, readFile } from "node:fs/promises"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"
import sharp from "sharp"

const __dirname = dirname(fileURLToPath(import.meta.url))
const outDir = join(__dirname, "..", "public", "icons")

async function main() {
  await mkdir(outDir, { recursive: true })

  const standard = await readFile(join(__dirname, "icon-source.svg"))
  const maskable = await readFile(join(__dirname, "icon-source-maskable.svg"))

  const targets = [
    { src: standard, size: 192, name: "icon-192.png" },
    { src: standard, size: 512, name: "icon-512.png" },
    { src: standard, size: 180, name: "apple-touch-icon.png" },
    { src: maskable, size: 192, name: "maskable-192.png" },
    { src: maskable, size: 512, name: "maskable-512.png" },
  ]

  for (const target of targets) {
    await sharp(target.src, { density: 384 })
      .resize(target.size, target.size)
      .png()
      .toFile(join(outDir, target.name))
    console.log(`wrote ${target.name}`)
  }

  await sharp(standard, { density: 384 })
    .resize(32, 32)
    .png()
    .toFile(join(__dirname, "..", "public", "favicon.png"))
  console.log("wrote favicon.png")
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
