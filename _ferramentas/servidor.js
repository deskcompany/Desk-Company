const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;
// As telas moram em telas/<modulo>/ desde 08/out/2026. O servidor entrega a
// pasta `telas`, entao o endereco de uma tela e /<modulo>/<arquivo>.
const ROOT = path.resolve(__dirname, '..', 'telas');
const INICIAL = 'pagina-dashboard-kpis.html';

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.woff2': 'font/woff2',
  '.woff': 'font/woff',
  '.ttf': 'font/ttf',
  '.md': 'text/markdown; charset=utf-8'
};

// Em qual pasta esta uma tela, pelo nome do arquivo. O nome e unico no sistema.
function pastaDe(arquivo) {
  const pastas = fs.readdirSync(ROOT, { withFileTypes: true }).filter((d) => d.isDirectory());
  for (const d of pastas) {
    if (fs.existsSync(path.join(ROOT, d.name, arquivo))) return d.name;
  }
  return null;
}

const server = http.createServer((req, res) => {
  const partes = req.url.split('?');
  let reqPath = decodeURI(partes[0]);
  const query = partes.length > 1 ? '?' + partes.slice(1).join('?') : '';
  if (reqPath === '/' || reqPath === '') reqPath = '/' + INICIAL;

  // Endereco antigo, sem a pasta (/pagina-x.html): REDIRECIONA para o novo.
  // Tem de ser redirecionamento de verdade, e nao entrega direta: os links de
  // uma tela sao relativos a pasta dela, e so resolvem certo se o navegador
  // souber em que pasta esta.
  const nu = reqPath.lastIndexOf('/') === 0 && reqPath.startsWith('/pagina-') && reqPath.endsWith('.html');
  if (nu) {
    const arquivo = reqPath.slice(1);
    const pasta = pastaDe(arquivo);
    if (pasta) {
      res.writeHead(302, { Location: '/' + pasta + '/' + arquivo + query });
      res.end();
      return;
    }
  }

  const filePath = path.join(ROOT, reqPath);
  if (!filePath.startsWith(ROOT)) {
    res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('403 Proibido');
    return;
  }

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end(`<h2>404 - Página não encontrada</h2><p>O arquivo <code>${reqPath}</code> não existe na pasta <code>telas</code> do projeto.</p>`);
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME[ext] || 'application/octet-stream';
    res.writeHead(200, {
      'Content-Type': contentType,
      'Access-Control-Allow-Origin': '*'
    });
    fs.createReadStream(filePath).pipe(res);
  });
});

server.listen(PORT, () => {
  console.log(`[Desk ERP Server] Servidor local ativo em: http://localhost:${PORT}/`);
});
