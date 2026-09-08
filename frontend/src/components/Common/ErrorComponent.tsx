import { Link } from "@tanstack/react-router"
import { Button } from "@/components/ui/button"

const ErrorComponent = () => {
  return (
    <div
      className="flex min-h-[60vh] items-center justify-center flex-col p-4"
      data-testid="error-component"
    >
      <div className="flex items-center z-10">
        <div className="flex flex-col ml-4 items-center justify-center p-4">
          <span className="text-6xl md:text-8xl font-bold leading-none mb-4">
            —
          </span>
          <h1 className="page-title">页面暂时无法加载</h1>
        </div>
      </div>

      <p className="text-lg text-muted-foreground mb-4 text-center z-10">
        请刷新页面重试，或返回工作空间继续操作。
      </p>
      <Button asChild>
        <Link to="/">返回工作空间</Link>
      </Button>
    </div>
  )
}

export default ErrorComponent
