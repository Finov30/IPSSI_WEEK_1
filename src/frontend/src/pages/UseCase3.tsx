import { useState, useEffect } from 'react'
import { api, UseCase3Response } from '@/services/api'
import FranceMap from '@/components/Map/FranceMap'
import RegionMarker from '@/components/Map/RegionMarker'
import SectorFilter from '@/components/Filters/SectorFilter'
import RegionFilter from '@/components/Filters/RegionFilter'
import './UseCase.css'

const UseCase3 = () => {
  const [data, setData] = useState<UseCase3Response[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    secteur: null as string | null,
    region: null as string | null,
    effectif: null as string | null,
  })

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const result = await api.getEffectifs(filters)
        setData(result)
      } catch (error) {
        console.error('Erreur lors du chargement des données:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [filters])

  // Agrégation par région
  const regionData = data.reduce((acc, item) => {
    if (!item.region) return acc
    const key = item.region
    if (!acc[key]) {
      acc[key] = 0
    }
    acc[key] += item.nombre_entreprises
    return acc
  }, {} as Record<string, number>)

  const maxValue = Math.max(...Object.values(regionData), 1)

  return (
    <div className="usecase-page">
      <div className="page-header">
        <h1>Répartition des effectifs</h1>
        <p>Explorez la répartition des effectifs par secteurs et territoires</p>
      </div>

      <div className="filters-container">
        <SectorFilter
          value={filters.secteur}
          onChange={(secteur) => setFilters({ ...filters, secteur })}
        />
        <RegionFilter
          value={filters.region}
          onChange={(region) => setFilters({ ...filters, region })}
        />
        <div className="filter-group">
          <label htmlFor="effectif-filter" className="filter-label">
            Tranche d'effectifs
          </label>
          <select
            id="effectif-filter"
            className="filter-select"
            value={filters.effectif || ''}
            onChange={(e) => setFilters({ ...filters, effectif: e.target.value || null })}
          >
            <option value="">Toutes</option>
            <option value="00">0 salarié</option>
            <option value="01">1 ou 2 salariés</option>
            <option value="02">3 à 5 salariés</option>
            <option value="03">6 à 9 salariés</option>
            <option value="11">10 à 19 salariés</option>
            <option value="12">20 à 49 salariés</option>
            <option value="21">50 à 99 salariés</option>
            <option value="22">100 à 199 salariés</option>
            <option value="31">200 à 249 salariés</option>
            <option value="32">250 à 499 salariés</option>
            <option value="41">500 à 999 salariés</option>
            <option value="42">1000 à 1999 salariés</option>
            <option value="51">2000 à 4999 salariés</option>
            <option value="52">5000 à 9999 salariés</option>
            <option value="53">10000 salariés et plus</option>
            <option value="NN">Non renseigné</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading">Chargement des données...</div>
      ) : (
        <>
          <div className="stats">
            <div className="stat-card">
              <div className="stat-value">{data.length}</div>
              <div className="stat-label">Agrégations</div>
            </div>
            <div className="stat-card">
              <div className="stat-value">
                {data.reduce((sum, item) => sum + item.nombre_entreprises, 0).toLocaleString()}
              </div>
              <div className="stat-label">Total entreprises</div>
            </div>
          </div>

          <FranceMap>
            {Object.entries(regionData).map(([region, value]) => (
              <RegionMarker
                key={region}
                region={region}
                value={value}
                maxValue={maxValue}
                color="#4facfe"
                popupContent={
                  <div>
                    <strong>{region}</strong>
                    <br />
                    Entreprises: {value.toLocaleString()}
                  </div>
                }
              />
            ))}
          </FranceMap>
        </>
      )}
    </div>
  )
}

export default UseCase3

