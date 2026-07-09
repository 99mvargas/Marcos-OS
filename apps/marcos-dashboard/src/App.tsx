import { BrowserRouter, Routes, Route } from "react-router-dom"
import { Bot, Settings, Receipt } from "lucide-react"
import { AppShell } from "@/components/layout/app-shell"
import { HomePage } from "@/features/home/home-page"
import { FinancePage } from "@/features/finance/finance-page"
import { StatementVaultPage } from "@/features/finance/statement-vault/statement-vault-page"
import { DevelopmentSummaryPage } from "@/features/development/development-summary-page"
import { CapturePage } from "@/features/capture/capture-page"
import { ComingSoon } from "@/features/placeholder/coming-soon"

function App() {
  return (
    <BrowserRouter>
      <AppShell>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/finance" element={<FinancePage />} />
          <Route path="/finance/statement-vault" element={<StatementVaultPage />} />
          <Route
            path="/finance/receipts"
            element={
              <ComingSoon
                icon={Receipt}
                title="Receipts"
                description="Receipt capture and tracking is landing in a future screen."
              />
            }
          />
          <Route path="/development" element={<DevelopmentSummaryPage />} />
          <Route path="/capture" element={<CapturePage />} />
          <Route
            path="/ai"
            element={
              <ComingSoon
                icon={Bot}
                title="AI Employees"
                description="Engineering, Business, Finance, Home, and Health — coming soon."
              />
            }
          />
          <Route
            path="/system"
            element={
              <ComingSoon
                icon={Settings}
                title="System"
                description="Builder VM, Docker, and Git status are coming soon."
              />
            }
          />
        </Routes>
      </AppShell>
    </BrowserRouter>
  )
}

export default App
