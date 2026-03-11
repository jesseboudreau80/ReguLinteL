import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'

const API = 'http://localhost:8000'

export function DealDetail() {
  const { id } = useParams()
  const [deal, setDeal] = useState(null)

  useEffect(() => {
    fetch(`${API}/api/deals/${id}`).then(r => r.json()).then(setDeal)
  }, [id])

  if (!deal) return <p>Loading...</p>

  return (
    <section>
      <h2>{deal.business_name} - Regulatory Snapshot</h2>
      <p>{deal.street_address}, {deal.city}, {deal.state}</p>
      <h3>Required Licenses</h3>
      <ul>{deal.required_licenses.map(item => <li key={item}>{item}</li>)}</ul>
      <h3>Inspection Agencies</h3>
      <ul>{deal.inspection_agencies.map(item => <li key={item}>{item}</li>)}</ul>
      <h3>LP Deal Risk Radar</h3>
      <pre>{JSON.stringify(deal.risk_radar, null, 2)}</pre>
      <h3>Due Diligence Checklist</h3>
      <ul>{deal.due_diligence_checklist.map(item => <li key={item}>{item}</li>)}</ul>
      <h3>Uploaded Documents</h3>
      <ul>{deal.uploaded_documents.length ? deal.uploaded_documents.map(d => <li key={d}>{d}</li>) : <li>No documents uploaded</li>}</ul>
      <h3>Exports</h3>
      <p>
        <a href={`${API}/api/deals/${id}/export/pdf`} target="_blank">PDF</a> |{' '}
        <a href={`${API}/api/deals/${id}/export/txt`} target="_blank">TXT</a> |{' '}
        <a href={`${API}/api/deals/${id}/export/json`} target="_blank">JSON</a>
      </p>
    </section>
  )
}
