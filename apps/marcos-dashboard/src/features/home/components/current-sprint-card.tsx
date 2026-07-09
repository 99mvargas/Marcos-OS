import { Card, CardContent, CardHeader, CardTitle, CardAction } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import type { SprintSummary } from "@/types/dashboard"

export function CurrentSprintCard({ sprint }: { sprint: SprintSummary }) {
  return (
    <Card className="border-0 bg-gradient-to-br from-violet-600 to-indigo-700 text-white shadow-lg shadow-violet-950/20 ring-0">
      <CardHeader>
        <p className="text-xs font-medium uppercase tracking-wider text-white/70">
          Sprint {sprint.number}
        </p>
        <CardTitle className="text-lg font-semibold text-white">{sprint.name}</CardTitle>
        <CardAction>
          <Badge className="bg-white/15 text-white hover:bg-white/15">{sprint.status}</Badge>
        </CardAction>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm leading-relaxed text-white/80">{sprint.description}</p>
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs text-white/70">
            <span>Progress</span>
            <span className="font-medium text-white">{sprint.progress}%</span>
          </div>
          <Progress
            value={sprint.progress}
            className="[&_[data-slot=progress-indicator]]:bg-white [&_[data-slot=progress-track]]:h-1.5 [&_[data-slot=progress-track]]:bg-white/20"
          />
        </div>
      </CardContent>
    </Card>
  )
}
