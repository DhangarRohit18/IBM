/**
 * LEGACYX — React Query + Router Providers.
 *
 * Wraps the application with all required context providers:
 *   - QueryClientProvider (TanStack Query)
 *   - BrowserRouter (React Router)
 *
 * Zustand stores do not require a Provider — they are module-level singletons.
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,       // 30 seconds
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

interface ProvidersProps {
  children: React.ReactNode
}

export function Providers({ children }: ProvidersProps) {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  )
}
