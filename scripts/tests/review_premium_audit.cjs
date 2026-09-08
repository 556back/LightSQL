// Reconcile the HTML auditor with verified React/Radix component semantics.
// Keep the raw report intact. Any unrecognized finding remains a failure.
const fs = require('node:fs')
const ts = require('typescript')
const report = JSON.parse(fs.readFileSync('.local/premium-audit.json', 'utf8'))
const resolved = [], unresolved = []
for (const finding of report.findings) {
  const text = fs.readFileSync(finding.file, 'utf8')
  const source = ts.createSourceFile(finding.file, text, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX)
  let node
  function visit(current) {
    if (ts.isJsxOpeningElement(current) && ["Button", "Form"].includes(current.tagName.getText(source)) && source.getLineAndCharacterOfPosition(current.getStart(source)).line + 1 === finding.line) node = current
    ts.forEachChild(current, visit)
  }
  visit(source)
  const attr = (element, name) => element.attributes.properties.some(p => p.name?.getText(source) === name)
  let reason
  if (node?.tagName.getText(source) === 'Form' && finding.ruleId === 'form.novalidate-missing' && text.includes('"@/components/ui/form"')) {
    const provider = fs.readFileSync('frontend/src/components/ui/form.tsx', 'utf8')
    const child = node.parent.children.find(n => ts.isJsxElement(n) && n.openingElement.tagName.getText(source) === 'form')
    if (provider.includes('const Form = FormProvider') && child && attr(child.openingElement, 'noValidate')) reason = 'Form is the RHF context provider, not an HTML form; its actual form declares noValidate.'
  }
  if (node?.tagName.getText(source) === 'Button' && finding.ruleId === 'affordance.actionless-button') {
    const element = node.parent
    const link = element.children.find(n => ts.isJsxElement(n) && ['Link', 'RouterLink'].includes(n.openingElement.tagName.getText(source)))
    if (attr(node, 'asChild') && link && attr(link.openingElement, 'to')) reason = 'Radix Slot renders the child router link with a real to destination, not an actionless button.'
    const parent = element.parent
    if (ts.isJsxElement(parent) && ['DialogTrigger', 'DropdownMenuTrigger'].includes(parent.openingElement.tagName.getText(source)) && attr(parent.openingElement, 'asChild') && text.includes('"@/components/ui/')) reason = 'The canonical Radix trigger injects button handlers through asChild.'
  }
  if (reason) resolved.push({ ...finding, classification: 'verified-parser-false-positive', reason })
  else unresolved.push(finding)
}
fs.writeFileSync('.local/premium-audit-reviewed.json', JSON.stringify({ rawSummary: report.summary, resolved, unresolved }, null, 2))
console.log(`Reviewed audit: ${resolved.length} verified React/Radix parser false positives; ${unresolved.length} unresolved findings.`)
if (unresolved.length) { console.error(unresolved); process.exitCode = 1 }
