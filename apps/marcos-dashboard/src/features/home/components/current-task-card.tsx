import { ListTodo } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { formatRelativeTime } from "@/lib/format"
import type { CurrentTask } from "@/types/dashboard"

export function CurrentTaskCard({ task }: { task: CurrentTask }) {
  return (
    <Card>
      <CardContent className="flex items-start gap-3">
        <div className="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-lg bg-accent">
          <ListTodo className="size-4.5 text-accent-foreground" strokeWidth={2} />
        </div>
        <div className="min-w-0 flex-1 space-y-0.5">
          <div className="flex items-center gap-1.5">
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Current Task
            </p>
            <span className="relative flex size-1.5">
              <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-500/60" />
              <span className="relative inline-flex size-1.5 rounded-full bg-emerald-500" />
            </span>
          </div>
          <p className="truncate text-[15px] font-semibold text-foreground">{task.title}</p>
          <p className="line-clamp-2 text-sm text-muted-foreground">{task.detail}</p>
          <p className="pt-0.5 text-xs text-muted-foreground/80">
            Started {formatRelativeTime(task.startedAt)}
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
