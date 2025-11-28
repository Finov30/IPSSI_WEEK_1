import { useState, useEffect } from 'react'
import { api, UseCase2Response } from '@/services/api'
import FranceMap from '@/components/Map/FranceMap'
import RegionMarker from '@/components/Map/RegionMarker'
import SectorFilter from '@/components/Filters/SectorFilter'
import RegionFilter from '@/components/Filters/RegionFilter'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import './UseCase.css'

const COLORS = ['#667eea', '#f093fb', '#4facfe', '#00f2fe']

const UseCase2 = () => {
  const [data, setData] = useState<UseCase2Response[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({
    sexe: null as string | null,
    secteur: null as string | null,
    region: null as string | null,
  })

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        // Convertir null en undefined pour l'API
        const apiFilters = {
          sexe: filters.sexe ?? undefined,
          secteur: filters.secteur ?? undefined,
          region: filters.region ?? undefined,
        }
        const result = await api.getSexeDirigeants(apiFilters)
        setData(result)
      } catch (error) {
        console.error('Erreur lors du chargement des données:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [filters])

  // Agrégation par région et sexe (normaliser les valeurs)
  const regionData = data.reduce((acc, item) => {
    if (!item.region) return acc
    const key = item.region
    if (!acc[key]) {
      acc[key] = { M: 0, F: 0 }
    }
    // Normaliser la valeur de sexe
    const sexeNormalized = item.sexe?.toString().trim().toUpperCase() || ''
    if (sexeNormalized === 'M' || sexeNormalized === 'F') {
      acc[key][sexeNormalized as 'M' | 'F'] += item.nombre_entreprises
    }
    return acc
  }, {} as Record<string, { M: number; F: number }>)

  const maxValue = Math.max(
    ...Object.values(regionData).flatMap((v) => [v.M, v.F]),
    1
  )

  // Données pour le graphique global (normaliser les valeurs de sexe)
  const globalData = data.reduce(
    (acc, item) => {
      // Normaliser la valeur de sexe (M, F en majuscules, supprimer espaces)
      const sexeNormalized = item.sexe?.toString().trim().toUpperCase() || ''
      if (sexeNormalized === 'M' || sexeNormalized === 'F') {
        acc[sexeNormalized] = (acc[sexeNormalized] || 0) + item.nombre_entreprises
      }
      return acc
    },
    {} as Record<string, number>
  )

  const pieData = Object.entries(globalData)
    .map(([sexe, value]) => ({
      name: sexe === 'M' ? 'Homme' : sexe === 'F' ? 'Femme' : sexe,
      value,
    }))
    .filter((item) => item.name === 'Homme' || item.name === 'Femme') // Filtrer uniquement M et F

  return (
    <div className="usecase-page">
      <div className="page-header">
        <h1>Répartition par sexe des dirigeants</h1>
        <p>Visualisez la répartition par sexe des dirigeants selon les secteurs d'activité</p>
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
          <label htmlFor="sexe-filter" className="filter-label">
            Sexe
          </label>
          <select
            id="sexe-filter"
            className="filter-select"
            value={filters.sexe || ''}
            onChange={(e) => setFilters({ ...filters, sexe: e.target.value || null })}
          >
            <option value="">Tous</option>
            <option value="M">Homme</option>
            <option value="F">Femme</option>
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

          {pieData.length > 0 && (
            <div className="chart-container">
              <h2>Répartition globale par sexe</h2>
              <ResponsiveContainer width="100%" height={400}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                    outerRadius={120}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {pieData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}

          <FranceMap>
            {Object.entries(regionData).map(([region, values]) => {
              const total = values.M + values.F
              return (
                <RegionMarker
                  key={region}
                  region={region}
                  value={total}
                  maxValue={maxValue}
                  color="#667eea"
                  popupContent={
                    <div>
                      <strong>{region}</strong>
                      <br />
                      Hommes: {values.M.toLocaleString()}
                      <br />
                      Femmes: {values.F.toLocaleString()}
                      <br />
                      Total: {total.toLocaleString()}
                    </div>
                  }
                />
              )
            })}
          </FranceMap>
        </>
      )}
    </div>
  )
}

export default UseCase2

