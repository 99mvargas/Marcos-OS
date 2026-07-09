import { useEffect, useState } from "react"
import { Lightbulb, Receipt, FileText, Camera } from "lucide-react"
import type { LucideIcon } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { formatRelativeTime } from "@/lib/format"
import { listRecentCaptures } from "@/api/captures"
import type { CaptureCategory, CaptureItem } from "@/api/captures"

const CATEGORY_ICON: Record<CaptureCategory, LucideIcon> = {
  ideas: Lightbulb,
  receipts: Receipt,
  statements: FileText,
  photos: Camera,
}

const CATEGORY_LABEL: Record<CaptureCategory, string> = {
  ideas: "Idea",
  receipts: "Receipt",
  statements: "Statement",
  photos: "Photo",
}

export function RecentUploads() {
  const [items, setItems] = useState<CaptureItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    listRecentCaptures()
      .then((data) => {
        if (!cancelled) setItems(data)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Uploads</CardTitle>
      </CardHeader>
      <CardContent className="space-y-1">
        {loading ? (
          <p className="text-sm text-muted-foreground">Loading…</p>
        ) : items.length === 0 ? (
          <p className="text-sm text-muted-foreground">Nothing captured yet.</p>
        ) : (
          items.map((item) => {
            const Icon = CATEGORY_ICON[item.category]
            return (
              <div
                key={`${item.category}/${item.filename}`}
                className="flex items-center gap-3 rounded-lg px-1 py-2 first:pt-0 last:pb-0"
              >
                <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-accent">
                  <Icon className="size-4 text-accent-foreground" strokeWidth={2} />
                </span>
                <div className="min-w-0 flex-1 space-y-0.5">
                  <p className="truncate text-sm font-medium text-foreground">{item.filename}</p>
                  <p className="text-xs text-muted-foreground">{formatRelativeTime(item.uploadedAt)}</p>
                </div>
                <Badge variant="secondary" className="shrink-0">
                  {CATEGORY_LABEL[item.category]}
                </Badge>
              </div>
            )
          })
        )}
      </CardContent>
    </Card>
  )
}
