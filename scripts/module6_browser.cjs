// Isolated M06 acceptance: local protocol replay, real synthetic PostgreSQL SQL.
const { chromium, expect } = require('@playwright/test')
const fs = require('node:fs')
const path = require('node:path')
const local = path.join(__dirname, '../.local')
const fixture = JSON.parse(fs.readFileSync(path.join(local, 'module5-fixture.json'), 'utf8'))

async function main() {
  const browser = await chromium.launch({ channel: 'msedge', headless: true })
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1100 } })
    const page = await context.newPage()
    const errors = []
    let asks = 0
    let executions = 0
    let streams = 0
    page.on('pageerror', (error) => errors.push(error.message))
    page.on('request', (request) => {
      if (request.method() === 'POST' && request.url().endsWith('/turns')) asks++
      if (request.method() === 'POST' && request.url().endsWith('/execute')) executions++
      if (request.url().endsWith('/events')) {
        streams++
        if (request.url().includes('token')) throw Error('Token in URL')
      }
    })
    await page.goto(fixture.url + '/login')
    await page.getByTestId('email-input').fill('admin@lightsql.example.com')
    await page.getByTestId('password-input').fill('LightSQL-Demo-2026!')
    await page.getByRole('button', { name: '登录工作空间' }).click()
    await page.waitForURL(/\/topics\/?$/)
    await page.goto(fixture.url + '/ask')
    await page.getByLabel('业务主题', { exact: true }).selectOption(fixture.topic_id)
    await page.getByRole('button', { name: '新建会话', exact: true }).click()
    await page.getByLabel('问答方式', { exact: true }).selectOption('metrics')
    await expect(page.getByText('进度实时同步', { exact: false })).toBeVisible()
    await page.getByLabel('你的业务问题', { exact: true }).fill('净销售额按客户区域分组')
    await page.getByRole('button', { name: '发送问题', exact: true }).click()
    const article = page.locator('article').last()
    await expect(article).toContainText('查询完成', { timeout: 25000 })
    await article.getByText('核对口径与来源', { exact: true }).click()
    await expect(article).toContainText('业务数据更新时间尚未提供')
    await expect(article).toContainText('m03_orders')
    await article.getByRole('button', { name: '评价回答', exact: true }).click()
    await article.getByLabel('评价', { exact: true }).selectOption('incorrect')
    await article.getByLabel('问题分类', { exact: true }).selectOption('filter')
    await article.getByLabel('反馈说明', { exact: true }).fill('M06复核：希望补充时间范围')
    await article.getByRole('button', { name: '保存反馈', exact: true }).click()
    await expect(article).toContainText('已记录：结果有问题')
    const restoredUrl = page.url()
    await page.reload()
    await expect(page.locator('article')).toContainText('已记录：结果有问题')
    await expect(page.locator('article')).toContainText('查询完成')
    await page.getByLabel('搜索历史会话', { exact: true }).fill('M06复核')
    await expect(page.locator('aside').filter({ has: page.getByRole('heading', { name: '最近会话' }) })).toContainText('已反馈')
    await page.getByLabel('搜索历史会话', { exact: true }).fill('不存在的问题 xyz')
    await expect(page.getByText('没有匹配的有效会话')).toBeVisible()
    await page.getByLabel('搜索历史会话', { exact: true }).fill('')
    await page.getByRole('button', { name: '修改反馈', exact: true }).click()
    await expect(page.getByLabel('反馈说明', { exact: true })).toHaveValue('M06复核：希望补充时间范围')
    await page.getByLabel('评价', { exact: true }).selectOption('helpful')
    await page.getByRole('button', { name: '保存反馈', exact: true }).click()
    await expect(page.locator('article')).toContainText('已记录：有帮助')
    const beforeReconnect = streams
    await context.setOffline(true)
    await page.waitForTimeout(2200)
    await context.setOffline(false)
    await expect.poll(() => streams, { timeout: 35000 }).toBeGreaterThan(beforeReconnect)
    await expect(page.getByText('进度实时同步', { exact: false })).toBeVisible({ timeout: 35000 })
    await page.getByText('核对口径与来源', { exact: true }).click()
    await expect(page.locator('article table')).toBeVisible()
    await expect(page.locator('article')).not.toContainText('完成时间：尚未完成', { timeout: 10000 })
    await page.evaluate(() => window.scrollTo(0, 0))
    await page.screenshot({ path: path.join(local, 'module6-workbench.png'), fullPage: true })
    if (asks !== 1 || executions !== 1) throw Error(`Repeated work: asks=${asks} executions=${executions}`)
    await page.getByLabel('问答方式', { exact: true }).selectOption('explore')
    await page.getByLabel('继续追问或补充条件', { exact: true }).fill('渠道统计退款金额')
    await page.getByRole('button', { name: '发送问题', exact: true }).click()
    await expect(page.locator('article').last()).toContainText('查询完成', { timeout: 25000 })
    await page.locator('article').last().getByText('核对口径与来源', { exact: true }).click()
    await expect(page.locator('article').last()).toContainText('未自动套用指标口径')
    await expect(page.locator('article').last().locator('table')).toBeVisible()
    await page.evaluate(() => window.scrollTo(0, 0))
    await page.screenshot({ path: path.join(local, 'module6-exploration.png'), fullPage: true })
    await page.setViewportSize({ width: 390, height: 844 })
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1)
    if (overflow) throw Error('Mobile page overflows')
    await page.screenshot({ path: path.join(local, 'module6-mobile.png'), fullPage: true })
    if (errors.length) throw Error(errors.join('\n'))
    fs.writeFileSync(path.join(local, 'module6-browser.json'), JSON.stringify({ restoredUrl, asks, executions, streams, errors, passed: true }, null, 2))
    console.log('M06 browser passed: evidence, feedback edit, history/search/reload, stream reconnect, no repeat query, SQL exploration, mobile layout.')
  } finally {
    await browser.close()
  }
}
main().catch((error) => { console.error(error); process.exitCode = 1 })

