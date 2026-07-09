import { Bot, GitBranch } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardAction } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { formatRelativeTime } from "@/lib/format"
import { cn } from "@/lib/utils"
import type { BuilderStatus } from "@/types/dashboard"

const STATE_STYLES: Record<BuilderStatus["state"], string> = {
  Active: "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400",
  Idle: "bg-muted text-muted-foreground",
  Blocked: "bg-amber-500/15 text-amber-600 dark:text-amber-400",
}

export function BuilderStatusCard({ status }: { status: BuilderStatus }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Bot className="size-4 text-muted-foreground" strokeWidth={2} />
          <CardTitle>Builder Status</CardTitle>
        </div>
        <CardAction>
          <Badge className={cn("hover:bg-inherit", STATE_STYLES[status.state])}>
            {status.state}
          </Badge>
        </CardAction>
      </CardHeader>
      <CardContent className="space-y-2">
        <p className="text-sm text-foreground">
          <span className="font-medium">{status.agent}</span>
          <span className="text-muted-foreground"> · {status.lastAction}</span>
        </p>
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <GitBranch className="size-3.5" />
            {status.branch}
          </span>
          <span>{formatRelativeTime(status.lastActionAt)}</span>
        </div>
      </CardContent>
    </Card>
  )
}
