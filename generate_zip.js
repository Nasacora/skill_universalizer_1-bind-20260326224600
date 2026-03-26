const fs = require('fs');
const path = require('path');

// Simple ZIP creator using Node.js built-ins
function readAllFiles(dir, baseDir = dir) {
  const results = [];
  if (!fs.existsSync(dir)) return results;
  
  const items = fs.readdirSync(dir);
  for (const item of items) {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);
    if (stat.isDirectory()) {
      results.push(...readAllFiles(fullPath, baseDir));
    } else {
      const relativePath = path.relative(baseDir, fullPath);
      results.push({ path: relativePath, content: fs.readFileSync(fullPath) });
    }
  }
  return results;
}

async function createZip() {
  // Try to use jszip
  let JSZip;
  try {
    JSZip = require('jszip');
  } catch(e) {
    console.log('Installing jszip...');
    require('child_process').execSync('npm install jszip', { stdio: 'inherit' });
    JSZip = require('jszip');
  }

  const zip = new JSZip();

  // Collect all project files
  const dirs = ['.claude', 'README.md'];
  
  for (const item of dirs) {
    if (!fs.existsSync(item)) {
      console.log(`Skipping ${item} (not found)`);
      continue;
    }
    
    const stat = fs.statSync(item);
    if (stat.isDirectory()) {
      const files = readAllFiles(item, '.');
      for (const file of files) {
        zip.file(`skill-universalizer-project/${file.path}`, file.content);
        console.log(`  + ${file.path}`);
      }
    } else {
      zip.file(`skill-universalizer-project/${item}`, fs.readFileSync(item));
      console.log(`  + ${item}`);
    }
  }

  const buffer = await zip.generateAsync({
    type: 'nodebuffer',
    compression: 'DEFLATE',
    compressionOptions: { level: 9 }
  });

  fs.writeFileSync('skill-universalizer.zip', buffer);
  const sizeKB = (buffer.length / 1024).toFixed(1);
  console.log(`\n✅ ZIP creado: skill-universalizer.zip (${sizeKB} KB)`);
}

createZip().catch(console.error);
