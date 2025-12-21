/* Debug script to parse a TSX file and emit diagnostics to Cursor debug logger. */
const fs = require('fs');
const path = require('path');

const ENDPOINT =
  'http://127.0.0.1:7242/ingest/e1d41711-273d-454d-b5e5-330f005364fd';

const DEBUG_LOG_PATH = path.join(process.cwd(), '..', '.cursor', 'debug.log');

function send(payload) {
  try {
    // Node 18+ has global fetch; if not present, skip sending.
    if (typeof fetch === 'function') {
      fetch(ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      }).catch(() => {});
    }
  } catch (_) {}

  // Fallback: also write to local debug log file so we always have evidence.
  try {
    fs.appendFileSync(DEBUG_LOG_PATH, JSON.stringify(payload) + '\n', 'utf8');
  } catch (_) {}
}

function log(hypothesisId, location, message, data) {
  const payload = {
    sessionId: 'debug-session',
    runId: process.env.RUN_ID || 'pre-fix',
    hypothesisId,
    location,
    message,
    data,
    timestamp: Date.now(),
  };
  send(payload);
  // Also print to stdout for immediate terminal visibility.
  try {
    // Keep it compact.
    console.log(JSON.stringify(payload));
  } catch (_) {}
}

function main() {
  const rel =
    'src/app/(dashboard)/options/tail-hedge/page.tsx'.replace(/\//g, path.sep);
  const filePath = path.join(process.cwd(), rel);

  log('A', 'debug_parse_tail_hedge.cjs:main', 'Starting parse', { filePath });

  const content = fs.readFileSync(filePath, 'utf8');

  // Basic character stats to catch obvious unterminated constructs.
  const stats = {
    length: content.length,
    crlfCount: (content.match(/\r\n/g) || []).length,
    lfCount: (content.match(/\n/g) || []).length,
    openBraces: (content.match(/\{/g) || []).length,
    closeBraces: (content.match(/\}/g) || []).length,
    openParens: (content.match(/\(/g) || []).length,
    closeParens: (content.match(/\)/g) || []).length,
    openBrackets: (content.match(/\[/g) || []).length,
    closeBrackets: (content.match(/\]/g) || []).length,
    backticks: (content.match(/`/g) || []).length,
  };
  log('B', 'debug_parse_tail_hedge.cjs:stats', 'File stats', stats);

  // Look around the main return to detect odd invisible chars.
  const needle = '\n  return (\n';
  const idx = content.indexOf(needle);
  const windowStart = Math.max(0, (idx === -1 ? 0 : idx) - 200);
  const windowEnd = Math.min(content.length, (idx === -1 ? 200 : idx + 200));
  const snippet = content.slice(windowStart, windowEnd);
  const suspiciousChars = [];
  for (let i = 0; i < snippet.length; i++) {
    const code = snippet.charCodeAt(i);
    // Track non-ASCII control chars except \r \n \t
    if (
      (code < 32 && code !== 9 && code !== 10 && code !== 13) ||
      code === 0xfeff
    ) {
      suspiciousChars.push({ at: windowStart + i, code });
    }
  }
  log('C', 'debug_parse_tail_hedge.cjs:snippet', 'Return() vicinity', {
    needleFound: idx !== -1,
    windowStart,
    windowEnd,
    suspiciousChars,
  });

  // TypeScript parse diagnostics (best approximation to Next/SWC parsing).
  let ts;
  try {
    ts = require('typescript');
  } catch (e) {
    log('D', 'debug_parse_tail_hedge.cjs:ts', 'typescript not available', {
      error: String(e && e.message ? e.message : e),
    });
    process.exit(2);
  }

  const sourceFile = ts.createSourceFile(
    filePath,
    content,
    ts.ScriptTarget.Latest,
    /*setParentNodes*/ true,
    ts.ScriptKind.TSX
  );

  const diags = sourceFile.parseDiagnostics || [];
  const mapped = diags.slice(0, 20).map((d) => {
    const msg = ts.flattenDiagnosticMessageText(d.messageText, '\n');
    const start = typeof d.start === 'number' ? d.start : 0;
    const lc = sourceFile.getLineAndCharacterOfPosition(start);
    return {
      code: d.code,
      message: msg,
      start,
      line: lc.line + 1,
      character: lc.character + 1,
      length: d.length,
    };
  });

  log('E', 'debug_parse_tail_hedge.cjs:ts', 'parseDiagnostics', {
    diagnosticCount: diags.length,
    diagnostics: mapped,
  });

  // Also emit the first error line excerpt to help pinpoint root cause.
  if (mapped.length > 0) {
    const first = mapped[0];
    const lines = content.split(/\r?\n/);
    const lineText = lines[first.line - 1] || '';
    log('F', 'debug_parse_tail_hedge.cjs:first', 'first diagnostic context', {
      line: first.line,
      character: first.character,
      lineText,
    });
  }

  // Exit non-zero if parse errors exist to make CI-style usage easier.
  process.exit(diags.length > 0 ? 1 : 0);
}

main();


