import { useState, useEffect } from 'react'
import { api, UseCase1Response } from '@/services/api'
import FranceMap from '@/components/Map/FranceMap'
import RegionMarker from '@/components/Map/RegionMarker'
import SectorFilter from '@/components/Filters/SectorFilter'
import RegionFilter from '@/components/Filters/RegionFilter'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import './UseCase.css'

const UseCase1 = () => {
  const [data, setData] = useState<UseCase1Response[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    secteur: null as string | null,
    region: null as string | null,
  })

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        // Ne pas filtrer par année pour voir l'évolution complète
        // Convertir null en undefined pour l'API
        const apiFilters = {
          secteur: filters.secteur ?? undefined,
          region: filters.region ?? undefined,
        }
        const result = await api.getCreations(apiFilters)
        setData(result)
      } catch (error: any) {
        console.error('Erreur lors du chargement des données:', error)
        // Afficher un message d'erreur à l'utilisateur
        if (error.response) {
          console.error('Erreur API:', error.response.status, error.response.data)
        } else if (error.request) {
          console.error('Pas de réponse de l\'API:', error.request)
        }
        // Ne pas réessayer en boucle si erreur
        setData([])
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [filters])

  // Agrégation par région pour la carte
  const regionData = data.reduce((acc, item) => {
    if (!item.region) return acc
    const key = item.region
    if (!acc[key]) {
      acc[key] = 0
    }
    acc[key] += item.nombre_creations
    return acc
  }, {} as Record<string, number>)

  const maxValue = Math.max(...Object.values(regionData), 1)

  // Données pour le graphique (par année)
  const chartData = data.reduce((acc, item) => {
    if (!item.annee) return acc
    const key = item.annee.toString()
    if (!acc[key]) {
      acc[key] = 0
    }
    acc[key] += item.nombre_creations
    return acc
  }, {} as Record<string, number>)

  const chartDataArray = Object.entries(chartData)
    .map(([annee, nombre]) => ({ annee: parseInt(annee), nombre }))
    .sort((a, b) => a.annee - b.annee)

  return (
    <div className="usecase-page">
      <div className="page-header">
        <h1>Évolution des créations d'entreprises</h1>
        <p>Analysez l'évolution des créations d'entreprises par année et secteur d'activité</p>
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
        <div className="filter-info">
          <p>💡 L'évolution est affichée sur toutes les années disponibles. Utilisez les filtres secteur et région pour affiner l'analyse.</p>
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
                {data.reduce((sum, item) => sum + item.nombre_creations, 0).toLocaleString()}
              </div>
              <div className="stat-label">Total créations</div>
            </div>
          </div>

          <FranceMap>
            {Object.entries(regionData).map(([region, value]) => (
              <RegionMarker
                key={region}
                region={region}
                value={value}
                maxValue={maxValue}
                color="#667eea"
                popupContent={
                  <div>
                    <strong>{region}</strong>
                    <br />
                    Créations: {value.toLocaleString()}
                  </div>
                }
              />
            ))}
          </FranceMap>

          {chartDataArray.length > 0 ? (
            <div className="chart-container">
              <h2>Évolution temporelle des créations</h2>
              <p className="chart-description">
                Évolution du nombre de créations d'entreprises de {chartDataArray[0]?.annee} à {chartDataArray[chartDataArray.length - 1]?.annee}
                {filters.secteur && ` - Secteur ${filters.secteur}`}
                {filters.region && ` - ${filters.region}`}
              </p>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={chartDataArray}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="annee" 
                    label={{ value: 'Année', position: 'insideBottom', offset: -5 }}
                  />
                  <YAxis 
                    label={{ value: 'Nombre de créations', angle: -90, position: 'insideLeft' }}
                  />
                  <Tooltip 
                    formatter={(value: number) => value.toLocaleString()}
                    labelFormatter={(label) => `Année ${label}`}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="nombre" 
                    stroke="#667eea" 
                    strokeWidth={2}
                    name="Nombre de créations"
                    dot={{ fill: '#667eea', r: 4 }}
                    activeDot={{ r: 6 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="chart-container">
              <p className="no-data-message">
                Aucune donnée disponible pour les filtres sélectionnés. Essayez de modifier les filtres secteur ou région.
              </p>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default UseCase1

