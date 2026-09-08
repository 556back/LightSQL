import { Link } from "@tanstack/react-router"
import { Button } from "@/components/ui/button"

const NotFound = () => {
  return (
    <div
      className="flex min-h-[60vh] items-center justify-center flex-col p-4"
      data-testid="not-found"
    >
      <div className="flex items-center z-10">
        <div className="flex flex-col ml-4 items-center justify-center p-4">
          <span className="text-6xl md:text-8xl font-bold leading-none mb-4">
            404
          </span>
          <h1 className="page-title">没有找到这个页面</h1>
        </div>
      </div>

      <p className="text-lg text-muted-foreground mb-4 text-center z-10">
        页面可能已移动，请检查地址，或返回工作空间。
      </p>
      <div className="z-10">
        <Button className="mt-4" asChild>
          <Link to="/">返回工作空间</Link>
        </Button>
      </div>
    </div>
  )
}

export default NotFound
