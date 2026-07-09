const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? `${window.location.protocol}//${window.location.hostname}:8420`

export type CaptureCategory = "ideas" | "receipts" | "statements" | "photos"

export type CaptureItem = {
  filename: string
  category: CaptureCategory
  uploadedAt: string
}

export async function uploadCapture(category: CaptureCategory, file: File): Promise<void> {
  const formData = new FormData()
  formData.append("file", file)
  const response = await fetch(`${API_BASE_URL}/captures/${category}`, {
    method: "POST",
    body: formData,
  })
  if (!response.ok) {
    throw new Error(`Upload failed: ${response.status}`)
  }
}

type RawCaptureItem = {
  filename: string
  category: CaptureCategory
  uploaded_at: string
}

export async function listRecentCaptures(): Promise<CaptureItem[]> {
  const response = await fetch(`${API_BASE_URL}/captures`)
  if (!response.ok) {
    throw new Error(`Failed to load captures: ${response.status}`)
  }
  const data: { items: RawCaptureItem[] } = await response.json()
  return data.items.map((item) => ({
    filename: item.filename,
    category: item.category,
    uploadedAt: item.uploaded_at,
  }))
}
