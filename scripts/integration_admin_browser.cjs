const { chromium, expect } = require('@playwright/test')
const path = require('node:path')
async function main() {
  const browser = await chromium.launch({channel:'msedge',headless:true})
  try {
    const page = await browser.newPage({ viewport:{width:1280,height:1000} })
    const errors=[]
    page.on('pageerror', e=>errors.push(e.message))
    await page.goto('http://127.0.0.1:8000/login')
    await page.getByTestId('email-input').fill('admin@lightsql.example.com')
    await page.getByTestId('password-input').fill('LightSQL-Demo-2026!')
    await page.getByRole('button',{name:'登录工作空间'}).click()
    await expect(page.getByRole('link',{name:'外部系统接入',exact:true})).toBeVisible({timeout:15000})
    await page.getByRole('link',{name:'外部系统接入',exact:true}).click()
    await expect(page.getByRole('heading',{name:'外部系统接入',exact:true})).toBeVisible()
    await expect(page.getByLabel('权限上限用户')).toBeVisible()
    await expect.poll(()=>page.getByLabel('权限上限用户').locator('option').count()).toBeGreaterThan(1)
    await page.screenshot({path:path.join(__dirname,'../.local/integration-admin.png'),fullPage:true})
    const health=await page.request.get('http://127.0.0.1:8000/api/v1/utils/health-check/')
    if(!health.ok())throw Error('API health failed')
    const schema=await page.request.get('http://127.0.0.1:8000/api/integration/v1/openapi.json')
    if(!(await schema.json()).paths['/api/integration/v1/answers'])throw Error('Public schema missing')
    if(errors.length)throw Error(errors.join('\n'))
    console.log('Local API health, public OpenAPI and integration administration browser checks passed.')
  } finally {await browser.close()}
}
main().catch(e=>{console.error(e);process.exit(1)})
