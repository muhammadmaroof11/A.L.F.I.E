/**
 * Retry compression for the 7 locked webp files
 * Writes compressed versions alongside originals with _opt suffix,
 * then swaps them.
 */
import sharp from 'sharp';
import { stat, mkdir, copyFile, unlink, rename } from 'fs/promises';
import { join, dirname, basename } from 'path';

const BACKUP_DIR = 'e:/Me/A.L.F.I.E/alfie_website/_asset_backups';

const files = [
  { path: 'e:/Me/A.L.F.I.E/alfie_website/public/assets/industry_photos/car_rental/chauffer.webp', width: 1200, quality: 75 },
  { path: 'e:/Me/A.L.F.I.E/alfie_website/public/assets/industry_photos/car_rental/driver-service.webp', width: 1920, quality: 75 },
  { path: 'e:/Me/A.L.F.I.E/alfie_website/public/assets/industry_photos/car_rental/rental_car.webp', width: 1920, quality: 75 },
  { path: 'e:/Me/A.L.F.I.E/alfie_website/public/assets/industry_photos/clinics/doctor.webp', width: 800, quality: 78 },
  { path: 'e:/Me/A.L.F.I.E/alfie_website/public/assets/industry_photos/clinics/doctor2.webp', width: 800, quality: 78 },
  { path: 'e:/Me/A.L.F.I.E/alfie_website/public/assets/industry_photos/law_firms/law.webp', width: 1920, quality: 75 },
  { path: 'e:/Me/A.L.F.I.E/alfie_website/public/assets/industry_photos/law_firms/law2.webp', width: 1920, quality: 75 },
];

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)}MB`;
}

async function processFile({ path, width, quality }) {
  const name = basename(path);
  const dir = dirname(path);
  const optPath = join(dir, `_opt_${name}`);
  
  try {
    const origStats = await stat(path);
    const origSize = origStats.size;

    // Read into buffer first (avoids file lock on read)
    const { default: fs } = await import('fs');
    const buffer = fs.readFileSync(path);

    // Compress to new file
    await sharp(buffer)
      .resize({ width, withoutEnlargement: true })
      .webp({ quality, effort: 6 })
      .toFile(optPath);

    const newStats = await stat(optPath);
    const newSize = newStats.size;
    const savings = ((1 - newSize / origSize) * 100).toFixed(1);

    // Backup original
    const backupSubDir = dir.replace(/.*public[/\\]assets/, '').replace(/\\/g, '/');
    const backupPath = join(BACKUP_DIR, backupSubDir, name);
    await mkdir(dirname(backupPath), { recursive: true });
    
    try {
      await copyFile(path, backupPath);
    } catch (e) {
      // backup may already exist from first run
    }

    // Now swap: delete original, rename opt to original name
    try {
      await unlink(path);
      await rename(optPath, path);
      console.log(`  🟢 ${name}: ${formatSize(origSize)} → ${formatSize(newSize)} (${savings}% smaller)`);
    } catch (e) {
      // If delete fails, at least we have the optimized version
      console.log(`  🟡 ${name}: Compressed to _opt_${name} (${formatSize(newSize)}) — original locked, manual swap needed`);
    }
  } catch (err) {
    console.error(`  ❌ ${name}: ${err.message}`);
  }
}

console.log('Retrying 7 locked WebP files...\n');
for (const f of files) {
  await processFile(f);
}
console.log('\nDone!');
