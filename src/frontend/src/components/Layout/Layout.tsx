import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import './Layout.css'

interface LayoutProps {
  children: ReactNode
}

const Layout = ({ children }: LayoutProps) => {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Accueil' },
    { path: '/usecase1', label: 'Évolution créations' },
    { path: '/usecase2', label: 'Sexe dirigeants' },
    { path: '/usecase3', label: 'Effectifs' },
    { path: '/usecase4', label: 'Dominance sectorielle' },
    { path: '/usecase5', label: 'Types juridiques' },
  ]

  return (
    <div className="layout">
      <header className="header">
        <div className="header-content">
          <h1 className="logo">Sirene DataViz</h1>
          <nav className="nav">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <main className="main-content">{children}</main>
    </div>
  )
}

export default Layout

