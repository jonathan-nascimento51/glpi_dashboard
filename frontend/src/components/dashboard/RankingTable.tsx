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

  // Configuração de cores e estilos por nível com gradientes sutis como os StatusCards
  const getLevelStyle = (level?: string) => {
    switch (level) {
      case 'N4':
        return {
          bgGradient: 'bg-gradient-to-br from-slate-500 to-slate-600',
          accentColor: '#64748B',
          shadowColor: 'shadow-slate-500/5',
          hoverShadow: 'hover:shadow-slate-500/10',
          backgroundOpacity: 'opacity-5',
          borderOpacity: 'opacity-20'
        }
      case 'N3':
        return {
          bgGradient: 'bg-gradient-to-br from-emerald-500 to-emerald-600',
          accentColor: '#10B981',
          shadowColor: 'shadow-emerald-500/5',
          hoverShadow: 'hover:shadow-emerald-500/10',
          backgroundOpacity: 'opacity-5',
          borderOpacity: 'opacity-20'
        }
      case 'N2':
        return {
          bgGradient: 'bg-gradient-to-br from-amber-500 to-orange-600',
          accentColor: '#F59E0B',
          shadowColor: 'shadow-amber-500/5',
          hoverShadow: 'hover:shadow-amber-500/10',
          backgroundOpacity: 'opacity-5',
          borderOpacity: 'opacity-20'
        }
      case 'N1':
        return {
          bgGradient: 'bg-gradient-to-br from-blue-500 to-cyan-600',
          accentColor: '#3B82F6',
          shadowColor: 'shadow-blue-500/5',
          hoverShadow: 'hover:shadow-blue-500/10',
          backgroundOpacity: 'opacity-5',
          borderOpacity: 'opacity-20'
        }
      default:
        return {
          bgGradient: 'bg-gradient-to-br from-gray-500 to-slate-600',
          accentColor: '#6B7280',
          shadowColor: 'shadow-gray-500/5',
          hoverShadow: 'hover:shadow-gray-500/10',
          backgroundOpacity: 'opacity-5',
          borderOpacity: 'opacity-20'
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
    hidden: { opacity: 0, y: 20, scale: 0.9 },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: 0.5,
        ease: "easeOut"
      }
    },
    hover: {
      y: -2,
      scale: 1.01,
      zIndex: 5,
      transition: {
        duration: 0.3,
        ease: "easeOut"
      }
    }
  }

  const iconVariants = {
    hover: {
      scale: 1.3,
      rotate: 15,
      transition: {
        duration: 0.2,
        ease: "easeOut"
      }
    }
  }

  return (
    <Card className={cn("figma-ranking-tecnicos w-full h-full flex flex-col rounded-2xl shadow-none", className)}>
      <CardHeader className="px-5 pt-4 pb-2 flex-shrink-0">
        <div className="flex items-center justify-between">
          <CardTitle className="figma-heading-large flex items-center gap-2">
            <div className="p-2 rounded-xl bg-gradient-to-br from-slate-500 to-slate-600 shadow-lg">
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
      
      <CardContent className="px-5 pb-4 pt-0 flex-1 flex flex-col">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="flex-1 flex flex-col"
        >
          <div 
            ref={scrollContainerRef}
            className="flex w-full flex-1 overflow-x-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent"
            style={{ zIndex: 1, overflowY: 'visible' }}
          >
          {topTechnicians.map((technician, index) => {
            const levelStyle = getLevelStyle(technician.level)
            const position = index + 1
            const isTopThree = position <= 3
            
            return (
              <motion.div
                key={technician.id}
                variants={cardVariants}
                whileHover="hover"
                className={cn(
                  "flex-shrink-0 w-36 flex flex-col justify-between p-6 border-r border-white/10 last:border-r-0",
                  "cursor-pointer relative group overflow-visible",
                  "figma-glass-card rounded-xl border-0 shadow-none",
                  "border-l-4",
                  levelStyle.shadowColor,
                  levelStyle.hoverShadow
                )}
                style={{ 
                  borderLeftColor: levelStyle.accentColor,
                  position: 'relative',
                  zIndex: 2
                }}
              >
                {/* Gradient Background - Seguindo padrão dos StatusCards */}
                <div className={cn(
                  "absolute inset-0 bg-gradient-to-br rounded-xl transition-opacity duration-300",
                  levelStyle.bgGradient,
                  levelStyle.backgroundOpacity,
                  "group-hover:opacity-10"
                )} />
                
                {/* Animated Border - Seguindo padrão dos StatusCards */}
                <div className="absolute inset-0 rounded-xl">
                  <div className={cn(
                    "absolute inset-0 rounded-xl bg-gradient-to-r blur-sm transition-opacity duration-300",
                    levelStyle.bgGradient,
                    levelStyle.borderOpacity,
                    "group-hover:opacity-30"
                  )} />
                </div>
                <div className="flex items-center justify-between mb-1.5 relative z-10">
                  <motion.div 
                    variants={iconVariants}
                    className={cn(
                      "w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold",
                      isTopThree ? "figma-glass-card figma-body shadow-md" : "figma-glass-card figma-body"
                    )}
                  >
                    {position <= 3 && position === 1 && <Trophy className="w-3 h-3" />}
                    {position <= 3 && position === 2 && <Medal className="w-3 h-3" />}
                    {position <= 3 && position === 3 && <Award className="w-3 h-3" />}
                    {position > 3 && position}
                  </motion.div>
                  
                  {technician.level && (
                    <motion.div 
                      className={cn(
                        "px-2 py-0.5 rounded-full text-xs font-medium shadow-sm text-white bg-gradient-to-r",
                        levelStyle.bgGradient
                      )}
                      whileHover={{ scale: 1.05 }}
                      transition={{ duration: 0.2 }}
                    >
                      {technician.level}
                    </motion.div>
                  )}
                </div>

                <div className="text-center mb-1.5 relative z-10">
                  <div className="figma-body leading-tight">
                    {(() => {
                      const nameParts = technician.name.split(' ');
                      const firstName = nameParts[0] || '';
                      const lastNameInitial = nameParts.length > 1 ? nameParts[nameParts.length - 1].charAt(0).toUpperCase() + '.' : '';
                      return `${firstName} ${lastNameInitial}`.trim();
                    })()}
                  </div>
                </div>
                
                <div className="text-center space-y-0.5 relative z-10">
                  <motion.div 
                    className="figma-numeric"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ duration: 0.6, ease: "easeOut", delay: 0.2 }}
                  >
                    {formatNumber(technician.total)}
                  </motion.div>
                </div>
                
                {/* Enhanced Shine Effect */}
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -skew-x-12 opacity-0 pointer-events-none"
                  whileHover={{
                    opacity: [0, 1, 0],
                    x: [-150, 350]
                  }}
                  transition={{ duration: 0.4, ease: "easeOut" }}
                />
              </motion.div>
            )
          })}
          </div>
        </motion.div>
      </CardContent>
    </Card>
  )
}
