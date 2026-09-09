/**
 * LEGACYX — Common TypeScript Types.
 *
 * Shared types used across multiple features.
 * Feature-specific types live in their respective feature/types/ files.
 */

/** Standard API success envelope. */
export interface ApiResponse<T> {
  success: true
  data: T
}

/** Standard API error envelope. */
export interface ApiErrorBody {
  success: false
  error: string
  details?: Array<{ field: string; message: string }>
}

/** Pagination metadata returned by list endpoints. */
export interface PaginationMeta {
  total: number
  page: number
  page_size: number
  total_pages: number
}

/** Generic paginated list response. */
export interface PaginatedResponse<T> {
  items: T[]
  meta: PaginationMeta
}

/** Health check service status. */
export type ServiceStatusValue = 'ok' | 'degraded' | 'unavailable'

export interface ServiceStatus {
  name: string
  status: ServiceStatusValue
  message?: string
}

/** Full health check response. */
export interface HealthResponse {
  status: ServiceStatusValue
  app_name: string
  app_version: string
  environment: string
  timestamp: string
  services: ServiceStatus[]
}
