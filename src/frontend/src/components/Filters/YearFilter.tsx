import './Filters.css'

interface YearFilterProps {
  value: number | null
  onChange: (year: number | null) => void
  minYear?: number
  maxYear?: number
}

const YearFilter = ({ value, onChange, minYear = 1900, maxYear = new Date().getFullYear() }: YearFilterProps) => {
  const years = Array.from({ length: maxYear - minYear + 1 }, (_, i) => minYear + i).reverse()

  return (
    <div className="filter-group">
      <label htmlFor="year-filter" className="filter-label">
        Année
      </label>
      <select
        id="year-filter"
        className="filter-select"
        value={value || ''}
        onChange={(e) => onChange(e.target.value ? parseInt(e.target.value) : null)}
      >
        <option value="">Toutes les années</option>
        {years.map((year) => (
          <option key={year} value={year}>
            {year}
          </option>
        ))}
      </select>
    </div>
  )
}

export default YearFilter

