// Run after `npm --prefix frontend run build`, with a local LightSQL server.
// API fixtures are intercepted in the browser: no database writes or model calls.
const { chromium, expect } = require('@playwright/test')
const fs = require('node:fs')
const path = require('node:path')
const base = process.env.LIGHTSQL_UI_URL || 'http://127.0.0.1:8000'
const output = path.resolve(__dirname, '../../.local/ux-review')
const source = { id: 'source-sales', name: '销售业务库', database_type: 'postgresql', database: 'sales', enabled: true, revision: 1, host: 'localhost', port: 5432, username: 'reader', tls_mode: 'prefer', description: '订单与客户数据', created_at: '2026-09-07T01:00:00Z' }
const table = { schema_name: 'public', name: 'orders', kind: 'table', comment: '订单明细', columns: [
  { name: 'id', data_type: 'integer', primary_key: true, nullable: false, comment: '订单编号' },
  { name: 'amount', data_type: 'numeric', primary_key: false, nullable: false, comment: '订单金额' },
  { name: 'region', data_type: 'text', primary_key: false, nullable: true, comment: '销售地区' },
], foreign_keys: [], warnings: [] }
const secondTable = { ...table, name: 'customers', comment: '客户信息', columns: [{ name: 'customer_id', data_type: 'integer', primary_key: true, nullable: false, comment: '客户编号' }] }
const definition = { schema_version: 1, owner: '数据团队', timezone: 'Asia/Shanghai', external_allowed: false, models: [], dimensions: [], metrics: [], filters: [], relations: [], entities: [] }
const summaries = [
  { id: 'sales', name: '销售经营', description: '从订单、客户到销售趋势，了解每一笔收入的来源。', availability: 'ready', metric_count: 3, dimension_count: 4, current_version: 2, source_name: source.name },
  { id: 'inventory', name: '库存分析', description: '查看商品库存，识别需要补货的商品。', availability: 'draft', metric_count: 0, dimension_count: 0, current_version: 0, source_name: source.name },
  { id: 'review', name: '客户增长', description: '分析新客、复购和客户分布。', availability: 'needs_review', metric_count: 2, dimension_count: 3, current_version: 1, source_name: source.name },
]
async function main() {
  fs.mkdirSync(output, { recursive: true })
  const browser = await chromium.launch({ channel: 'msedge', headless: true })
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } })
  const page = await context.newPage()
  const errors = []
  const writes = []
  let isAdmin = true
  let syncFails = false
  let scopeFails = false
  let catalog = { source_id: source.id, revision: 1, source_revision: 1, version: 1, needs_sync: false, needs_confirmation: false, synced_at: '2026-09-07T02:00:00Z', scope: [{ schema_name: 'public', name: 'orders', kind: 'table' }], tables: [table, secondTable] }
  let draft = { ...summaries[1], source_id: source.id, enabled: true, revision: 1, member_ids: [], definition: structuredClone(definition) }
  await context.addInitScript(() => { localStorage.setItem('access_token', 'ui-fixture'); localStorage.setItem('vite-ui-theme', 'light') })
  page.on('pageerror', e => errors.push(e.message))
  await page.route('**/api/v1/**', async route => {
    const request = route.request()
    const url = new URL(request.url())
    const endpoint = url.pathname.replace('/api/v1', '')
    const method = request.method()
    const respond = (json, status = 200) => route.fulfill({ status, json })
    if (!['GET', 'HEAD'].includes(method)) writes.push({ endpoint, method, body: request.postDataJSON() })
    if (endpoint === '/users/me') return respond({ id: 'user', email: 'review@example.com', full_name: '数据管理员', is_active: true, is_superuser: isAdmin })
    if (endpoint === '/datasources/') return respond({ data: [source], count: 1 })
    if (endpoint === '/topics/' && method === 'GET') return respond(summaries)
    if (endpoint === '/topics/' && method === 'POST') return respond({ ...draft, ...request.postDataJSON() })
    if (endpoint === '/topics/inventory' && method === 'GET') return respond(draft)
    if (endpoint === '/topics/inventory/draft') {
      const body = request.postDataJSON()
      draft = { ...draft, ...body, revision: draft.revision + 1 }
      return respond(draft)
    }
    if (endpoint === '/topics/sales/published') return respond({ id: 'sales', name: '销售经营', description: '销售指标口径', version: 2, owner: '数据团队', timezone: 'Asia/Shanghai', metrics: [], dimensions: [] })
    if (endpoint === '/catalog/source-sales') return respond(catalog)
    if (endpoint === '/catalog/source-sales/jobs') return respond([])
    if (endpoint === '/catalog/source-sales/schemas') return respond(['public'])
    if (endpoint === '/catalog/source-sales/discover') return respond([table, secondTable])
    if (endpoint === '/catalog/source-sales/scope') {
      if (scopeFails) return respond({ detail: '选表范围已被其他管理员修改' }, 409)
      catalog = { ...catalog, scope: request.postDataJSON().objects, revision: catalog.revision + 1 }
      return respond(catalog)
    }
    if (endpoint === '/catalog/source-sales/sync') return syncFails ? respond({ detail: '同步服务暂不可用' }, 503) : respond({ id: 'job', status: 'queued' })
    if (endpoint.includes('conversations') && method === 'GET') return respond([])
    if (endpoint.includes('model-status')) return respond({ name: '本地模型', configured: false })
    if (method !== 'GET') errors.push(`Unexpected mutation: ${method} ${endpoint}`)
    return respond([])
  })
  async function screenshot(name) { await page.screenshot({ path: path.join(output, `${name}.png`), fullPage: true, animations: 'disabled' }) }
  async function noOverflow() { expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true) }
  try {
    await page.goto(base + '/topics')
    await expect(page.getByRole('heading', { name: '销售经营', exact: true })).toBeVisible()
    await screenshot('topics-desktop')
    await page.getByRole('button', { name: '可开始问数', exact: true }).click()
    await expect(page.locator('article')).toHaveCount(1)
    await page.getByRole('link', { name: '开始问数', exact: true }).click()
    await expect(page).toHaveURL(/ask\?topic=sales/)
    await expect(page.getByLabel('业务主题', { exact: true })).toHaveValue('sales')
    await screenshot('ask-desktop')
    await page.goto(base + '/topics')
    await page.getByLabel('搜索主题').fill('不存在')
    await expect(page.getByText('没有匹配的主题')).toBeVisible()
    await page.getByRole('button', { name: '清除筛选' }).click()
    await expect(page.locator('article')).toHaveCount(3)
    await page.getByRole('button', { name: '新建主题', exact: true }).click()
    await expect(page.getByLabel('绑定数据源')).toHaveValue(source.id)
    await expect(page.getByLabel('业务责任人')).toHaveValue('数据管理员')
    await page.getByLabel('主题名称', { exact: true }).fill('库存分析')
    await page.getByRole('button', { name: '创建并选择数据表' }).click()
    await expect(page.getByRole('button', { name: '添加数据表', exact: true })).toBeVisible()
    await screenshot('workspace-desktop')
    await page.getByRole('button', { name: '添加数据表', exact: true }).click()
    await page.getByLabel('目录对象').selectOption('0')
    await expect(page.getByLabel('业务名称', { exact: true })).toHaveValue('订单明细')
    // Clearing the table must not crash or preserve the old physical binding.
    await page.getByLabel('目录对象').selectOption('')
    await page.getByLabel('目录对象').selectOption('0')
    await page.getByLabel('每行数据代表什么').fill('每行是一笔订单')
    await page.getByRole('button', { name: '应用到工作区' }).click()
    await page.getByRole('button', { name: '保存草稿', exact: true }).click()
    await expect(page.getByRole('button', { name: '保存草稿', exact: true })).toBeDisabled()
    expect(draft.definition.models[0].id).toMatch(/^models_[a-z0-9_]+$/)
    expect(draft.definition.models[0].primary_key).toEqual(['id'])
    await page.getByRole('button', { name: '下一步：添加分析维度' }).click()
    await page.getByRole('button', { name: '添加维度', exact: true }).click()
    await expect(page.getByLabel('来自哪张数据表')).toHaveValue(draft.definition.models[0].id)
    await page.getByRole('button', { name: '取消', exact: true }).click()
    await page.getByRole('button', { name: /1.*选择数据表/ }).click()
    await page.getByRole('button', { name: '添加数据表', exact: true }).click()
    await page.getByLabel('目录对象').selectOption('1')
    await page.getByLabel('每行数据代表什么').fill('每行是一位客户')
    await page.getByRole('button', { name: '应用到工作区' }).click()
    await page.getByRole('button', { name: '保存草稿', exact: true }).click()
    await expect(page.getByRole('button', { name: '保存草稿', exact: true })).toBeDisabled()
    await page.getByRole('button', { name: /2.*添加分析维度/ }).click()
    await page.getByRole('button', { name: '添加维度', exact: true }).click()
    await page.getByLabel('来自哪张数据表').selectOption(draft.definition.models[0].id)
    await page.getByLabel('映射字段').selectOption('region')
    await page.getByLabel('来自哪张数据表').selectOption(draft.definition.models[1].id)
    await expect(page.getByLabel('映射字段')).toHaveValue('')
    await page.setViewportSize({ width: 390, height: 844 })
    await noOverflow()
    await screenshot('editor-mobile')
    await page.getByRole('button', { name: '取消', exact: true }).click()
    await noOverflow()
    await screenshot('workspace-mobile')
    await page.getByRole('button', { name: '高级配置：关联、条件与别名' }).click()
    await expect(page.getByRole('button', { name: '表间关联 0' })).toBeVisible()
    await page.goto(base + '/catalog')
    await expect(page.getByRole('heading', { name: 'orders', exact: true })).toBeVisible()
    await noOverflow()
    await screenshot('catalog-mobile')
    await page.setViewportSize({ width: 1440, height: 1000 })
    await screenshot('catalog-desktop')
    await page.getByRole('link', { name: '前往业务主题', exact: true }).click()
    await expect(page).toHaveURL(/topics\?source=source-sales/)
    await page.getByRole('button', { name: '新建主题', exact: true }).click()
    await expect(page.getByLabel('绑定数据源')).toHaveValue(source.id)
    await page.getByRole('button', { name: '取消', exact: true }).click()
    await page.goto(base + '/catalog?source=source-sales')
    await expect(page.locator('#catalog-source')).toHaveValue(source.id)
    await page.getByRole('button', { name: '选择数据表', exact: true }).click()
    await page.getByRole('button', { name: '保存并同步', exact: true }).click()
    await expect(page.getByText('数据表已保存，正在同步字段和关联')).toBeVisible()
    expect(writes.slice(-2).map(w => w.endpoint)).toEqual(['/catalog/source-sales/scope', '/catalog/source-sales/sync'])
    syncFails = true
    await page.getByRole('button', { name: '选择数据表', exact: true }).click()
    await page.getByRole('button', { name: '保存并同步', exact: true }).click()
    await expect(page.getByText(/选表已保存，但同步未启动/)).toBeVisible()
    scopeFails = true
    const count = writes.filter(w => w.endpoint.endsWith('/sync')).length
    await page.getByRole('button', { name: '选择数据表', exact: true }).click()
    await page.getByRole('button', { name: '保存并同步', exact: true }).click()
    await expect(page.getByText('选表范围已被其他管理员修改', { exact: true })).toBeVisible()
    expect(writes.filter(w => w.endpoint.endsWith('/sync')).length).toBe(count)
    await page.getByRole('button', { name: '取消', exact: true }).click()
    await page.setViewportSize({ width: 390, height: 844 })
    await page.goto(base + '/topics')
    await expect(page.locator('article')).toHaveCount(3)
    await noOverflow()
    await screenshot('topics-mobile')
    await page.evaluate(() => document.documentElement.classList.add('dark'))
    await screenshot('topics-dark-mobile')
    isAdmin = false
    await page.reload()
    await expect(page.getByRole('button', { name: '新建主题', exact: true })).toHaveCount(0)
    await expect(page.getByRole('link', { name: '查看业务口径' })).toHaveCount(3)
    await expect(page.getByRole('navigation', { name: '数据准备流程' })).toHaveCount(0)
    await page.goto(base + '/topics/sales')
    await page.getByRole('link', { name: '使用这个主题问数' }).click()
    await expect(page).toHaveURL(/ask\?topic=sales/)
    expect(errors).toEqual([])
    fs.writeFileSync(path.join(output, 'result.json'), JSON.stringify({ passed: true, browserErrors: errors, interceptedWrites: writes.length, checks: ['status and search filters', 'topic-to-ask navigation', 'guided creation', 'generated stable IDs', 'table deselection', 'primary key mapping', 'single-table default', 'dependent field reset', 'advanced configuration', 'save then sync', 'partial sync failure', 'scope conflict prevents sync', '390px overflow', 'dark theme', 'member navigation'] }, null, 2))
    console.log('PASS: frontend UX flows, mobile layouts, dark theme and failure handling. API writes were intercepted.')
  } finally { await browser.close() }
}
main().catch(error => { console.error(error); process.exitCode = 1 })
