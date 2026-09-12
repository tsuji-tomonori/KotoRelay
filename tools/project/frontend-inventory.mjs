/** TypeScript構文木から実装コンポーネント・API呼出し・操作イベントを列挙する。 */
import ts from 'typescript';
import { readdirSync, readFileSync } from 'node:fs';
import { join, relative } from 'node:path';
const root = process.cwd();
function files(folder) {
  return readdirSync(folder, { withFileTypes: true }).flatMap((entry) =>
    entry.isDirectory()
      ? files(join(folder, entry.name))
      : /\.tsx?$/.test(entry.name)
        ? [join(folder, entry.name)]
        : [],
  );
}
const result = { components: [], calls: [], interactions: [] };
for (const path of files(join(root, 'frontend/src')).sort()) {
  const file = ts.createSourceFile(
    path,
    readFileSync(path, 'utf8'),
    ts.ScriptTarget.Latest,
    true,
    path.endsWith('.tsx') ? ts.ScriptKind.TSX : ts.ScriptKind.TS,
  );
  const source = relative(root, path);
  function visit(node) {
    const line = file.getLineAndCharacterOfPosition(node.getStart(file)).line + 1;
    if (ts.isFunctionDeclaration(node) && node.name && /^[A-Z]/.test(node.name.text))
      result.components.push({ name: node.name.text, source, line });
    if (
      ts.isCallExpression(node) &&
      /^(api|getImage|set[A-Z]\w*)$/.test(node.expression.getText(file))
    )
      result.calls.push({ source, line, expression: node.getText(file) });
    if (ts.isJsxAttribute(node) && /^on[A-Z]/.test(node.name.getText(file)))
      result.interactions.push({
        source,
        line,
        event: node.name.getText(file),
        expression: node.initializer?.getText(file) ?? '',
      });
    ts.forEachChild(node, visit);
  }
  visit(file);
}
process.stdout.write(JSON.stringify(result));
