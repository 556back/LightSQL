// Exercise the production UI with every API request intercepted locally.
const { chromium, expect } = require('@playwright/test')
const fs = require('node:fs')
const path = require('node:path')
const base = process.env.LIGHTSQL_UI_URL || 'http://127.0.0.1:8000'
const output = path.resolve(__dirname, '../../.local/quality-review')
const definition = { name: '评分核验', cases: [{ id: 'net', split: 'blind' }] }
const dataset = { id: 'gold', name: definition.name, digest: 'a'.repeat(64), provenance: 'synthetic', dev: 0, blind: 25 }
const results = Array.from({ length: 25 }, (_, index) => ({ case_id: `case-${index + 1}`, correct: index === 24, error_category: index === 24 ? 'none' : 'plan', difference: index === 24 ? null : { code: 'row_count', expected_count: 3, actual_count: 2 } }))
results[1].difference = { code: 'numeric_value', row: 2, column: 1, side: 'actual' }
delete results[2].difference
const runDefinition = { dataset_id: 'gold', dataset_digest: dataset.digest, split: 'blind', observations: [] }
const run = { id: 'run', model: '本地回放', context_variant: 'C', evidence: 'protocol_replay', split: 'blind', created_at: '2026-09-08T01:00:00Z', summary: { total: 25, correct: 1, end_to_end_accuracy: .04, coverage: 1, answer_precision: .04, p95_ms: 12, critical_errors: 0, cost: null, currency: 'CNY', errors: { plan: 24 }, cases: results } }

async function main() {
  fs.mkdirSync(output, { recursive: true })
  const browser = await chromium.launch({ channel: 'msedge', headless: true })
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, locale: 'zh-CN' })
  await context.addInitScript(() => { localStorage.setItem('access_token', 'fixture'); localStorage.setItem('vite-ui-theme', 'light') })
  const page = await context.newPage()
  const errors = [], writes = [], checks = []
  let datasets = [dataset], runs = [run], failUpload = false, delayRuns = false, failRuns = false
  page.on('pageerror', error => errors.push(error.message))
  await page.route('**/api/v1/**', async route => {
    const request = route.request(), endpoint = new URL(request.url()).pathname.replace('/api/v1', '')
    const respond = (json, status = 200) => route.fulfill({ status, json })
    if (endpoint === '/users/me') return respond({ id: 'admin', email: 'fixture@example.com', is_superuser: true, is_active: true })
    if (endpoint === '/quality/operations') return respond({ detail: '本地运维夹具未启用' }, 503)
    if (request.method() === 'POST') {
      writes.push({ endpoint, body: request.postDataJSON() })
      if (failUpload) return respond({ detail: '题集不存在或摘要不匹配' }, 409)
      if (endpoint === '/quality/datasets') { datasets = [dataset]; return respond(dataset, 201) }
      if (endpoint === '/quality/runs') return respond({ id: run.id, summary: run.summary }, 201)
    }
    if (endpoint === '/quality/datasets') return respond(datasets)
    if (endpoint === '/quality/datasets/gold') return respond({ id: dataset.id, digest: dataset.digest, definition })
    if (endpoint === '/quality/runs/run') return respond({ id: run.id, summary: run.summary, definition: runDefinition })
    if (endpoint === '/quality/runs') {
      if (delayRuns) await new Promise(resolve => setTimeout(resolve, 700))
      return failRuns ? respond({ detail: '评测读取失败' }, 503) : respond(runs)
    }
    errors.push(`Unexpected API ${request.method()} ${endpoint}`)
    return respond([], 404)
  })
  const upload = (label, value, name = 'fixture.json') => page.getByLabel(label, { exact: true }).setInputFiles({ name, mimeType: 'application/json', buffer: Buffer.from(typeof value === 'string' ? value : JSON.stringify(value)) })
  const shot = name => page.screenshot({ path: path.join(output, `${name}.png`), fullPage: true, animations: 'disabled' })
  try {
    await page.goto(base + '/quality')
    await page.getByRole('button', { name: '质量评测', exact: true }).click()
    await expect(page.getByText('选择或导入题集，开始核对评测记录。')).toBeVisible()
    await upload('导入金标题集 JSON', '{broken')
    await expect(page.getByRole('alert')).toContainText('文件不是有效的 JSON')
    await upload('导入金标题集 JSON', { definition: runDefinition })
    await expect(page.getByRole('alert')).toContainText('请选择包含 cases')
    expect(writes).toHaveLength(0)
    await upload('导入金标题集 JSON', '\uFEFF' + JSON.stringify({ id: 'old', digest: dataset.digest, definition }))
    await expect(page.getByRole('status').filter({ hasText: '题集已导入' })).toBeVisible()
    expect(writes.at(-1).body).toEqual(definition)
    await expect(page.getByLabel('比较题集')).toHaveValue('gold')
    await expect(page.getByLabel('评测集合')).toHaveValue('blind')
    checks.push('Malformed and wrong-kind files are rejected locally; BOM export imports and selects blind set')

    const summary = page.locator('summary').filter({ hasText: '逐题错误分析' })
    await summary.focus()
    await page.keyboard.press('Enter')
    await expect(page.getByText('第 1–20 题，共 24 题')).toBeVisible()
    await expect(page.getByText(/预期 3 行，实际 2 行/).first()).toBeVisible()
    await expect(page.getByText(/实际结果第 2 行，第 1 列/)).toBeVisible()
    await expect(page.getByText('历史记录未保存具体差异，请查阅导出证据')).toBeVisible()
    await page.getByRole('button', { name: '下一页题目' }).click()
    await expect(page.getByText('第 21–24 题，共 24 题')).toBeVisible()
    await page.getByLabel('仅看未通过').uncheck()
    await expect(page.getByText('第 1–20 题，共 25 题')).toBeVisible()
    await shot('diagnostics-desktop')
    checks.push('Keyboard disclosure, localized diagnostics, legacy fallback, failed-only pagination and reset')

    const datasetDownload = page.waitForEvent('download')
    await page.getByRole('button', { name: '导出题集', exact: true }).click()
    const exportedDataset = JSON.parse(fs.readFileSync(await (await datasetDownload).path(), 'utf8'))
    expect(exportedDataset.definition).toEqual(definition)
    await upload('导入金标题集 JSON', exportedDataset)
    await expect(page.getByRole('status').filter({ hasText: '题集已导入' })).toBeVisible()
    const runDownload = page.waitForEvent('download')
    await page.getByRole('button', { name: '导出运行证据' }).click()
    const exportedRun = JSON.parse(fs.readFileSync(await (await runDownload).path(), 'utf8'))
    await page.getByLabel('评测集合').selectOption('dev')
    await expect(page.getByText('该集合尚无评测运行。')).toBeVisible()
    failUpload = true
    await upload('导入评测运行 JSON', exportedRun)
    await expect(page.getByRole('alert')).toContainText('题集不存在或摘要不匹配')
    await expect(page.getByLabel('评测集合')).toHaveValue('dev')
    failUpload = false
    await upload('导入评测运行 JSON', exportedRun)
    await expect(page.getByRole('status').filter({ hasText: '评测运行已导入' })).toBeVisible()
    await expect(page.getByLabel('评测集合')).toHaveValue('blind')
    expect(writes.at(-1).body).toEqual(runDefinition)
    checks.push('Both downloads round-trip; failed upload keeps selection; successful run import selects original dataset and split')

    await page.setViewportSize({ width: 390, height: 844 })
    await page.emulateMedia({ reducedMotion: 'reduce', colorScheme: 'dark' })
    await page.evaluate(() => { document.documentElement.classList.add('dark') })
    await summary.click()
    await expect(page.getByLabel('仅看未通过')).toBeVisible()
    await page.getByLabel('评测集合').focus()
    await page.keyboard.press('Alt+ArrowDown')
    await shot('diagnostics-mobile-dark-select')
    await page.keyboard.press('Escape')
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true)
    await shot('diagnostics-mobile-dark')
    checks.push('390px dark/reduced-motion layout, native select popup and no horizontal overflow')

    await page.getByLabel('比较题集').selectOption('')
    delayRuns = true
    await page.reload()
    await page.getByRole('button', { name: '质量评测', exact: true }).click()
    await page.getByLabel('比较题集').selectOption('gold')
    await expect(page.getByText('正在读取评测运行…')).toBeVisible()
    await page.getByLabel('评测集合').selectOption('blind')
    await expect(page.locator('article')).toHaveCount(1)
    checks.push('Pending run loading is announced')
    failRuns = true
    await page.reload()
    await page.getByRole('button', { name: '质量评测', exact: true }).click()
    await page.getByLabel('比较题集').selectOption('gold')
    await expect(page.getByText('评测读取失败')).toBeVisible({ timeout: 20000 })
    failRuns = false; runs = []
    await page.getByRole('button', { name: '重试', exact: true }).click()
    await expect(page.getByText('该集合尚无评测运行。')).toBeVisible()
    checks.push('Run read failure, explicit retry and empty state')
    expect(errors).toEqual([])
    fs.writeFileSync(path.join(output, 'report.json'), JSON.stringify({ checks, errors, writes: writes.length }, null, 2))
    console.log(JSON.stringify({ checks, errors, writes: writes.length }, null, 2))
  } finally { await browser.close() }
}
main().catch(error => { console.error(error); process.exitCode = 1 })
