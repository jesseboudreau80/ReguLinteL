import { Link, Route, Routes } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { Dashboard } from './pages/Dashboard'
import { NewScan } from './pages/NewScan'
import { DealDetail } from './pages/DealDetail'

const API = 'http://localhost:8000'

export default function App() {
  const [deals, setDeals] = useState([])

  const loadDeals = async () => {
    const r = await fetch(`${API}/api/deals`)
    setDeals(await r.json())
  }

  useEffect(() => {
    loadDeals()
  }, [])

  return (
    <div className="layout">
      <aside>
        <h1>ReguLinteL</h1>
        <nav>
          <Link to="/">Dashboard</Link>
          <Link to="/new-scan">New Regulatory Scan</Link>
        </nav>
      </aside>
      <main>
        <Routes>
          <Route path="/" element={<Dashboard deals={deals} />} />
          <Route path="/new-scan" element={<NewScan onDone={loadDeals} />} />
          <Route path="/deals/:id" element={<DealDetail />} />
        </Routes>
      </main>
    </div>
  )
}
