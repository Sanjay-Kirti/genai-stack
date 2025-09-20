import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { User } from 'lucide-react'
import { cn } from '@/lib/utils'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  const navigation = [
    { name: 'Workflow Builder', href: '/builder' },
    { name: 'My Stacks', href: '/stacks' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <Link to="/" className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
                    <span className="text-white font-bold text-sm">GS</span>
                  </div>
                  <span className="ml-2 text-xl font-semibold text-gray-900">GenAI Stack</span>
                </Link>
              </div>
              <nav className="ml-10 flex items-baseline space-x-1">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={cn(
                      'px-4 py-2 rounded-lg text-sm transition-all duration-200',
                      location.pathname.startsWith(item.href)
                        ? 'bg-green-50 text-green-700 font-medium'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    )}
                  >
                    {item.name}
                  </Link>
                ))}
              </nav>
            </div>
            <div className="flex items-center gap-3">
              <button className="w-9 h-9 bg-purple-100 rounded-full flex items-center justify-center hover:bg-purple-200 transition-colors">
                <User className="w-5 h-5 text-purple-600" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>
    </div>
  )
}
