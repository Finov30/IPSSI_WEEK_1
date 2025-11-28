import { useState, useEffect } from 'react'
import { api, UseCase5Response } from '@/services/api'
import FranceMap from '@/components/Map/FranceMap'
import RegionMarker from '@/components/Map/RegionMarker'
import SectorFilter from '@/components/Filters/SectorFilter'
import RegionFilter from '@/components/Filters/RegionFilter'
import './UseCase.css'

const UseCase5 = () => {
  const [data, setData] = useState<UseCase5Response[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    secteur: null as string | null,
    region: null as string | null,
    categorie_juridique: null as number | null,
  })

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        // Convertir null en undefined pour l'API
        const apiFilters = {
          secteur: filters.secteur ?? undefined,
          region: filters.region ?? undefined,
          categorie_juridique: filters.categorie_juridique ?? undefined,
        }
        const result = await api.getTypesJuridiques(apiFilters)
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
        <h1>Types juridiques et catégories</h1>
        <p>Analysez les types juridiques et catégories d'entreprise par secteur et région</p>
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
                color="#43e97b"
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

          <div className="chart-container">
            <h2>Répartition par catégorie juridique</h2>
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Catégorie juridique</th>
                    <th>Secteur</th>
                    <th>Région</th>
                    <th>Nombre d'entreprises</th>
                  </tr>
                </thead>
                <tbody>
                  {data
                    .sort((a, b) => b.nombre_entreprises - a.nombre_entreprises)
                    .slice(0, 50)
                    .map((item, index) => (
                      <tr key={index}>
                        <td>{item.categorie_juridique}</td>
                        <td>{item.secteur || 'N/A'}</td>
                        <td>{item.region || 'N/A'}</td>
                        <td>{item.nombre_entreprises.toLocaleString()}</td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default UseCase5

