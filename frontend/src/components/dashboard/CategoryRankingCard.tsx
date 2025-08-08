import React from "react"
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

import { 
 
  AlertTriangle,
  Loader2
} from "lucide-react"
import { cn } from "@/lib/utils"
import { useTopCategories } from "@/hooks/useTopCategories"

interface CategoryRankingCardProps {
  limit?: number
  startDate?: string
  endDate?: string
  maintenanceGroup?: string
}





const getRankColor = (rank: number) => {
  if (rank <= 3) return 'bg-gradient-to-br from-yellow-400 to-orange-500'
  if (rank <= 5) return 'bg-gradient-to-br from-blue-500 to-purple-600'
  return 'bg-gradient-to-br from-gray-400 to-gray-600'
}

import { CategoryRanking } from '@/hooks/useTopCategories'

const CategoryItem: React.FC<{ category: CategoryRanking; index: number }> = ({ category, index }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="group p-3 rounded-lg figma-glass-card hover:shadow-md transition-all duration-200 border-0"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <div className={cn(
            "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold",
            getRankColor(category.rank)
          )}>
            {category.rank}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="font-medium text-slate-900 dark:text-slate-100 text-sm truncate" title={category.complete_name}>
                {category.name}
              </span>
            </div>
            <div className="flex items-center gap-3 text-xs text-slate-600 dark:text-slate-400">
              {category.parent_category && (
                <span className="truncate" title={category.parent_category}>
                  {category.parent_category}
                </span>
              )}
            </div>
          </div>
        </div>
        <div className="text-right flex-shrink-0">
          <div className="text-xl font-bold text-slate-900 dark:text-slate-100">
            {category.ticket_count}
          </div>
          <div className="text-xs text-slate-500 dark:text-slate-400">
            chamados
          </div>
        </div>
      </div>
    </motion.div>
  )
}

export const CategoryRankingCard: React.FC<CategoryRankingCardProps> = ({ 
  limit = 5,
  startDate,
  endDate,
  maintenanceGroup
}) => {
  const { data: categories, isLoading, error } = useTopCategories({
    limit,
    startDate,
    endDate,
    maintenanceGroup
  })

  if (isLoading) {
    return (
      <Card className="figma-glass-card border-0 shadow-lg h-full">
        <CardContent className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
        </CardContent>
      </Card>
    )
  }

  if (error || !categories) {
    return (
      <Card className="figma-glass-card border-0 shadow-lg h-full">
        <CardContent className="flex items-center justify-center h-64">
          <div className="text-center">
            <AlertTriangle className="h-8 w-8 text-red-500 mx-auto mb-2" />
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Erro ao carregar dados das categorias
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  const totalTickets = categories.reduce((sum, cat) => sum + cat.ticket_count, 0)
  
  return (
    <Card className="figma-glass-card border-0 shadow-lg h-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-1">
              Top 5 Categorias
            </CardTitle>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Ranking por volume de chamados
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-slate-900 dark:text-slate-100">
              {totalTickets}
            </div>
            <div className="text-xs text-slate-500 dark:text-slate-400">
              Total
            </div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <div className="space-y-2">
          {categories.map((category, index) => (
            <CategoryItem 
              key={category.id} 
              category={category} 
              index={index} 
            />
          ))}
        </div>
        
        <div className="mt-4 pt-3 border-t border-slate-200 dark:border-slate-700">
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <div className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                {totalTickets}
              </div>
              <div className="text-xs text-slate-500 dark:text-slate-400">
                Total de Chamados
              </div>
            </div>
            <div>
              <div className="text-lg font-semibold text-blue-600">
                {categories.length}
              </div>
              <div className="text-xs text-slate-500 dark:text-slate-400">
                Categorias
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}