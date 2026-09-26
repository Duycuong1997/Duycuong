'use strict';

// Minimal static file server (no dependencies) used by Playwright's webServer
// and for local preview: `node scripts/serve.js`.
// Document root is the repository root so that public/index.html can reference
// ../src/validation.js.
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '..');
const PORT = process.env.PORT ? Number(process.env.PORT) : 4173;

const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
};

const server = http.createServer((req, res) => {
  const urlPath = decodeURIComponent(req.url.split('?')[0]);
  const safePath = path
    .normalize(urlPath)
    .replace(/^(\.\.[/\\])+/, ''); // prevent path traversal
  const filePath = path.join(ROOT, safePath === '/' ? '/public/index.html' : safePath);

  if (!filePath.startsWith(ROOT)) {
    res.writeHead(403).end('Forbidden');
    return;
  }

  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404).end('Not Found');
      return;
    }
    const type = TYPES[path.extname(filePath)] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': type }).end(data);
  });
});

server.listen(PORT, () => {
  // eslint-disable-next-line no-console
  console.log(`Static server running at http://localhost:${PORT}/`);
});
