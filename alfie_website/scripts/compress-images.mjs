/**
 * ALFIE Image Compression Script
 * Converts all industry photos to optimized WebP format
 * Backs up originals before replacing
 */
import sharp from 'sharp';
import { readdir, stat, mkdir, copyFile, unlink, rename } from 'fs/promises';
import { join, extname, basename, dirname } from 'path';

const ASSETS_ROOT = 'e:/Me/A.L.F.I.E/alfie_website/public/assets';
const BACKUP_DIR  = 'e:/Me/A.L.F.I.E/alfie_website/_asset_backups';

// Target sizes based on usage:
// Hero/large photos: max 1920px wide, quality 75 → ~150-300KB
// Portrait/headshots: max 800px wide, quality 78 → ~50-120KB  
// Detail shots: max 1200px wide, quality 75 → ~100-200KB
// Logo: max 600px wide, quality 85 → ~30-60KB

const COMPRESSION_PROFILES = {
  // Large environmental/atmosphere shots
  large: { width: 1920, quality: 75 },
  // Portraits and headshots  
  portrait: { width: 800, quality: 78 },
  // Mid-size contextual shots
  medium: { width: 1200, quality: 75 },
  // Brand assets
  brand: { width: 600, quality: 85 },
};

// Map each file to its compression profile
const FILE_PROFILES = {
  // Clinics
  'clinic_female.jpg':          'portrait',
  'clinic_male.jpg':            'portrait',
  'dentist_clinic.webp':        'large',
  'doctor.webp':                'portrait',
  'doctor2.webp':               'portrait',
  'niche_clinic_consult.jpeg':  'large',
  // Car Rental
  'carrental_female.jpg':       'portrait',
  'carrental_male.jpg':         'portrait',
  'chauffer.webp':              'medium',
  'driver-service.webp':        'large',
  'niche_fleet_vip.jpeg':       'large',
  'rental_car.webp':            'large',
  // Hospitality
  'hospitality_female.jpg':     'portrait',
  'hospitality_male.jpg':       'portrait',
  'niche_hospitality_dining.jpeg': 'large',
  'restaurant.webp':            'large',
  // Law Firms
  'law.webp':                   'large',
  'law2.webp':                  'large',
  'law_female.jpg':             'portrait',
  'law_male.jpg':               'portrait',
  'niche_legal_detail.jpeg':    'medium',
  // Real Estate
  'niche_realestate_luxury.jpeg': 'large',
  'realestate_female.jpg':      'portrait',
  'realestate_male.jpg':        'portrait',
  // Brand
  'logo.png':                   'brand',
};

async function findImages(dir) {
  const results = [];
  const entries = await readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      results.push(...await findImages(fullPath));
    } else {
      const ext = extname(entry.name).toLowerCase();
      if (['.jpg', '.jpeg', '.png', '.webp'].includes(ext)) {
        results.push(fullPath);
      }
    }
  }
  return results;
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)}KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)}MB`;
}

async function compressImage(filePath) {
  const name = basename(filePath);
  const profile = FILE_PROFILES[name];
  
  if (!profile) {
    console.log(`  ⏭  SKIP: ${name} (no profile defined)`);
    return null;
  }

  const config = COMPRESSION_PROFILES[profile];
  const originalStats = await stat(filePath);
  const originalSize = originalStats.size;

  // Create backup
  const normalizedFile = filePath.replace(/\\/g, '/');
  const normalizedRoot = ASSETS_ROOT.replace(/\\/g, '/');
  const relativePath = normalizedFile.replace(normalizedRoot, '');
  const backupPath = join(BACKUP_DIR, relativePath);
  await mkdir(dirname(backupPath), { recursive: true });
  await copyFile(filePath, backupPath);

  // Determine output path (always .webp)
  const ext = extname(filePath);
  const webpPath = filePath.replace(ext, '.webp');
  const tempPath = filePath + '.tmp.webp';

  try {
    await sharp(filePath)
      .resize({ width: config.width, withoutEnlargement: true })
      .webp({ quality: config.quality, effort: 6 })
      .toFile(tempPath);

    const newStats = await stat(tempPath);
    const newSize = newStats.size;
    const savings = ((1 - newSize / originalSize) * 100).toFixed(1);

    // If original wasn't webp, remove original and rename temp
    if (ext.toLowerCase() !== '.webp') {
      await unlink(filePath);
      await rename(tempPath, webpPath);
    } else {
      // Replace the webp in-place
      await unlink(filePath);
      await rename(tempPath, webpPath);
    }

    const result = {
      file: name,
      profile,
      original: formatSize(originalSize),
      compressed: formatSize(newSize),
      savings: `${savings}%`,
      outputName: basename(webpPath),
    };

    const color = parseFloat(savings) > 50 ? '🟢' : parseFloat(savings) > 20 ? '🟡' : '⚪';
    console.log(`  ${color} ${name} → ${basename(webpPath)}: ${formatSize(originalSize)} → ${formatSize(newSize)} (${savings}% smaller)`);
    
    return result;
  } catch (err) {
    console.error(`  ❌ FAILED: ${name}: ${err.message}`);
    // Clean up temp file if it exists
    try { await unlink(tempPath); } catch {}
    return null;
  }
}

async function main() {
  console.log('╔══════════════════════════════════════════════╗');
  console.log('║  A.L.F.I.E Image Compression Pipeline       ║');
  console.log('╚══════════════════════════════════════════════╝');
  console.log();

  // Create backup directory
  await mkdir(BACKUP_DIR, { recursive: true });
  console.log(`📦 Backups will be saved to: ${BACKUP_DIR}`);
  console.log();

  const images = await findImages(ASSETS_ROOT);
  console.log(`Found ${images.length} images to process.\n`);

  let totalOriginal = 0;
  let totalCompressed = 0;
  let processed = 0;
  const results = [];

  for (const img of images) {
    const result = await compressImage(img);
    if (result) {
      results.push(result);
      processed++;
    }
  }

  // Summary
  console.log('\n═══════════════════════════════════════════════');
  console.log(`✅ Compressed ${processed}/${images.length} images`);
  console.log(`📦 Originals backed up to: ${BACKUP_DIR}`);
  console.log('═══════════════════════════════════════════════');
}

main().catch(console.error);
