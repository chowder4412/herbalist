const http = require('http');
const fs = require('fs');
const path = require('path');

let PORT = parseInt(process.env.PORT || '8000', 10);
const PUBLIC_DIR = __dirname;

function createServer(port) {
    const server = http.createServer((req, res) => {
        const reqPath = req.url === '/' ? 'index.html' : path.normalize(req.url).replace(/^(\.\.[\/\\])+/, '');
        const filePath = path.resolve(PUBLIC_DIR, reqPath);

        // Security check against directory traversal
        if (!filePath.startsWith(path.resolve(PUBLIC_DIR))) {
            res.writeHead(403, { 'Content-Type': 'application/json' });
            return res.end(JSON.stringify({ error: 'Forbidden: Invalid path' }));
        }

        fs.readFile(filePath, (err, content) => {
            if (err) {
                res.writeHead(404, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'File not found' }));
            } else {
                let contentType = 'text/html';
                if (filePath.endsWith('.js')) contentType = 'text/javascript';
                if (filePath.endsWith('.css')) contentType = 'text/css';
                if (filePath.endsWith('.json')) contentType = 'application/json';

                const allowedOrigin = process.env.CORS_ALLOWED_ORIGIN || '*';
                res.writeHead(200, { 
                    'Content-Type': contentType,
                    'Access-Control-Allow-Origin': allowedOrigin
                });
                res.end(content, 'utf-8');
            }
        });
    });

    server.on('error', (err) => {
        if (err.code === 'EADDRINUSE') {
            console.log(`⚠️ Port ${port} is already in use (server is already running!). Trying fallback port ${port + 1}...`);
            createServer(port + 1);
        } else {
            console.error('Server error:', err);
        }
    });

    server.listen(port, () => {
        console.log(`\n🌿 Herbalist AI Server is running!`);
        console.log(`🔗 Open in your browser: http://localhost:${port}\n`);
    });
}

createServer(PORT);
