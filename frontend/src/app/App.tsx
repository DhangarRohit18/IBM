/**
 * LEGACYX — App Root.
 *
 * Composes Providers + Router.
 * No business logic belongs here.
 */

import { Providers } from './Providers'
import { Router } from './Router'

export function App() {
  return (
    <Providers>
      <Router />
    </Providers>
  )
}
