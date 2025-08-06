import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { 
  AlertCircle, 
  Clock, 
  User, 
  Calendar,
  RefreshCw,
  ExternalLink
} from "lucide-react"
import { NewTicket } from "@/types"
import { cn, formatRelativeTime } from "@/lib/utils"
import { apiService } from "@/services/api"

interface NewTicketsListProps {
  className?: string
  limit?: number
}

const priorityConfig = {
  'Alta': {
    color: 'bg-slate-100 text-slate-800 border-slate-200',
    icon: '🔴'
  },
  'Média': {
    color: 'bg-slate-100 text-slate-700 border-slate-200',
    icon: '🟡'
  },
  'Baixa': {
    color: 'bg-slate-50 text-slate-600 border-slate-200',
    icon: '🟢'
  },
  'Normal': {
    color: 'bg-slate-100 text-slate-700 border-slate-200',
    icon: '🔵'
  }
}

export function NewTicketsList({ className, limit = 8 }: NewTicketsListProps) {
  const [tickets, setTickets] = useState<NewTicket[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)

  const fetchTickets = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const newTickets = await apiService.getNewTickets(limit)
      setTickets(newTickets)
      setLastUpdate(new Date())
    } catch (err) {
      console.error('Erro ao buscar tickets novos:', err)
      setError('Erro ao carregar tickets')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchTickets()
    
    // CORREÇÃO: Auto-refresh otimizado para 5 minutos com controle de interação
    const interval = setInterval(() => {
      // Verificar se auto-refresh está habilitado
      const autoRefreshEnabled = localStorage.getItem('autoRefreshEnabled')
      if (autoRefreshEnabled === 'false') {
        console.log('⏸️ Auto-refresh de tickets desabilitado pelo usuário')
        return
      }

      const lastInteraction = localStorage.getItem('lastUserInteraction')
      const now = Date.now()
      const timeSinceInteraction = lastInteraction ? now - parseInt(lastInteraction) : Infinity
      
      // Só atualiza se não houver interação recente (últimos 2 minutos)
      if (timeSinceInteraction > 120000) {
        console.log('🎫 Atualizando lista de tickets novos')
        fetchTickets()
      } else {
        console.log('⏸️ Atualização da lista de tickets pausada (interação recente)')
      }
    }, 300000) // 5 minutos
    
    return () => clearInterval(interval)
  }, [limit])

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    } catch {
      return 'Data inválida'
    }
  }

  const getPriorityConfig = (priority: string) => {
    return priorityConfig[priority as keyof typeof priorityConfig] || priorityConfig['Normal']
  }

  const itemVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: {
      opacity: 1,
      x: 0,
      transition: {
        duration: 0.3,
        ease: "easeOut"
      }
    }
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  return (
    <Card className={cn("figma-tickets-recentes h-full flex flex-col", className)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="figma-heading-large flex items-center gap-2">
            <div className="p-2 rounded-xl bg-gradient-to-br shadow-lg from-slate-600 to-slate-700">
              <AlertCircle className="h-5 w-5 text-white" />
            </div>
            Tickets Novos
          </CardTitle>
          
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="bg-slate-50 text-slate-700 border-slate-200">
              {tickets.length} tickets
            </Badge>
            <Button
              variant="outline"
              size="sm"
              onClick={fetchTickets}
              disabled={isLoading}
              className="h-8 w-8 p-0"
            >
              <RefreshCw className={cn("h-4 w-4", isLoading && "animate-spin")} />
            </Button>
          </div>
        </div>
        
        {lastUpdate && (
          <div className="flex items-center gap-1 figma-body">
            <Clock className="h-3 w-3" />
            Atualizado {formatRelativeTime(lastUpdate)}
          </div>
        )}
      </CardHeader>
      
      <CardContent className="pt-0 flex-1 overflow-hidden">
        {isLoading ? (
          <div className="space-y-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="flex items-start gap-3 p-3 figma-glass-card rounded-lg">
                  <div className="w-8 h-8 bg-gray-200 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-3/4" />
                    <div className="h-3 bg-gray-200 rounded w-1/2" />
                    <div className="h-3 bg-gray-200 rounded w-1/4" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="text-center py-8">
            <AlertCircle className="w-12 h-12 mx-auto mb-4 text-red-400" />
            <div className="text-sm text-red-600 font-medium">{error}</div>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={fetchTickets}
              className="mt-3"
            >
              Tentar novamente
            </Button>
          </div>
        ) : tickets.length === 0 ? (
          <div className="text-center py-8">
            <AlertCircle className="w-12 h-12 mx-auto mb-4 figma-body" />
            <div className="figma-body font-medium">Nenhum ticket novo encontrado</div>
            <div className="figma-body mt-1">Todos os tickets foram processados</div>
          </div>
        ) : (
          <motion.div 
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="space-y-3 h-80 overflow-y-auto pr-2"
          >
            {tickets.map((ticket, index) => {
              const priorityConf = getPriorityConfig(ticket.priority)
              
              return (
                <motion.div
                  key={ticket.id}
                  variants={itemVariants}
                  className="group p-3 figma-glass-card rounded-lg transition-all duration-200 border border-transparent"
                >
                  <div className="flex items-start gap-3">
                    {/* Ícone de prioridade */}
                    <div className="flex-shrink-0 mt-0.5">
                      <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium border ${priorityConf.color}`}>
                        <span className="mr-1">{priorityConf.icon}</span>
                        {ticket.priority}
                      </div>
                    </div>
                    
                    {/* Conteúdo do ticket */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <div className="flex items-center gap-2">
                          <span className="figma-subheading">
                            #{ticket.id}
                          </span>
                          <Badge variant="secondary" className="text-xs">
                            NOVO
                          </Badge>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="opacity-0 group-hover:opacity-100 transition-opacity h-6 w-6 p-0"
                        >
                          <ExternalLink className="h-3 w-3" />
                        </Button>
                      </div>
                      
                      <h4 className="figma-body mb-2 line-clamp-2 leading-tight">
                        {ticket.title}
                      </h4>
                      
                      {ticket.description && (
                        <p className="figma-body mb-2 line-clamp-2 leading-relaxed opacity-75">
                          {ticket.description}
                        </p>
                      )}
                      
                      <div className="flex items-center justify-between figma-body">
                        <div className="flex items-center gap-1">
                          <User className="h-3 w-3" />
                          <span className="truncate max-w-24">{ticket.requester}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          <span>{formatDate(ticket.date)}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </motion.div>
        )}
      </CardContent>
    </Card>
  )
}