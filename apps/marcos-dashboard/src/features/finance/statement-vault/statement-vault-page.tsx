import { useEffect, useRef, useState } from "react"
import type { ChangeEvent } from "react"
import { Upload, FileText } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardAction } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { listStatements, uploadStatement } from "@/api/statements"
import type { StatementType } from "@/types/finance"

const STATEMENT_TYPE_LABELS: Record<StatementType, string> = {
  "credit-card": "Credit Card",
  checking: "Checking",
  savings: "Savings",
  investment: "Investment",
  mortgage: "Mortgage",
  loan: "Loan",
}

const SUPPORTED_TYPES: StatementType[] = [
  "credit-card",
  "checking",
  "savings",
  "investment",
  "mortgage",
  "loan",
]

export function StatementVaultPage() {
  const [filenames, setFilenames] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  async function refresh() {
    try {
      const files = await listStatements()
      setFilenames(files)
      setError(null)
    } catch {
      setError("Could not reach marcos-api. Is it running on :8420?")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  async function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    event.target.value = ""
    if (!file) return

    setUploading(true)
    try {
      await uploadStatement(file)
      await refresh()
    } catch {
      setError("Upload failed. Is marcos-api running on :8420?")
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="space-y-6">
      <h2 className="text-[15px] font-semibold tracking-tight">Statement Vault</h2>

      <Card>
        <CardHeader>
          <CardTitle>Upload Statement</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-border p-6 text-center">
            <Upload className="size-5 text-muted-foreground" strokeWidth={2} />
            <p className="text-sm text-muted-foreground">
              {uploading ? "Uploading…" : "Upload a PDF statement to the vault."}
            </p>
            <input
              ref={inputRef}
              type="file"
              accept="application/pdf"
              className="sr-only"
              onChange={handleFileChange}
            />
            <Button
              size="sm"
              variant="outline"
              disabled={uploading}
              onClick={() => inputRef.current?.click()}
            >
              {uploading ? "Uploading…" : "Choose File"}
            </Button>
          </div>
          {error && <p className="text-xs text-destructive">{error}</p>}
          <div className="space-y-1.5">
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Supported Types
            </p>
            <div className="flex flex-wrap gap-1.5">
              {SUPPORTED_TYPES.map((type) => (
                <Badge key={type} variant="outline">
                  {STATEMENT_TYPE_LABELS[type]}
                </Badge>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recent Statements</CardTitle>
          <CardAction>
            <Badge variant="secondary">{filenames.length}</Badge>
          </CardAction>
        </CardHeader>
        <CardContent className="space-y-1">
          {loading ? (
            <p className="text-sm text-muted-foreground">Loading…</p>
          ) : filenames.length === 0 ? (
            <p className="text-sm text-muted-foreground">No statements uploaded yet.</p>
          ) : (
            filenames.map((filename) => (
              <div
                key={filename}
                className="flex items-center gap-3 rounded-lg px-1 py-2 first:pt-0 last:pb-0"
              >
                <span className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-accent">
                  <FileText className="size-4 text-accent-foreground" strokeWidth={2} />
                </span>
                <div className="min-w-0 flex-1 space-y-0.5">
                  <p className="truncate text-sm font-medium text-foreground">{filename}</p>
                </div>
                <Badge variant="secondary" className="shrink-0">
                  Stored
                </Badge>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  )
}
