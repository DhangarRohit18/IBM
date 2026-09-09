/**
 * LEGACYX — Application Entry Point.
 *
 * Mounts the React application into #root.
 * All providers and routing are configured inside App.
 */

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { App } from './app/App'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

