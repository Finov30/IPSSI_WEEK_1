import { REGIONS_COORDINATES } from '@/utils/regions'
import './Filters.css'

interface RegionFilterProps {
  value: string | null
  onChange: (region: string | null) => void
}

const RegionFilter = ({ value, onChange }: RegionFilterProps) => {
  return (
    <div className="filter-group">
      <label htmlFor="region-filter" className="filter-label">
        Région
      </label>
      <select
        id="region-filter"
        className="filter-select"
        value={value || ''}
        onChange={(e) => onChange(e.target.value || null)}
      >
        <option value="">Toutes les régions</option>
        {REGIONS_COORDINATES.map((region) => (
          <option key={region.name} value={region.name}>
            {region.name}
          </option>
        ))}
      </select>
    </div>
  )
}

export default RegionFilter

