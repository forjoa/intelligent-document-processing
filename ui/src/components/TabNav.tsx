import type { Tab } from '../types'

interface TabNavProps {
  active: Tab
  onChange: (tab: Tab) => void
}

export function TabNav({ active, onChange }: TabNavProps): JSX.Element {
  const base = 'px-6 py-2 text-sm font-medium border-b-2 transition-colors'
  const on = 'border-gray-900 text-gray-900'
  const off = 'border-transparent text-gray-400 hover:text-gray-700'

  return (
    <nav className="flex border-b border-gray-200 mb-8">
      <button className={`${base} ${active === 'upload' ? on : off}`} onClick={() => onChange('upload')}>
        Upload
      </button>
      <button className={`${base} ${active === 'search' ? on : off}`} onClick={() => onChange('search')}>
        Search
      </button>
    </nav>
  )
}
