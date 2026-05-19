import { useState } from 'react'
import type { Tab } from './types'
import { TabNav } from './components/TabNav'
import { UploadView } from './components/UploadView'
import { SearchView } from './components/SearchView'

export function App(): JSX.Element {
  const [active, setActive] = useState<Tab>('upload')

  return (
    <div className="min-h-screen bg-white text-gray-900">
      <div className="max-w-2xl mx-auto px-6 py-10">
        <h1 className="text-2xl font-semibold text-gray-900 mb-8">Document Processing</h1>
        <TabNav active={active} onChange={setActive} />
        {active === 'upload' ? <UploadView /> : <SearchView />}
      </div>
    </div>
  )
}
