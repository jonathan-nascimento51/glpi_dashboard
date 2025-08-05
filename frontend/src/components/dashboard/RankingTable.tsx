import { motion } from "framer-motion"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn, formatNumber, getStatusColor } from "@/lib/utils"
import { Trophy, Medal, Award, User, Star } from "lucide-react"

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
  const getRankIcon = (position: number) => {
    switch (position) {
      case 1: return <Trophy className="h-5 w-5 text-yellow-500 drop-shadow-sm" />
      case 2: return <Medal className="h-5 w-5 text-gray-400 drop-shadow-sm" />
      case 3: return <Award className="h-5 w-5 text-amber-600 drop-shadow-sm" />
      default: return <Star className="h-4 w-4 text-gray-400" />
    }
  }

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

  // ANIMAÇÕES MODERNAS E SUAVES
  const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        ease: "easeOut",
        staggerChildren: 0.1
      }
    }
  }

  const rowVariants = {
    hidden: { opacity: 0, x: -20, scale: 0.95 },
    visible: {
      opacity: 1,
      x: 0,
      scale: 1,
      transition: {
        duration: 0.5,
        ease: "easeOut"
      }
    },
    hover: {
      scale: 1.02,
      transition: {
        duration: 0.2,
        ease: "easeInOut"
      }
    }
  }

  const cardVariants = {
    hidden: { opacity: 0, scale: 0.9 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.5,
        ease: "easeOut"
      }
    }
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className={className}
    >
      <motion.div variants={cardVariants}>
        <Card className="border-0 shadow-2xl bg-white/80 backdrop-blur-xl rounded-2xl overflow-hidden">
          <CardHeader className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 text-white">
            <CardTitle className="flex items-center gap-3 text-xl font-bold">
              <div className="p-2 bg-white/20 rounded-lg backdrop-blur-sm">
                <Trophy className="h-6 w-6" />
              </div>
              {title}
              <div className="ml-auto flex items-center gap-2">
                <div className="px-3 py-1 bg-white/20 rounded-full text-sm font-medium backdrop-blur-sm">
                  {data.length} técnicos
                </div>
              </div>
            </CardTitle>
          </CardHeader>
          
          <CardContent className="p-0">
            <div className="overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow className="border-gray-100 bg-gray-50/50">
                    <TableHead className="w-16 font-semibold text-gray-700">#</TableHead>
                    <TableHead className="font-semibold text-gray-700">Técnico</TableHead>
                    <TableHead className="text-center font-semibold text-gray-700">Resolvidos</TableHead>
                    <TableHead className="text-center font-semibold text-gray-700">Pendentes</TableHead>
                    <TableHead className="text-center font-semibold text-gray-700">Eficiência</TableHead>
                    <TableHead className="text-center font-semibold text-gray-700">Status</TableHead>
                  </TableRow>
                </TableHeader>
                
                <TableBody>
                  {data.map((technician, index) => {
                    const position = index + 1
                    return (
                      <motion.tr
                        key={technician.id}
                        variants={rowVariants}
                        whileHover="hover"
                        className={cn(
                          "border-gray-100/50 transition-all duration-300 cursor-pointer",
                          getRowHoverEffect(position)
                        )}
                      >
                        <TableCell className="font-medium py-4">
                          <div className="flex items-center gap-3">
                            <motion.div 
                              className={cn(
                                "w-8 h-8 rounded-xl flex items-center justify-center text-sm font-bold transition-all duration-300",
                                getRankColor(position)
                              )}
                              whileHover={{ scale: 1.1, rotate: 5 }}
                              transition={{ duration: 0.2 }}
                            >
                              {position}
                            </motion.div>
                            <motion.div
                              whileHover={{ scale: 1.2, rotate: 10 }}
                              transition={{ duration: 0.2 }}
                            >
                              {getRankIcon(position)}
                            </motion.div>
                          </div>
                        </TableCell>
                        
                        <TableCell className="py-4">
                          <div className="flex items-center gap-4">
                            <motion.div 
                              className="relative"
                              whileHover={{ scale: 1.1 }}
                              transition={{ duration: 0.2 }}
                            >
                              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 via-purple-500 to-indigo-600 rounded-xl flex items-center justify-center text-white text-lg font-bold shadow-lg">
                                {technician.name.charAt(0).toUpperCase()}
                              </div>
                              <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full border-2 border-white shadow-sm"></div>
                            </motion.div>
                            <div>
                              <div className="font-semibold text-gray-900 text-lg">
                                {technician.name}
                              </div>
                              <div className="text-sm text-gray-500">
                                Técnico Nível {position <= 3 ? 'Senior' : 'Pleno'}
                              </div>
                            </div>
                          </div>
                        </TableCell>
                        
                        <TableCell className="text-center py-4">
                          <motion.div
                            whileHover={{ scale: 1.05 }}
                            transition={{ duration: 0.2 }}
                          >
                            <Badge className="bg-gradient-to-r from-green-500 to-emerald-600 text-white border-0 shadow-lg px-4 py-2 text-sm font-semibold">
                              {formatNumber(technician.resolved)}
                            </Badge>
                          </motion.div>
                        </TableCell>
                        
                        <TableCell className="text-center py-4">
                          <motion.div
                            whileHover={{ scale: 1.05 }}
                            transition={{ duration: 0.2 }}
                          >
                            <Badge className="bg-gradient-to-r from-orange-500 to-red-500 text-white border-0 shadow-lg px-4 py-2 text-sm font-semibold">
                              {formatNumber(technician.pending)}
                            </Badge>
                          </motion.div>
                        </TableCell>
                        
                        <TableCell className="text-center py-4">
                          <div className="flex items-center justify-center gap-3">
                            <div className="relative w-16 h-3 bg-gray-200 rounded-full overflow-hidden shadow-inner">
                              <motion.div 
                                className="h-full bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-600 rounded-full shadow-sm"
                                initial={{ width: 0 }}
                                animate={{ width: `${Math.min(technician.efficiency, 100)}%` }}
                                transition={{ duration: 1, ease: "easeOut", delay: index * 0.1 }}
                              />
                            </div>
                            <motion.span 
                              className="text-sm font-bold text-gray-700 min-w-[3rem]"
                              whileHover={{ scale: 1.1 }}
                              transition={{ duration: 0.2 }}
                            >
                              {technician.efficiency}%
                            </motion.span>
                          </div>
                        </TableCell>
                        
                        <TableCell className="text-center py-4">
                          <motion.div
                            whileHover={{ scale: 1.05 }}
                            transition={{ duration: 0.2 }}
                          >
                            <Badge 
                              className={cn(
                                "capitalize font-semibold px-4 py-2 border-0 shadow-lg",
                                technician.status === 'active' && "bg-gradient-to-r from-green-500 to-emerald-600 text-white",
                                technician.status === 'busy' && "bg-gradient-to-r from-yellow-500 to-orange-500 text-white",
                                technician.status === 'inactive' && "bg-gradient-to-r from-gray-400 to-gray-500 text-white"
                              )}
                            >
                              <motion.div 
                                className={cn(
                                  "w-2 h-2 rounded-full mr-2",
                                  technician.status === 'active' && "bg-white",
                                  technician.status === 'busy' && "bg-white",
                                  technician.status === 'inactive' && "bg-white"
                                )}
                                animate={{ scale: [1, 1.2, 1] }}
                                transition={{ duration: 2, repeat: Infinity }}
                              />
                              {technician.status === 'active' ? 'Ativo' : 
                               technician.status === 'busy' ? 'Ocupado' : 'Inativo'}
                            </Badge>
                          </motion.div>
                        </TableCell>
                      </motion.tr>
                    )
                  })}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}
