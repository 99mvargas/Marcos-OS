export type ServiceIconId = "home" | "box" | "clapperboard"

export interface ServiceDefinition {
  id: string
  name: string
  description: string
  url: string
  icon: ServiceIconId
  status: "online"
}

export const SERVICE_REGISTRY: ServiceDefinition[] = [
  {
    id: "home-assistant",
    name: "Home Assistant",
    description: "Smart home automation hub",
    url: "http://10.0.0.145:8123",
    icon: "home",
    status: "online",
  },
  {
    id: "portainer",
    name: "Portainer",
    description: "Docker container management",
    url: "http://10.0.0.47:9000",
    icon: "box",
    status: "online",
  },
  {
    id: "jellyfin",
    name: "Jellyfin",
    description: "Media server",
    url: "http://10.0.0.47:8096",
    icon: "clapperboard",
    status: "online",
  },
]
