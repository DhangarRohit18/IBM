/**
 * LEGACYX — 404 Not Found Page.
 */

import { Link } from 'react-router-dom'
import { AlertTriangle } from 'lucide-react'

export function NotFoundPage() {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100%',
      gap: '16px',
      color: 'var(--text-secondary)',
    }}>
      <AlertTriangle size={40} color="var(--text-muted)" />
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: '18px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>
          Page not found
        </div>
        <div style={{ fontSize: '13px', color: 'var(--text-muted)', marginBottom: '20px' }}>
          The route you requested does not exist yet.
        </div>
        <Link to="/" style={{
          color: 'var(--accent)',
          fontSize: '13px',
          textDecoration: 'none',
          fontWeight: 500,
        }}>
          ← Return to Dashboard
        </Link>
      </div>
    </div>
  )
}
