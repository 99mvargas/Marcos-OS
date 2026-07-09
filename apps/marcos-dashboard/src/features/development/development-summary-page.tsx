import { Code2 } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const SECTIONS = [
  "Architecture",
  "Repository Philosophy",
  "Folder Organization",
  "Executive Pattern",
  "Provider Pattern",
  "Mock Data Rules",
  "UI Rules",
  "Build Rules",
  "Verification Rules",
  "Definition of Done",
  "Token Efficiency Rules",
]

export function DevelopmentSummaryPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-[15px] font-semibold tracking-tight">Development</h2>
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <Code2 className="size-4 text-muted-foreground" strokeWidth={2} />
            <CardTitle>DEVELOPMENT.md Summary</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground">
            Marcos OS is built one typed domain at a time: types first, mock
            data second, UI third, and a Provider implementing a real
            integration last. See <code className="text-xs">DEVELOPMENT.md</code>{" "}
            at the repository root for the full guide.
          </p>
          <div className="space-y-1.5">
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Sections
            </p>
            <ul className="list-inside list-disc space-y-0.5 text-sm text-foreground">
              {SECTIONS.map((section) => (
                <li key={section}>{section}</li>
              ))}
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
