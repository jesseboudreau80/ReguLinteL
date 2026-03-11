import { useState } from 'react'

const API = 'http://66.94.117.172:8000'
const serviceOptions = ['boarding','daycare','grooming','veterinary','training','retail','swimming']

export function NewScan({ onDone }) {
  const [form, setForm] = useState({ business_name: '', street_address: '', city: '', state: '', services: [] })
  const [status, setStatus] = useState('')

  const toggle = (name) => {
    setForm(f => ({ ...f, services: f.services.includes(name) ? f.services.filter(s => s !== name) : [...f.services, name] }))
  }

  const submit = async (e) => {
    e.preventDefault()
    setStatus('Running silent scan...')
    console.log('Submitting scan payload:', form)
    const r = await fetch(`${API}/api/scans`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form)
    })
    if (r.ok) {
      setStatus('Scan completed.')
      setForm({ business_name: '', street_address: '', city: '', state: '', services: [] })
      onDone()
    } else {
      setStatus('Scan failed.')
    }
  }

  return (
    <section>
      <h2>New Regulatory Scan</h2>
      <form onSubmit={submit} className="card">
        <input placeholder="Business Name" value={form.business_name} onChange={e => setForm({ ...form, business_name: e.target.value })} required />
        <input placeholder="Street Address" value={form.street_address} onChange={e => setForm({ ...form, street_address: e.target.value })} required />
        <input placeholder="City" value={form.city} onChange={e => setForm({ ...form, city: e.target.value })} required />
        <input placeholder="State" value={form.state} maxLength={2} onChange={e => setForm({ ...form, state: e.target.value.toUpperCase() })} required />

        <label>Services Offered</label>
        <div className="services">
          {serviceOptions.map(s => (
            <label key={s}><input type="checkbox" checked={form.services.includes(s)} onChange={() => toggle(s)} /> {s}</label>
          ))}
        </div>

        <button>Run Silent Scan</button>
      </form>
      <p>{status}</p>
    </section>
  )
}
