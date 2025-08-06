import { motion } from "framer-motion"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn, formatNumber } from "@/lib/utils"
import { Trophy, Medal, Award, Star, Users } from "lucide-react"
import { useRef, useEffect } from "react"

interface TechnicianRanking {
  id: string
  name: string
  level: string
  total: number
  rank: number
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
    .sort((a, b) => b.total - a.total)

  // Configuração de cores e estilos por nível com gradientes similares ao StatusCard
  const getLevelStyle = (level?: string) => {
    switch (level) {
      case 'N4':
        return {
          bgGradient: 'bg-gradient-to-br from-blue-500 to-cyan-600',
          accentColor: '#2D9CDB',
          shadowColor: 'shadow-blue-500/10',
          hoverShadow: 'hover:shadow-blue-500/20'
        }
      case 'N3':
        return {
          bgGradient: 'bg-gradient-to-br from-green-500 to-emerald-600',
          accentColor: '#27AE60',
          shadowColor: 'shadow-green-500/10',
          hoverShadow: 'hover:shadow-green-500/20'
        }
      case 'N2':
        return {
          bgGradient: 'bg-gradient-to-br from-yellow-500 to-orange-600',
          accentColor: '#F2994A',
          shadowColor: 'shadow-orange-500/10',
          hoverShadow: 'hover:shadow-orange-500/20'
        }
      case 'N1':
        return {
          bgGradient: 'bg-gradient-to-br from-purple-500 to-pink-600',
          accentColor: '#9B51E0',
          shadowColor: 'shadow-purple-500/10',
          hoverShadow: 'hover:shadow-purple-500/20'
        }
      default:
        return {
          bgGradient: 'bg-gradient-to-br from-gray-500 to-slate-600',
          accentColor: '#6B7280',
          shadowColor: 'shadow-gray-500/10',
          hoverShadow: 'hover:shadow-gray-500/20'
        }
    }
  }

  // Estatísticas por nível para o cabeçalho
  const levelStats = topTechnicians.reduce((acc, tech) => {
    const level = tech.level || 'Outros'
    acc[level] = (acc[level] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  // Adicionar scroll horizontal com roda do mouse
  useEffect(() => {
    const container = scrollContainerRef.current
    if (!container) return

    const handleWheel = (e: WheelEvent) => {
      e.preventDefault()
      container.scrollLeft += e.deltaY
    }

    container.addEventListener('wheel', handleWheel, { passive: false })
    
    return () => {
      container.removeEventListener('wheel', handleWheel)
    }
  }, [])

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  const cardVariants = {
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
    <Card className={cn("w-full bg-white/80 backdrop-blur-xl border-0 shadow-xl rounded-2xl", className)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg text-gray-700 font-semibold">
            <div className="p-2 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600 shadow-lg">
              <Users className="h-5 w-5 text-white" />
            </div>
            Ranking de Técnicos
          </CardTitle>
          <div className="flex items-center gap-2">
            {Object.entries(levelStats).map(([level, count]) => {
              const style = getLevelStyle(level)
              return (
                <Badge 
                  key={level} 
                  className={cn(
                    "text-xs px-2 py-1 border-0 shadow-sm text-white font-medium bg-gradient-to-r",
                    style.bgGradient
                  )}
                >
                  {level}: {count}
                </Badge>
              )
            })}
          </div>
        </div>
      </CardHeader>
      
      <CardContent>
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-4"
        >
          <div 
            ref={scrollContainerRef}
            className="flex w-full h-32 bg-gray-50/50 backdrop-blur-sm rounded-lg shadow-inner overflow-x-auto overflow-y-hidden border border-gray-200/50 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent"
          >
          {topTechnicians.map((technician, index) => {
            const levelStyle = getLevelStyle(technician.level)
            const position = index + 1
            const isTopThree = position <= 3
            
            return (
              <motion.div
                key={technician.id}
                variants={cardVariants}
                className={cn(
                  "flex-shrink-0 w-36 flex flex-col justify-between p-3 border-r border-white/10 last:border-r-0",
                  "transition-all duration-300 hover:scale-105 relative group overflow-hidden",
                  "bg-white/80 backdrop-blur-xl shadow-xl hover:shadow-2xl rounded-2xl border-0",
                  "border-l-4",
                  "hover:shadow-lg", levelStyle.hoverShadow
                )}
                style={{ borderLeftColor: levelStyle.accentColor }}
              >
                {/* Gradient Background - Opacidade mais suave */}
                <div className={cn(
                  "absolute inset-0 bg-gradient-to-br opacity-5 rounded-2xl",
                  levelStyle.bgGradient
                )} />
                
                {/* Animated Border com blur para suavizar */}
                <div className="absolute inset-0 rounded-2xl">
                  <div className={cn(
                    "absolute inset-0 rounded-2xl bg-gradient-to-r opacity-20 blur-sm",
                    levelStyle.bgGradient
                  )} />
                </div>
                <div className="flex items-center justify-between mb-2 relative z-10">
                  <div className={cn(
                    "w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold",
                    isTopThree ? "bg-white/90 backdrop-blur-sm border border-gray-200 text-gray-700 shadow-md" : "bg-white/70 backdrop-blur-sm border border-gray-200 text-gray-600"
                  )}>
                    {position <= 3 && position === 1 && <Trophy className="w-3 h-3" />}
                    {position <= 3 && position === 2 && <Medal className="w-3 h-3" />}
                    {position <= 3 && position === 3 && <Award className="w-3 h-3" />}
                    {position > 3 && position}
                  </div>
                  
                  {technician.level && (
                    <div className={cn(
                      "px-2 py-0.5 rounded-full text-xs font-medium shadow-sm text-white bg-gradient-to-r",
                      levelStyle.bgGradient
                    )}>
                      {technician.level}
                    </div>
                  )}
                </div>

                <div className="text-center mb-2 relative z-10">
                  <div className="text-xs font-medium text-gray-700 leading-tight">
                    {(() => {
                      const nameParts = technician.name.split(' ');
                      const firstName = nameParts[0] || '';
                      const lastNameInitial = nameParts.length > 1 ? nameParts[nameParts.length - 1].charAt(0).toUpperCase() + '.' : '';
                      return `${firstName} ${lastNameInitial}`.trim();
                    })()}
                  </div>
                </div>
                
                <div className="text-center space-y-1 relative z-10">
                  <div className="text-lg font-bold text-gray-900">
                    {formatNumber(technician.total)}
                  </div>
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
