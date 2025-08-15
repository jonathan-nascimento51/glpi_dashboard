import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  AlertCircle, 
  CheckCircle, 
  Clock, 
  XCircle,
  type LucideIcon 
} from "lucide-react"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Formatacao de numeros para padrao brasileiro
export function formatNumber(value: number): string {
  return new Intl.NumberFormat('pt-BR').format(value)
}

// Formatacao de porcentagem
export function formatPercentage(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value / 100)
}

// Cores baseadas no status
export function getStatusColor(status: string): string {
  const colors = {
    new: "text-blue-600 bg-blue-50 border-blue-200",
    progress: "text-yellow-600 bg-yellow-50 border-yellow-200",
    pending: "text-orange-600 bg-orange-50 border-orange-200",
    resolved: "text-green-600 bg-green-50 border-green-200",
    online: "text-green-600 bg-green-50 border-green-200",
    offline: "text-red-600 bg-red-50 border-red-200",
    maintenance: "text-yellow-600 bg-yellow-50 border-yellow-200"
  }
  return colors[status as keyof typeof colors] || "text-gray-600 bg-gray-50 border-gray-200"
}

// icones baseados no status
export function getStatusIcon(status: string): LucideIcon {
  const icons = {
    new: AlertCircle,
    progress: Clock,
    pending: Clock,
    resolved: CheckCircle,
    online: CheckCircle,
    offline: XCircle,
    maintenance: AlertCircle
  }
  return icons[status as keyof typeof icons] || AlertCircle
}

// icones de tendencia
export function getTrendIcon(trend: string): LucideIcon {
  switch (trend) {
    case 'up':
    case 'increase':
      return TrendingUp
    case 'down':
    case 'decrease':
      return TrendingDown
    default:
      return Minus
  }
}

// Cores de tendencia
export function getTrendColor(trend: string): string {
  switch (trend) {
    case 'up':
    case 'increase':
      return "text-green-600"
    case 'down':
    case 'decrease':
      return "text-red-600"
    default:
      return "text-gray-600"
  }
}

// Formatacao de data relativa
export function formatRelativeTime(date: string | Date): string {
  const now = new Date()
  const target = new Date(date)
  const diffInSeconds = Math.floor((now.getTime() - target.getTime()) / 1000)
  
  if (diffInSeconds < 60) return 'Agora mesmo'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m atras`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h atras`
  return `${Math.floor(diffInSeconds / 86400)}d atras`
}
