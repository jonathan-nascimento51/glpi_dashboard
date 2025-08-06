import { motion } from "framer-motion"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn, formatNumber } from "@/lib/utils"
import { Trophy, Medal, Award, Star, Users } from "lucide-react"
import { useRef, useEffect } from "react"

interface TechnicianRanking {
  id: string
  name: string
  resolved: number
  pending: number
  efficiency: number
  status: 'active' | 'inactive' | 'busy'
}

interface RankingTableProps {
  data: TechnicianRanking[]
  title?: string
  className?: string
}

export function RankingTable({ 
  data, 
  title = "Ranking de Técnicos", 
  className 
}: RankingTableProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  
  // Pegar todos os técnicos e ordenar por número de chamados
  const topTechnicians = data
    .sort((a, b) => b.resolved - a.resolved)
  
  // Função para calcular a intensidade do cinza baseada na posição
  const getGrayIntensity = (index: number, total: number) => {
    // Quanto menor o índice (melhor posição), mais escuro o cinza
    const intensity = Math.round(((total - index - 1) / (total - 1)) * 60 + 20) // 20-80% de intensidade
    return `rgb(${intensity}, ${intensity}, ${intensity})`
  }

  // Adicionar scroll horizontal com roda do mouse
  useEffect(() => {
    const container = scrollContainerRef.current
    if (!container) return

    const handleWheel = (e: WheelEvent) => {
      // Prevenir o scroll vertical padrão
      e.preventDefault()
      
      // Converter movimento vertical da roda em horizontal
      container.scrollLeft += e.deltaY
    }

    container.addEventListener('wheel', handleWheel, { passive: false })
    
    return () => {
      container.removeEventListener('wheel', handleWheel)
    }
  }, [])

  const getRankColor = (position: number) => {
    switch (position) {
      case 1: return "bg-gradient-to-r from-yellow-400 via-yellow-500 to-yellow-600 text-white shadow-lg shadow-yellow-500/25"
      case 2: return "bg-gradient-to-r from-gray-300 via-gray-400 to-gray-500 text-white shadow-lg shadow-gray-400/25"
      case 3: return "bg-gradient-to-r from-amber-400 via-amber-500 to-amber-600 text-white shadow-lg shadow-amber-500/25"
      default: return "bg-gradient-to-r from-blue-50 to-indigo-50 text-gray-700 border border-gray-200/50"
    }
  }

  const getRowHoverEffect = (position: number) => {
    switch (position) {
      case 1: return "hover:shadow-xl hover:shadow-yellow-500/20 hover:scale-[1.02]"
      case 2: return "hover:shadow-xl hover:shadow-gray-400/20 hover:scale-[1.02]"
      case 3: return "hover:shadow-xl hover:shadow-amber-500/20 hover:scale-[1.02]"
      default: return "hover:shadow-lg hover:shadow-blue-500/10 hover:scale-[1.01]"
    }
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.05
      }
    }
  }

  const tileVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.4
      }
    }
  }

  return (
    <Card className={cn("w-full bg-white/50 backdrop-blur-sm border-0 shadow-sm", className)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <div className="p-2 rounded-xl bg-gradient-to-br from-slate-500 to-slate-700 shadow-lg">
              <Users className="h-5 w-5 text-white" />
            </div>
            Ranking de Técnicos
          </CardTitle>
          <Badge variant="outline" className="bg-slate-100 text-slate-700 border-0">
            Total: {topTechnicians.length}
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent>
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-4"
        >
          {/* Layout horizontal contínuo */}
          <div 
            ref={scrollContainerRef}
            className="flex w-full h-32 bg-gradient-to-r from-slate-50 to-slate-100 rounded-lg shadow-inner overflow-x-auto overflow-y-hidden border border-slate-200 scrollbar-thin scrollbar-thumb-slate-300 scrollbar-track-slate-100"
          >
          {topTechnicians.map((technician, index) => {
             const intensity = Math.round(((topTechnicians.length - index - 1) / (topTechnicians.length - 1)) * 40 + 10) // 10-50% de intensidade
             const backgroundColor = `hsl(215, ${20 + intensity}%, ${85 - intensity}%)` // Tons de azul-acinzentado
             const textColor = index < topTechnicians.length / 3 ? 'text-white' : 'text-slate-700'
            
            return (
              <motion.div
                 key={technician.id}
                 variants={tileVariants}
                 className="flex-shrink-0 w-32 flex flex-col justify-center items-center p-2 border-r border-slate-200 last:border-r-0 transition-all duration-300 hover:scale-105 hover:shadow-md"
                 style={{ backgroundColor }}
               >
                {/* Nome do técnico - parte superior */}
                <div className={cn("text-xs font-medium text-center leading-tight mb-2 px-1", textColor)}>
                  <div className="truncate max-w-full">
                    {(() => {
                      const nameParts = technician.name.split(' ');
                      const firstName = nameParts[0] || '';
                      const lastNameInitial = nameParts.length > 1 ? nameParts[nameParts.length - 1].charAt(0).toUpperCase() + '.' : '';
                      return `${firstName} ${lastNameInitial}`.trim();
                    })()}
                  </div>
                </div>
                
                {/* Número de chamados - centro */}
                <div className={cn("text-lg font-bold", textColor)}>
                  {formatNumber(technician.resolved)}
                </div>
              </motion.div>
            )
          })}
          </div>
        </motion.div>
      </CardContent>
    </Card>
  )
}
