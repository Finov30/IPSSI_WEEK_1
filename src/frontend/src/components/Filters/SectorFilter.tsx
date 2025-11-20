import { getSecteurLibelle, SECTEUR_LIBELLES } from '@/utils/secteurs'
import './Filters.css'

interface SectorFilterProps {
  value: string | null
  onChange: (secteur: string | null) => void
}

const SectorFilter = ({ value, onChange }: SectorFilterProps) => {
  const secteurs = Object.keys(SECTEUR_LIBELLES).sort()

  return (
    <div className="filter-group">
      <label htmlFor="sector-filter" className="filter-label">
        Secteur d'activité
      </label>
      <select
        id="sector-filter"
        className="filter-select"
        value={value || ''}
        onChange={(e) => onChange(e.target.value || null)}
      >
        <option value="">Tous les secteurs</option>
        {secteurs.map((code) => (
          <option key={code} value={code}>
            {code} - {getSecteurLibelle(code)}
          </option>
        ))}
      </select>
    </div>
  )
}

export default SectorFilter

