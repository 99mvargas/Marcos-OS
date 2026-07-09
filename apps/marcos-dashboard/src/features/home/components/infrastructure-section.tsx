import { Home, Box, Clapperboard, ExternalLink } from "lucide-react"
import type { LucideIcon } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle, CardAction } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { SERVICE_REGISTRY, type ServiceIconId } from "@/data/service-registry"

const ICONS: Record<ServiceIconId, LucideIcon> = {
  home: Home,
  box: Box,
  clapperboard: Clapperboard,
}

export function InfrastructureSection() {
  return (
    <div>
      <h2 className="mb-2.5 text-[15px] font-semibold tracking-tight">Infrastructure</h2>
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {SERVICE_REGISTRY.map((service) => {
          const Icon = ICONS[service.icon]
          return (
            <Card key={service.id}>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Icon className="size-4 text-muted-foreground" strokeWidth={2} />
                  <CardTitle>{service.name}</CardTitle>
                </div>
                <CardAction>
                  <Badge className="bg-emerald-500/15 text-emerald-600 hover:bg-inherit dark:text-emerald-400">
                    {service.status === "online" ? "Online" : service.status}
                  </Badge>
                </CardAction>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-muted-foreground">{service.description}</p>
                <Button
                  size="sm"
                  variant="outline"
                  className="w-full"
                  render={
                    <a href={service.url} target="_blank" rel="noopener noreferrer" />
                  }
                >
                  Open
                  <ExternalLink className="size-3.5" />
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
