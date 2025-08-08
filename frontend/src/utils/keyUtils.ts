/**
 * Utility functions for generating unique keys in React components
 * to prevent duplicate key warnings
 */

/**
 * Generates a unique key with a prefix and suffix
 * @param prefix - The prefix for the key
 * @param id - The main identifier
 * @param suffix - Optional suffix
 * @returns A unique key string
 */
export const generateUniqueKey = (prefix: string, id: string | number, suffix?: string): string => {
  const timestamp = Date.now()
  const random = Math.random().toString(36).substr(2, 5)
  return `${prefix}-${id}${suffix ? `-${suffix}` : ''}-${timestamp}-${random}`
}

/**
 * Generates a key for metrics components
 * @param type - The type of metric (e.g., 'new', 'progress', 'pending', 'resolved')
 * @param context - The context where it's being used (e.g., 'main-grid', 'level-grid')
 * @returns A unique key string
 */
export const generateMetricsKey = (type: string, context: string = 'default'): string => {
  const random = Math.random().toString(36).substr(2, 9)
  return `metrics-${context}-${type}-${Date.now()}-${random}`
}

/**
 * Generates a key for level components
 * @param level - The level (e.g., 'n1', 'n2', 'n3', 'n4')
 * @param status - The status (e.g., 'novos', 'pendentes', 'progresso', 'resolvidos')
 * @returns A unique key string
 */
export const generateLevelKey = (level: string, status: string): string => {
  const random = Math.random().toString(36).substr(2, 9)
  return `level-${level}-status-${status}-${Date.now()}-${random}`
}

/**
 * Generates a key for error/warning items in DataIntegrityMonitor
 * @param type - The type ('error' or 'warning')
 * @param section - The section ('metrics', 'system', 'ranking')
 * @param index - The index in the array
 * @returns A unique key string
 */
export const generateIntegrityKey = (type: 'error' | 'warning', section: string, index: number): string => {
  const random = Math.random().toString(36).substr(2, 9)
  return `integrity-${section}-${type}-${index}-${Date.now()}-${random}`
}

/**
 * Generates a key for skeleton loading items
 * @param index - The index in the array
 * @param context - The context where it's being used
 * @returns A unique key string
 */
export const generateSkeletonKey = (index: number, context: string = 'default'): string => {
  const random = Math.random().toString(36).substr(2, 9)
  return `skeleton-${context}-${index}-${Date.now()}-${random}`
}