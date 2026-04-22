import { Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import { MainLayout } from '@/components/layout/MainLayout'
import { Dashboard } from '@/pages/Dashboard'
import { Datasets } from '@/pages/Datasets'
import { Analysis } from '@/pages/Analysis'
import { DataCollection } from '@/pages/DataCollection'
import { Models } from '@/pages/Models'
import { Settings } from '@/pages/Settings'

function App() {
  return (
    <>
      <MainLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/datasets" element={<Datasets />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/collection" element={<DataCollection />} />
          <Route path="/models" element={<Models />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </MainLayout>
      <Toaster />
    </>
  )
}

export default App
