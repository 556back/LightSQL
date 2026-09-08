// Local fixed-response protocol replay, no model requests or configuration edits.
const { chromium, expect } = require('@playwright/test')
const fs = require('node:fs')
const path = require('node:path')
const local = path.join(__dirname, '../.local')
const fixture = JSON.parse(fs.readFileSync(path.join(local, 'module5-fixture.json'), 'utf8'))

async function main() {
  const browser = await chromium.launch({ channel: 'msedge', headless: true })
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } })
  const errors = []
  page.on('pageerror', error => errors.push(error.message))
  await page.goto(`${fixture.url}/login`)
  await page.getByTestId('email-input').fill('admin@lightsql.example.com')
  await page.getByTestId('password-input').fill('LightSQL-Demo-2026!')
  await page.getByRole('button', { name: '登录工作空间' }).click()
  await page.waitForURL(/\/topics\/?$/)
  await page.goto(`${fixture.url}/ask`)
  await page.getByLabel('业务主题', { exact: true }).selectOption(fixture.topic_id)
  await page.getByRole('button', { name: '新建会话', exact: true }).click()
  await page.getByLabel('问答方式', { exact: true }).selectOption('explore')
  const questions = ['我想看看订单明细，按日期倒序列出最近五笔。', '改成按渠道统计订单数和退款金额，画柱状图，并给我一些分析建议。', '按日期统计退款金额，并计算上一个有订单日期的退款金额，画折线图。']
  for (const [i, question] of questions.entries()) {
    await page.locator('#ask-question').fill(question)
    await page.getByRole('button', {name: '发送问题', exact: true}).click()
    const article = page.locator('article').last()
    await expect(article).toContainText(question)
    await expect(article.getByRole('table')).toBeVisible({ timeout: 45000 })
    if (i === 0) await expect(article.getByRole('row')).toHaveCount(6)
    if (i === 1) {
      await expect(article.getByRole('img', {name: /柱状图/})).toBeVisible()
      await expect(article).toContainText('本次返回行数', {timeout: 15000})
      await expect(article).toContainText('依据：')
      await expect(article.getByRole('cell', {name:'300.00',exact:true})).toBeVisible()
      await article.getByLabel('图表数值').selectOption({label:'退款金额'})
    }
    if (i === 2) {
      await expect(article.getByRole('img', {name:/折线图/})).toBeVisible()
      await expect(article.getByRole('cell', {name:'NULL',exact:true})).toBeVisible()
    }
    await article.scrollIntoViewIfNeeded()
    await page.screenshot({path:path.join(local, `module5-explore-${i}.png`)})
  }
  await page.setViewportSize({width:390,height:844})
  await expect(page.locator('article').last().getByRole('img')).toBeVisible()
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth)
  if (overflow) throw Error('Mobile page overflows')
  await page.screenshot({path:path.join(local,'module5-explore-mobile.png')})
  if (errors.length) throw Error(errors.join('\n'))
  fs.writeFileSync(path.join(local,'module5-explore-browser.json'), JSON.stringify({local_protocol_replay:true,actual_llm:false,auto_query:true,detail_rows:5,bar_chart:true,line_chart:true,analysis_evidence:true,mobile_no_overflow:true},null,2))
  await browser.close()
  console.log('Local replay + actual synthetic PostgreSQL queries: detail, charts, analysis, mobile passed.')
}
main().catch(error => { console.error(error); process.exit(1) })
