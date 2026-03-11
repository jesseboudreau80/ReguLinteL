import { Link } from 'react-router-dom'

const dot = (score) => {
  if (score >= 10) return 'red'
  if (score >= 5) return 'yellow'
  if (score >= 0) return 'green'
  return 'gray'
}

export function Dashboard({ deals }) {
  return (
    <section>
      <h2>Deal Dashboard</h2>
      <table>
        <thead>
          <tr>
            <th>Deal Name</th><th>City</th><th>State</th><th>Services</th><th>Zoning</th><th>Licensing</th><th>Inspection</th><th>Infrastructure</th><th>Entity</th><th>Risk Score</th>
          </tr>
        </thead>
        <tbody>
          {deals.map(d => (
            <tr key={d.id}>
              <td><Link to={`/deals/${d.id}`}>{d.business_name}</Link></td>
              <td>{d.city}</td>
              <td>{d.state}</td>
              <td>{d.services.join(', ')}</td>
              <td>{d.zoning_status}</td>
              <td>{d.licensing_status}</td>
              <td>{d.inspection_status}</td>
              <td>{d.infrastructure_status}</td>
              <td>{d.entity_status}</td>
              <td><span className={`dot ${dot(d.risk_score)}`}></span>{d.risk_score}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}
