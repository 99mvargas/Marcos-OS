import { Link } from "react-router-dom"
import { ArrowRight, ExternalLink } from "lucide-react"
import type { LucideIcon } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

type ActionCardProps = {
  icon: LucideIcon
  label: string
  description: string
} & ({ to: string; href?: undefined } | { href: string; to?: undefined })

export function ActionCard({ icon: Icon, label, description, to, href }: ActionCardProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Icon className="size-4 text-muted-foreground" strokeWidth={2} />
          <CardTitle>{label}</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-muted-foreground">{description}</p>
        {href ? (
          <Button
            size="sm"
            variant="outline"
            className="w-full"
            render={<a href={href} target="_blank" rel="noopener noreferrer" />}
          >
            Open
            <ExternalLink className="size-3.5" />
          </Button>
        ) : (
          <Button size="sm" variant="outline" className="w-full" render={<Link to={to!} />}>
            Go
            <ArrowRight className="size-3.5" />
          </Button>
        )}
      </CardContent>
    </Card>
  )
}
