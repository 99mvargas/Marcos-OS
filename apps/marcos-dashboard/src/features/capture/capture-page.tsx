import { useRef, useState } from "react"
import type { ChangeEvent } from "react"
import { Lightbulb, Receipt, FileText, Camera, Check } from "lucide-react"
import type { LucideIcon } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { uploadCapture } from "@/api/captures"
import type { CaptureCategory } from "@/api/captures"

type CaptureMode = "text" | "photo" | "pdf"

type CategoryDef = {
  id: CaptureCategory
  label: string
  icon: LucideIcon
  description: string
  mode: CaptureMode
}

const CATEGORIES: CategoryDef[] = [
  { id: "ideas", label: "Idea", icon: Lightbulb, description: "Quick text note.", mode: "text" },
  { id: "receipts", label: "Receipt", icon: Receipt, description: "Photo of a receipt.", mode: "photo" },
  { id: "statements", label: "Statement", icon: FileText, description: "PDF statement.", mode: "pdf" },
  { id: "photos", label: "Photo", icon: Camera, description: "General photo.", mode: "photo" },
]

type Status =
  | { kind: "idle" }
  | { kind: "uploading" }
  | { kind: "success" }
  | { kind: "error"; message: string }

export function CapturePage() {
  const [category, setCategory] = useState<CategoryDef>(CATEGORIES[0])
  const [text, setText] = useState("")
  const [status, setStatus] = useState<Status>({ kind: "idle" })
  const fileInputRef = useRef<HTMLInputElement>(null)

  function selectCategory(next: CategoryDef) {
    setCategory(next)
    setStatus({ kind: "idle" })
  }

  async function submitFile(file: File) {
    setStatus({ kind: "uploading" })
    try {
      await uploadCapture(category.id, file)
      setStatus({ kind: "success" })
    } catch {
      setStatus({ kind: "error", message: "Upload failed. Is marcos-api reachable?" })
    }
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    event.target.value = ""
    if (file) submitFile(file)
  }

  async function handleSaveIdea() {
    const trimmed = text.trim()
    if (!trimmed) return
    const file = new File([trimmed], `idea-${Date.now()}.txt`, { type: "text/plain" })
    await submitFile(file)
    setText("")
  }

  return (
    <div className="space-y-6">
      <h2 className="text-[15px] font-semibold tracking-tight">Capture</h2>

      <div className="grid grid-cols-4 gap-2">
        {CATEGORIES.map((c) => (
          <button
            key={c.id}
            type="button"
            onClick={() => selectCategory(c)}
            className={cn(
              "flex flex-col items-center gap-1.5 rounded-xl border p-3 text-xs font-medium transition-colors",
              category.id === c.id
                ? "border-primary bg-primary/10 text-primary"
                : "border-border text-muted-foreground hover:bg-muted",
            )}
          >
            <c.icon className="size-5" strokeWidth={2} />
            {c.label}
          </button>
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{category.label}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">{category.description}</p>

          {category.mode === "text" ? (
            <div className="space-y-3">
              <textarea
                value={text}
                onChange={(event) => setText(event.target.value)}
                rows={5}
                placeholder="Type your idea…"
                className="w-full resize-none rounded-lg border border-border bg-background p-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
              />
              <Button
                size="sm"
                className="w-full"
                disabled={!text.trim() || status.kind === "uploading"}
                onClick={handleSaveIdea}
              >
                {status.kind === "uploading" ? "Saving…" : "Save Idea"}
              </Button>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-border p-6 text-center">
              <category.icon className="size-5 text-muted-foreground" strokeWidth={2} />
              <input
                ref={fileInputRef}
                type="file"
                accept={category.mode === "pdf" ? "application/pdf" : "image/*"}
                capture={category.mode === "photo" ? "environment" : undefined}
                className="sr-only"
                onChange={handleFileChange}
              />
              <Button
                size="sm"
                variant="outline"
                disabled={status.kind === "uploading"}
                onClick={() => fileInputRef.current?.click()}
              >
                {status.kind === "uploading"
                  ? "Uploading…"
                  : category.mode === "photo"
                    ? "Take / Choose Photo"
                    : "Choose PDF"}
              </Button>
            </div>
          )}

          {status.kind === "success" && (
            <p className="flex items-center gap-1.5 text-xs font-medium text-emerald-600 dark:text-emerald-400">
              <Check className="size-3.5" strokeWidth={2.5} />
              Saved to {category.label}.
            </p>
          )}
          {status.kind === "error" && <p className="text-xs text-destructive">{status.message}</p>}
        </CardContent>
      </Card>
    </div>
  )
}
