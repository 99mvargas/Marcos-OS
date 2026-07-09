import { Upload, Lightbulb, Home, Clapperboard, Code2, Receipt } from "lucide-react"
import { ActionCard } from "@/features/home/components/action-card"
import { SERVICE_REGISTRY } from "@/data/service-registry"

const homeAssistant = SERVICE_REGISTRY.find((service) => service.id === "home-assistant")!
const jellyfin = SERVICE_REGISTRY.find((service) => service.id === "jellyfin")!

export function ActionCenter() {
  return (
    <div>
      <h2 className="mb-2.5 text-[15px] font-semibold tracking-tight">Action Center</h2>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <ActionCard
          icon={Upload}
          label="Upload Statement"
          description="Add a new financial statement to the Statement Vault."
          to="/finance/statement-vault"
        />
        <ActionCard
          icon={Lightbulb}
          label="Capture Idea"
          description="Quickly capture a thought before it's gone."
          to="/capture"
        />
        <ActionCard
          icon={Home}
          label="Open Home Assistant"
          description="Jump to your smart home dashboard."
          href={homeAssistant.url}
        />
        <ActionCard
          icon={Clapperboard}
          label="Open Jellyfin"
          description="Jump to your media server."
          href={jellyfin.url}
        />
        <ActionCard
          icon={Code2}
          label="Continue Development"
          description="See what's being built right now."
          to="/development"
        />
        <ActionCard
          icon={Receipt}
          label="Upload Receipt"
          description="Add a receipt to track a purchase."
          to="/finance/receipts"
        />
      </div>
    </div>
  )
}
