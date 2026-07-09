const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? `${window.location.protocol}//${window.location.hostname}:8420`

export type UploadedStatement = {
  filename: string
  status: string
}

export async function uploadStatement(file: File): Promise<UploadedStatement> {
  const formData = new FormData()
  formData.append("file", file)
  const response = await fetch(`${API_BASE_URL}/statements`, {
    method: "POST",
    body: formData,
  })
  if (!response.ok) {
    throw new Error(`Upload failed: ${response.status}`)
  }
  return response.json()
}

export async function listStatements(): Promise<string[]> {
  const response = await fetch(`${API_BASE_URL}/statements`)
  if (!response.ok) {
    throw new Error(`Failed to load statements: ${response.status}`)
  }
  const data: { filenames: string[] } = await response.json()
  return data.filenames
}
