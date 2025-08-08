import React, { useRef, useEffect, useMemo, useCallback } from "react"
import { motion } from "framer-motion"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn, formatNumber } from "@/lib/utils"
import { Trophy, Folder, Settings, Wrench, Zap, AlertTriangle, Info } from "lucide-react"
import { usePerformanceMonitoring, useRenderTracker } from "../../hooks/usePerformanceMonitoring"
import { performanceMonitor } from "../../utils/performanceMonitor"
import { useTopCategories, CategoryRanking } from "../../hooks/useTopCategories"
import { GLPI_CONFIG, getCategoryConfig, hasActiveData, getContextualMessage } from "../../config/glpi-config"

interface CategoryRankingTableProps {
  title?: string
  className?: string
  limit?: number
  autoRefresh?: boolean
  dateRange?: { start: string; end: string }
}

// Função para obter estilo baseado na categoria - Usando configuração GLPI
function getCategoryStyle(categoryName?: string, _level?: number) {
  if (!categoryName) {
    return {
      bgColor: 'bg-gradient-to-br from-slate-50 to-slate-100 border-slate-300',
      borderColor: 'border-slate-300',
      accentColor: 'bg-gradient-to-r from-slate-500 to-slate-600',
      iconColor: 'text-slate-700',
      iconBg: 'bg-slate-200',
      icon: Folder
    }
  }
  
  const config = getCategoryConfig(categoryName);
  const isActive = hasActiveData(categoryName);
  
  // Configurações baseadas na categoria principal
  if (config) {
    const colorMap = {
      blue: {
        bgColor: 'bg-gradient-to-br from-blue-50 to-blue-100 border-blue-300',
        borderColor: 'border-blue-300',
        accentColor: 'bg-gradient-to-r from-blue-500 to-blue-600',
        iconColor: 'text-blue-700',
        iconBg: 'bg-blue-200'
      },
      green: {
        bgColor: 'bg-gradient-to-br from-green-50 to-green-100 border-green-300',
        borderColor: 'border-green-300',
        accentColor: 'bg-gradient-to-r from-green-500 to-green-600',
        iconColor: 'text-green-700',
        iconBg: 'bg-green-200'
      },
      orange: {
        bgColor: 'bg-gradient-to-br from-orange-50 to-orange-100 border-orange-300',
        borderColor: 'border-orange-300',
        accentColor: 'bg-gradient-to-r from-orange-500 to-orange-600',
        iconColor: 'text-orange-700',
        iconBg: 'bg-orange-200'
      }
    };
    
    const colors = (colorMap as any)[config.color] || colorMap.blue;
    
    return {
      ...colors,
      icon: config.icon === 'Wrench' ? Wrench : config.icon === 'Settings' ? Settings : Folder,
      isActive
    };
  }
  
  // Estilos específicos para subcategorias conhecidas
  if (categoryName.includes('Elétrica') || categoryName.includes('Eletrica')) {
    return {
      bgColor: 'bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-300',
      borderColor: 'border-yellow-300',
      accentColor: 'bg-gradient-to-r from-yellow-500 to-yellow-600',
      iconColor: 'text-yellow-700',
      iconBg: 'bg-yellow-200',
      icon: Zap,
      isActive
    };
  }
  
  if (categoryName.includes('Hidráulica') || categoryName.includes('Hidraulica')) {
    return {
      bgColor: 'bg-gradient-to-br from-cyan-50 to-cyan-100 border-cyan-300',
      borderColor: 'border-cyan-300',
      accentColor: 'bg-gradient-to-r from-cyan-500 to-cyan-600',
      iconColor: 'text-cyan-700',
      iconBg: 'bg-cyan-200',
      icon: Wrench,
      isActive
    };
  }
  
  if (categoryName.includes('Rede Computadores')) {
    return {
      bgColor: 'bg-gradient-to-br from-purple-50 to-purple-100 border-purple-300',
      borderColor: 'border-purple-300',
      accentColor: 'bg-gradient-to-r from-purple-500 to-purple-600',
      iconColor: 'text-purple-700',
      iconBg: 'bg-purple-200',
      icon: Zap,
      isActive
    };
  }
  
  // Estilo padrão
  return {
    bgColor: 'bg-gradient-to-br from-slate-50 to-slate-100 border-slate-300',
    borderColor: 'border-slate-300',
    accentColor: 'bg-gradient-to-r from-slate-500 to-slate-600',
    iconColor: 'text-slate-700',
    iconBg: 'bg-slate-200',
    icon: Folder,
    isActive
  };
}



// Componente de card de categoria - Tema Conservação e Manutenção
const CategoryCard = React.memo<{
  category: CategoryRanking
  position: number
  isTopThree: boolean
}>(function CategoryCard({ category, position, isTopThree }) {
  const categoryStyle = getCategoryStyle(category.name, category.level)
  const isActive = categoryStyle.isActive
  
  return (
    <motion.div
      key={category.id}
      variants={cardVariants}
      whileHover="hover"
      className={cn(
        "flex-shrink-0 w-64 flex flex-col p-5 rounded-xl border-2 transition-all duration-300",
        "cursor-pointer relative group hover:shadow-xl transform hover:-translate-y-1",
        categoryStyle.bgColor,
        categoryStyle.borderColor,
        isTopThree && "ring-4 ring-opacity-30 shadow-lg",
        isTopThree && position === 1 && "ring-yellow-400 shadow-yellow-200",
        isTopThree && position === 2 && "ring-gray-400 shadow-gray-200",
        isTopThree && position === 3 && "ring-amber-400 shadow-amber-200",
        isActive && "ring-2 ring-green-400 ring-opacity-50"
      )}
    >
      {/* Indicador de dados ativos */}
      {isActive && (
        <div className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-green-500 border-2 border-white shadow-sm">
          <div className="w-full h-full rounded-full bg-green-400 animate-pulse"></div>
        </div>
      )}
      {/* Header com posição e ícone */}
      <div className="flex items-center justify-between mb-4">
        <div className={cn(
          "flex items-center justify-center w-10 h-10 rounded-full text-white font-bold text-lg shadow-lg",
          position <= 3 ? 'bg-gradient-to-br from-yellow-400 via-yellow-500 to-yellow-600' :
          position <= 5 ? 'bg-gradient-to-br from-orange-400 via-orange-500 to-orange-600' :
          position <= 10 ? 'bg-gradient-to-br from-slate-400 via-slate-500 to-slate-600' :
          'bg-gradient-to-br from-gray-400 via-gray-500 to-gray-600'
        )}>
          {position}
        </div>
        
        <div className="flex items-center space-x-2">
          <div className={cn(
            "p-2 rounded-lg shadow-sm",
            categoryStyle.iconBg
          )}>
            <categoryStyle.icon className={cn("w-5 h-5", categoryStyle.iconColor)} />
          </div>
          {isTopThree && (
            <Badge className={cn(
              "text-xs font-bold text-white border-0 px-2 py-1 shadow-sm",
              categoryStyle.accentColor
            )}>
              TOP {position}
            </Badge>
          )}
        </div>
      </div>

      {/* Nome da categoria */}
      <div className="mb-4">
        <h4 className="font-bold text-base text-gray-900 leading-tight mb-2">
          {category.name}
        </h4>
        <p className="text-sm text-gray-600 truncate font-medium">
          {category.parent_category}
        </p>
      </div>

      {/* Estatísticas */}
      <div className="mt-auto space-y-3">
        <div className="flex items-center justify-between p-3 bg-white/60 rounded-lg border">
          <span className="text-sm text-gray-700 font-semibold">Solicitações</span>
          <span className="font-bold text-2xl text-gray-900">
            {formatNumber(category.ticket_count)}
          </span>
        </div>
        
        <div className="flex items-center justify-between">
          {isActive ? (
            <div className="flex items-center gap-2 text-green-600">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-semibold">Com Dados</span>
            </div>
          ) : (
            <div className="flex items-center gap-2 text-gray-500">
              <AlertTriangle className="w-3 h-3" />
              <span className="text-sm font-semibold">Sem Dados</span>
            </div>
          )}
          {category.level > 1 && (
            <Badge variant="outline" className="text-sm font-bold border-2">
              N{category.level}
            </Badge>
          )}
        </div>
      </div>

      {/* Indicador de hover com gradiente industrial */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent 
                      opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl" />
      
      {/* Borda de destaque para top 3 */}
      {isTopThree && (
        <div className="absolute -inset-1 bg-gradient-to-r from-yellow-400 via-orange-500 to-yellow-400 
                        rounded-xl opacity-20 group-hover:opacity-30 transition-opacity duration-300 -z-10" />
      )}
    </motion.div>
  )
})

// Variantes de animação movidas para fora do componente
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
  hidden: { 
    opacity: 0, 
    y: 20,
    scale: 0.95
  },
  visible: { 
    opacity: 1, 
    y: 0,
    scale: 1,
    transition: {
      stiffness: 100,
      damping: 15
    }
  },
  hover: {
    y: -2,
    scale: 1.02,
    transition: {
      stiffness: 400,
      damping: 25
    }
  }
}

export const CategoryRankingTable = React.memo<CategoryRankingTableProps>(function CategoryRankingTable({ 
  title = "Ranking de Categorias de Serviços", 
  className,
  limit = 100,
  autoRefresh = false,
  dateRange
}) {
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  
  // Use the hook to fetch data
  const { data, isLoading, error } = useTopCategories({
    limit,
    autoRefresh,
    startDate: dateRange?.start,
    endDate: dateRange?.end
  })
  
  // Performance monitoring hooks
  const { measureRender } = usePerformanceMonitoring('CategoryRankingTable')
  const { trackRender } = useRenderTracker('CategoryRankingTable')
  
  // Track component renders
  useEffect(() => {
    trackRender()
    measureRender(() => {
      performanceMonitor.markComponentRender('CategoryRankingTable', {
        categoryCount: data?.length || 0,
        hasData: (data?.length || 0) > 0
      })
    })
  }, [data?.length, measureRender, trackRender])
  
  // Memoizar top categorias para evitar recálculos
  const topCategories = useMemo(() => {
    return data?.slice(0, limit) || [] // Limitar ao limite especificado
  }, [data, limit])
  
  // Handler para scroll horizontal com roda do mouse
  const handleWheel = useCallback((e: WheelEvent) => {
    if (e.deltaY !== 0) {
      e.preventDefault()
      if (scrollContainerRef.current) {
        scrollContainerRef.current.scrollLeft += e.deltaY
      }
    }
  }, [])
  
  // Adicionar scroll horizontal com roda do mouse
  useEffect(() => {
    const container = scrollContainerRef.current
    if (!container) return

    container.addEventListener('wheel', handleWheel, { passive: false })
    
    return () => {
      container.removeEventListener('wheel', handleWheel)
    }
  }, [handleWheel])
  
  if (isLoading) {
    return (
      <Card className={cn("w-full bg-white/80 backdrop-blur-sm shadow-xl border-2 border-gray-200", className)}>
        <CardHeader className="pb-4 bg-gradient-to-r from-orange-50 to-yellow-50 border-b-2 border-orange-200">
          <CardTitle className="text-xl font-bold text-gray-900 flex items-center gap-3">
            <div className="bg-orange-100 p-2 rounded-lg">
              <Wrench className="w-6 h-6 text-orange-700" />
            </div>
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent className="px-6 pb-6 pt-4">
          <div className="flex items-center justify-center h-40 text-gray-600">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-orange-200 border-t-orange-600 mx-auto mb-4"></div>
              <p className="text-lg font-semibold">Carregando categorias de serviços...</p>
              <p className="text-sm text-gray-500 mt-2">Aguarde enquanto processamos os dados</p>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className={cn("w-full bg-white/80 backdrop-blur-sm shadow-xl border-2 border-red-200", className)}>
        <CardHeader className="pb-4 bg-gradient-to-r from-red-50 to-orange-50 border-b-2 border-red-200">
          <CardTitle className="text-xl font-bold text-gray-900 flex items-center gap-3">
            <div className="bg-red-100 p-2 rounded-lg">
              <AlertTriangle className="w-6 h-6 text-red-700" />
            </div>
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent className="px-6 pb-6 pt-4">
          <div className="flex items-center justify-center h-40 text-red-600">
            <div className="text-center">
              <div className="bg-red-100 p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Folder className="w-8 h-8 text-red-500" />
              </div>
              <p className="text-lg font-semibold">Erro ao carregar categorias</p>
              <p className="text-sm text-gray-500 mt-2 bg-red-50 p-2 rounded border">{error}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (!data || data.length === 0) {
    const contextMessage = getContextualMessage(0);
    
    return (
      <Card className={cn("w-full bg-white/80 backdrop-blur-sm shadow-xl border-2 border-gray-200", className)}>
        <CardHeader className="pb-4 bg-gradient-to-r from-gray-50 to-slate-50 border-b-2 border-gray-200">
          <CardTitle className="text-xl font-bold text-gray-900 flex items-center gap-3">
            <div className="bg-blue-100 p-2 rounded-lg">
              <Info className="w-6 h-6 text-blue-700" />
            </div>
            {title}
            <div className="ml-auto flex items-center gap-2">
              <Badge className="bg-gradient-to-r from-orange-500 to-orange-600 text-white font-bold px-3 py-1 shadow-sm">
                0 categorias
              </Badge>
              <div className="bg-blue-100 px-3 py-1 rounded-full">
                <span className="text-sm font-bold text-blue-700">Sistema Novo</span>
              </div>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="px-6 pb-6 pt-4">
          <div className="flex items-center justify-center h-40 text-gray-500">
            <div className="text-center max-w-md">
              <div className="bg-blue-100 p-4 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Info className="w-8 h-8 text-blue-500" />
              </div>
              <p className="text-lg font-semibold text-gray-600 mb-2">
                {contextMessage?.title || 'Sistema GLPI Recém Implementado'}
              </p>
              <p className="text-sm text-gray-500 mb-3">
                {contextMessage?.description || 'Aguardando solicitações para gerar estatísticas'}
              </p>
              <div className="flex flex-wrap gap-2 justify-center mb-3">
                {Object.keys(GLPI_CONFIG.MAIN_CATEGORIES).map(category => (
                  <Badge key={category} variant="outline" className="text-xs">
                    {category} ({(GLPI_CONFIG.MAIN_CATEGORIES as any)[category].subcategories.slice(0, 3).join(', ')})
                  </Badge>
                ))}
              </div>
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 mt-4">
                <p className="text-xs text-amber-700 font-medium">
                  💡 Categorias ativas: {GLPI_CONFIG.ACTIVE_CATEGORIES.length} de {Object.keys(GLPI_CONFIG.MAIN_CATEGORIES).reduce((acc, cat) => acc + (GLPI_CONFIG.MAIN_CATEGORIES as any)[cat].subcategories.length, 0)} disponíveis
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }
  
  return (
    <Card className={cn("w-full flex flex-col bg-white/80 backdrop-blur-sm shadow-xl border-2 border-gray-200", className)}>
      <CardHeader className="pb-4 flex-shrink-0 bg-gradient-to-r from-orange-50 to-yellow-50 border-b-2 border-orange-200">
        <CardTitle className="text-xl font-bold text-gray-900 flex items-center gap-3">
          <div className="bg-orange-100 p-2 rounded-lg">
            <Trophy className="w-6 h-6 text-orange-700" />
          </div>
          {title}
          <div className="ml-auto flex items-center gap-2">
            <Badge className="bg-gradient-to-r from-orange-500 to-orange-600 text-white font-bold px-3 py-1 shadow-sm">
              {topCategories.length} categorias
            </Badge>
            <div className="bg-green-100 px-3 py-1 rounded-full">
              <span className="text-sm font-bold text-green-700">Ativo</span>
            </div>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="px-6 pb-6 pt-4 flex-1 flex flex-col">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="flex-1 flex flex-col"
        >
          <div 
            ref={scrollContainerRef}
            className="flex w-full flex-1 overflow-x-auto scrollbar-thin scrollbar-thumb-orange-300 scrollbar-track-orange-100 px-2 space-x-4 pb-2"
            style={{ minHeight: '280px' }}
          >
          {topCategories.map((category, index) => (
            <CategoryCard
              key={category.id}
              category={category}
              position={index + 1}
              isTopThree={index < 3}
            />
          ))}
          </div>
          
          {/* Indicador de scroll */}
          {topCategories.length > 4 && (
            <div className="flex justify-center mt-4">
              <div className="bg-orange-100 px-4 py-2 rounded-full border border-orange-200">
                <span className="text-sm font-medium text-orange-700 flex items-center gap-2">
                  <span>←</span>
                  Role horizontalmente para ver todas as categorias
                  <span>→</span>
                </span>
              </div>
            </div>
          )}
        </motion.div>
      </CardContent>
    </Card>
  )
})

export default CategoryRankingTable