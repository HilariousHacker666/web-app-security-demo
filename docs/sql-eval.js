function stripSqlComment(str) {
  let inQuote = false;
  for (let i = 0; i < str.length; i++) {
    const ch = str[i];
    if (ch === "'") inQuote = !inQuote;
    if (!inQuote && str[i] === '-' && str[i + 1] === '-') {
      return str.slice(0, i);
    }
  }
  return str;
}

function splitTopLevel(str, delim) {
  const parts = [];
  let current = '';
  let inQuote = false;
  let i = 0;
  while (i < str.length) {
    const ch = str[i];
    if (ch === "'") inQuote = !inQuote;
    if (!inQuote && str.slice(i, i + delim.length).toUpperCase() === delim.toUpperCase()) {
      parts.push(current);
      current = '';
      i += delim.length;
      continue;
    }
    current += ch;
    i++;
  }
  parts.push(current);
  return parts;
}

function evalCondition(cond, row) {
  cond = cond.trim();
  const eqIndex = cond.indexOf('=');
  if (eqIndex === -1) return false;
  const lhs = cond.slice(0, eqIndex).trim();
  const rhs = cond.slice(eqIndex + 1).trim();
  const resolve = (token) => {
    if (token.startsWith("'") && token.endsWith("'") && token.length >= 2) {
      return token.slice(1, -1);
    }
    return row[token] !== undefined ? String(row[token]) : undefined;
  };
  return resolve(lhs) === resolve(rhs);
}

function evalWhereClause(clause, row) {
  const orGroups = splitTopLevel(clause, ' OR ');
  return orGroups.some((group) => {
    const andConds = splitTopLevel(group, ' AND ');
    return andConds.every((cond) => evalCondition(cond, row));
  });
}

// Simulates: SELECT * FROM users WHERE username = '<u>' AND password = '<p>'
// built by naive string concatenation, "executed" against a mock table.
function vulnerableLogin(username, password, users) {
  const rawQuery =
    "SELECT * FROM users WHERE username = '" + username +
    "' AND password = '" + password + "'";
  const cleaned = stripSqlComment(rawQuery);
  const whereClause = cleaned.split(/WHERE/i)[1].trim();
  const matched = users.find((row) => evalWhereClause(whereClause, row));
  return { rawQuery, cleaned, matched };
}
