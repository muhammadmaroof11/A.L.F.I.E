/**
 * Update all source code references from old image extensions to .webp
 * Also updates logo.png -> logo.webp
 */
import { readFile, writeFile } from 'fs/promises';
import { join } from 'path';

const SRC_ROOT = 'e:/Me/A.L.F.I.E/alfie_website/src';

// Files that were converted from their original format to .webp
const replacements = [
  // Logo
  ['/logo.png', '/logo.webp'],
  
  // Clinics
  ['clinic_female.jpg', 'clinic_female.webp'],
  ['clinic_male.jpg', 'clinic_male.webp'],
  ['niche_clinic_consult.jpeg', 'niche_clinic_consult.webp'],
  
  // Car Rental  
  ['carrental_female.jpg', 'carrental_female.webp'],
  ['carrental_male.jpg', 'carrental_male.webp'],
  ['niche_fleet_vip.jpeg', 'niche_fleet_vip.webp'],
  
  // Hospitality
  ['hospitality_female.jpg', 'hospitality_female.webp'],
  ['hospitality_male.jpg', 'hospitality_male.webp'],
  ['niche_hospitality_dining.jpeg', 'niche_hospitality_dining.webp'],
  
  // Law Firms
  ['law_female.jpg', 'law_female.webp'],
  ['law_male.jpg', 'law_male.webp'],
  ['niche_legal_detail.jpeg', 'niche_legal_detail.webp'],
  
  // Real Estate
  ['niche_realestate_luxury.jpeg', 'niche_realestate_luxury.webp'],
  ['realestate_female.jpg', 'realestate_female.webp'],
  ['realestate_male.jpg', 'realestate_male.webp'],
];

import { readdir, stat } from 'fs/promises';

async function findJSXFiles(dir) {
  const results = [];
  const entries = await readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...await findJSXFiles(full));
    } else if (entry.name.endsWith('.jsx') || entry.name.endsWith('.js') || entry.name.endsWith('.css')) {
      results.push(full);
    }
  }
  return results;
}

async function main() {
  const files = await findJSXFiles(SRC_ROOT);
  
  // Also check index.html
  files.push('e:/Me/A.L.F.I.E/alfie_website/index.html');
  
  console.log(`Scanning ${files.length} source files for image reference updates...\n`);
  
  let totalReplacements = 0;
  
  for (const filePath of files) {
    let content;
    try {
      content = await readFile(filePath, 'utf-8');
    } catch { continue; }
    
    let modified = content;
    let fileReplacements = 0;
    
    for (const [from, to] of replacements) {
      const count = (modified.split(from).length - 1);
      if (count > 0) {
        modified = modified.replaceAll(from, to);
        fileReplacements += count;
      }
    }
    
    if (fileReplacements > 0) {
      await writeFile(filePath, modified, 'utf-8');
      const shortPath = filePath.replace(/.*alfie_website[/\\]/, '');
      console.log(`  ✅ ${shortPath}: ${fileReplacements} reference(s) updated`);
      totalReplacements += fileReplacements;
    }
  }
  
  console.log(`\n🎯 Total: ${totalReplacements} image references updated across all source files.`);
}

main().catch(console.error);
