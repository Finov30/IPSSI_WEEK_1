import { useState, useEffect } from 'react'
import { api, UseCase4Response } from '@/services/api'
import FranceMap from '@/components/Map/FranceMap'
import RegionMarker from '@/components/Map/RegionMarker'
import YearFilter from '@/components/Filters/YearFilter'
import { getSecteurLibelle } from '@/utils/secteurs'
import './UseCase.css'

const UseCase4 = () => {
  const [data, setData] = useState<UseCase4Response[]>([])
  const [loading, setLoading] = useState(true)
  const [year, setYear] = useState<number | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const result = await api.getDominanceSectorielle(year ? { year } : undefined)
        setData(result)
      } catch (error) {
        console.error('Erreur lors du chargement des données:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [year])

  const maxValue = Math.max(...data.map((d) => d.nombre_entreprises), 1)

  // Couleurs différentes par secteur
  const secteurColors: Record<string, string> = {}
  const colors = [
    '#667eea',
    '#f093fb',
    '#4facfe',
    '#00f2fe',
    '#43e97b',
    '#fa709a',
    '#fee140',
    '#30cfd0',
    '#a8edea',
    '#fed6e3',
  ]
  let colorIndex = 0

  data.forEach((item) => {
    if (!secteurColors[item.secteur_dominant]) {
      secteurColors[item.secteur_dominant] = colors[colorIndex % colors.length]
      colorIndex++
    }
  })

  return (
    <div className="usecase-page">
      <div className="page-header">
        <h1>Dominance sectorielle par région</h1>
        <p>Découvrez le secteur d'activité dominant dans chaque région</p>
      </div>

      <div className="filters-container">
        <YearFilter value={year} onChange={setYear} />
      </div>

      {loading ? (
        <div className="loading">Chargement des données...</div>
      ) : (
        <>
          <div className="stats">
            <div className="stat-card">
              <div className="stat-value">{data.length}</div>
              <div className="stat-label">Régions analysées</div>
            </div>
          </div>

          <FranceMap>
            {data.map((item) => (
              <RegionMarker
                key={item.region}
                region={item.region}
                value={item.nombre_entreprises}
                maxValue={maxValue}
                color={secteurColors[item.secteur_dominant] || '#667eea'}
                popupContent={
                  <div>
                    <strong>{item.region}</strong>
                    <br />
                    Secteur dominant: {item.secteur_dominant} - {getSecteurLibelle(item.secteur_dominant)}
                    <br />
                    Nombre d'entreprises: {item.nombre_entreprises.toLocaleString()}
                  </div>
                }
              />
            ))}
          </FranceMap>

          <div className="chart-container">
            <h2>Secteurs dominants par région</h2>
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Région</th>
                    <th>Secteur dominant</th>
                    <th>Libellé</th>
                    <th>Nombre d'entreprises</th>
                  </tr>
                </thead>
                <tbody>
                  {data
                    .sort((a, b) => b.nombre_entreprises - a.nombre_entreprises)
                    .map((item) => (
                      <tr key={item.region}>
                        <td>{item.region}</td>
                        <td>{item.secteur_dominant}</td>
                        <td>{getSecteurLibelle(item.secteur_dominant)}</td>
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

export default UseCase4

