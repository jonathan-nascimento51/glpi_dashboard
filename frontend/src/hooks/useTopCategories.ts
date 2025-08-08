import { useState, useEffect, useCallback } from 'react'
import api from '../services/api'

export interface CategoryRanking {
  id: string
  name: string
  complete_name: string
  ticket_count: number
  rank: number
  parent_category: string
  level: number
}

export interface UseTopCategoriesOptions {
  limit?: number
  startDate?: string
  endDate?: string
  maintenanceGroup?: string
  autoRefresh?: boolean
  refreshInterval?: number
}

export interface UseTopCategoriesReturn {
  data: CategoryRanking[]
  isLoading: boolean
  error: string | null
  refresh: () => Promise<void>
  lastUpdated: Date | null
}

export const useTopCategories = (options: UseTopCategoriesOptions = {}): UseTopCategoriesReturn => {
  const {
    limit = 10,
    startDate,
    endDate,
    maintenanceGroup,
    autoRefresh = false,
    refreshInterval = 300000 // 5 minutos
  } = options

  const [data, setData] = useState<CategoryRanking[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetchTopCategories = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)

      const params = new URLSearchParams()
      
      if (limit) params.append('limit', limit.toString())
      if (startDate) params.append('start_date', startDate)
      if (endDate) params.append('end_date', endDate)
      if (maintenanceGroup) params.append('maintenance_group', maintenanceGroup)

      const response = await api.get(`/tickets/top-categories?${params.toString()}`)
      
      if (response.data.success) {
        setData(response.data.data || [])
        setLastUpdated(new Date())
      } else {
        throw new Error(response.data.error || 'Erro ao buscar top categorias')
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido ao buscar top categorias'
      setError(errorMessage)
      console.error('Erro ao buscar top categorias:', err)
    } finally {
      setIsLoading(false)
    }
  }, [limit, startDate, endDate, maintenanceGroup])

  // Buscar dados iniciais
  useEffect(() => {
    fetchTopCategories()
  }, [fetchTopCategories])

  // Auto refresh
  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      fetchTopCategories()
    }, refreshInterval)

    return () => clearInterval(interval)
  }, [autoRefresh, refreshInterval, fetchTopCategories])

  const refresh = useCallback(async () => {
    await fetchTopCategories()
  }, [fetchTopCategories])

  return {
    data,
    isLoading,
    error,
    refresh,
    lastUpdated
  }
}

export default useTopCategories