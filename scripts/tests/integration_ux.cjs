// Real login and static assets; integration fixtures are intercepted in-browser.
// No business records or model calls are created by this UI regression.
const { chromium, expect } = require('@playwright/test')
const fs = require('node:fs')
const path = require('node:path')
const root = path.resolve(__dirname, '../..')
const env = Object.fromEntries(fs.readFileSync(path.join(root, '.local/startup.env'), 'utf8').trim().split(/\r?\n/).map(line => {
  const i = line.indexOf('='); return [line.slice(0, i), line.slice(i + 1)]
}))
const origin = `http://localhost:${env.LIGHTSQL_PORT || 18000}`
async function main() {
  const browser = await chromium.launch({ channel: 'msedge', headless: true })
  try {
    const page = await browser.newPage({ viewport: { width: 1366, height: 960 } })
    const errors = []
    page.on('pageerror', e => errors.push(e.message))
    await page.goto(origin + '/login')
    await page.getByTestId('email-input').fill(env.FIRST_SUPERUSER)
    await page.getByTestId('password-input').fill(env.FIRST_SUPERUSER_PASSWORD)
    await page.getByRole('button', { name: '登录工作空间' }).click()
    await expect(page.getByRole('link', { name: '外部系统接入', exact: true })).toBeVisible({ timeout: 15000 })
    const member = { id: '11111111-1111-4111-8111-111111111111', email: 'member@example.com', is_active: true, is_superuser: false }
    const topic = { id: '22222222-2222-4222-8222-222222222222', name: '销售经营' }
    let clients = []
    let submitted
    let rotations = 0
    await page.route('**/api/v1/users/?*', r => r.fulfill({ json: { data: [member], count: 1 } }))
    await page.route('**/api/v1/topics/', r => r.fulfill({ json: [topic] }))
    await page.route('**/api/v1/integrations/**', async r => {
      const request = r.request(), url = new URL(request.url()), method = request.method()
      if (url.pathname.endsWith('/check')) return r.fulfill({ json: { ok: true, topics: [{ topic_id: topic.id, name: topic.name, ok: true, message: '已发布 v1，可用指标 1 项、维度 2 项' }], warnings: [] } })
      if (url.pathname.endsWith('/rotate-secret')) { rotations++; return r.fulfill({ json: { client_secret: 'rotated-test-secret', revision: 2 } }) }
      if (url.pathname.endsWith('/identities')) return r.fulfill({ json: [{ subject: '$app', user_id: member.id, enabled: true }] })
      if (url.pathname.endsWith('/audit')) return r.fulfill({ json: [] })
      if (method === 'POST') {
        submitted = request.postDataJSON()
        const record = { ...submitted, id: '33333333-3333-4333-8333-333333333333', revision: 1 }
        clients = [record]
        return r.fulfill({ status: 201, json: { ...record, client_secret: 'one-time-fixture-secret' } })
      }
      return r.fulfill({ json: clients })
    })
    await page.getByRole('link', { name: '外部系统接入', exact: true }).click()
    await page.getByRole('button', { name: '检查接入配置', exact: true }).click()
    await expect(page.getByRole('alert')).toHaveText('请填写应用名称')
    await page.getByLabel('应用名称', { exact: true }).fill('ERP 接入测试')
    await page.getByLabel('权限上限用户').selectOption(member.id)
    await page.getByLabel(topic.name, { exact: true }).check()
    const origins = page.getByPlaceholder('https://erp.example.com')
    await origins.fill('https://erp.example.com/path')
    await page.getByRole('button', { name: '检查接入配置', exact: true }).click()
    await expect(page.getByRole('alert')).toContainText('不含路径')
    await origins.fill('https://erp.example.com/, https://erp.example.com')
    await page.getByRole('button', { name: '检查接入配置', exact: true }).click()
    await expect(page.getByRole('heading', { name: '配置检查通过' })).toBeVisible()
    await page.getByLabel('应用名称', { exact: true }).fill('ERP 接入')
    await expect(page.getByRole('heading', { name: '配置检查通过' })).toHaveCount(0)
    await page.getByRole('button', { name: '保存应用', exact: true }).click()
    await expect(page.getByText('one-time-fixture-secret', { exact: true })).toBeVisible()
    expect(submitted.origins).toEqual(['https://erp.example.com'])
    await expect(page.getByLabel('权限上限用户')).toBeDisabled()
    await expect(page.getByText('$app →', { exact: false })).toBeVisible()
    await page.getByRole('button', { name: '已保存，隐藏密钥' }).click()
    await expect(page.getByText('one-time-fixture-secret', { exact: true })).toHaveCount(0)
    await page.getByRole('button', { name: '嵌入页面', exact: true }).click()
    await expect(page.locator('pre').filter({ hasText: 'LightSQL.mount' })).toContainText(clients[0].id)
    page.once('dialog', d => d.dismiss())
    await page.getByRole('button', { name: '轮换应用密钥', exact: true }).click()
    expect(rotations).toBe(0)
    await page.getByLabel('应用名称', { exact: true }).fill('尚未保存')
    page.once('dialog', d => d.dismiss())
    await page.getByRole('button', { name: '新应用', exact: true }).click()
    await expect(page.getByLabel('应用名称', { exact: true })).toHaveValue('尚未保存')
    await page.getByLabel('应用名称', { exact: true }).fill('ERP 接入')
    await page.screenshot({ path: path.join(root, '.local/integration-ux-desktop.png'), fullPage: true })
    await page.setViewportSize({ width: 390, height: 844 })
    await expect.poll(() => page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true)
    await page.screenshot({ path: path.join(root, '.local/integration-ux-mobile.png'), fullPage: true })
    expect(errors).toEqual([])
    console.log('PASS: real login; validation; origin normalization; check invalidation; create and secret; guide; rotation cancellation; unsaved edits; mobile overflow; no page errors.')
  } finally { await browser.close() }
}
main().catch(e => { console.error(e); process.exitCode = 1 })
