import { Appearance } from "@/components/Common/Appearance"
import { DataSpectrum } from "@/components/Common/DataSpectrum"
import { Logo } from "@/components/Common/Logo"
import { Footer } from "./Footer"

interface AuthLayoutProps {
  children: React.ReactNode
}

export function AuthLayout({ children }: AuthLayoutProps) {
  return (
    <div className="grid min-h-svh lg:grid-cols-[1.05fr_1fr]">
      <div className="auth-story relative hidden overflow-hidden p-12 lg:flex lg:flex-col xl:p-16">
        <Logo
          variant="full"
          className="text-sidebar-foreground"
          asLink={false}
        />
        <div className="my-auto py-12">
          <p className="mb-5 text-xs tracking-[0.18em] text-sidebar-primary">
            从数据，到洞察
          </p>
          <h2 className="auth-display">
            每一个好问题，
            <br />
            都值得一个
            <br />
            <span className="text-sidebar-primary">清晰的答案。</span>
          </h2>
          <p className="mt-6 max-w-sm text-sm leading-7 text-sidebar-foreground/75">
            连接业务数据，用熟悉的语言探索。
            <br />
            让数字背后的线索，成为下一步的方向。
          </p>
          <DataSpectrum />
        </div>
        <p className="text-xs text-sidebar-foreground/70">
          LightSQL · 企业数据工作台
        </p>
      </div>
      <div className="flex flex-col gap-4 p-6 md:p-10">
        <div className="flex items-center justify-between">
          <Logo className="lg:invisible" />
          <Appearance />
        </div>
        <div className="flex flex-1 items-center justify-center">
          <div className="auth-form w-full max-w-sm">{children}</div>
        </div>
        <Footer />
      </div>
    </div>
  )
}
