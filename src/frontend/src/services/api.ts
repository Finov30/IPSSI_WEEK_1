import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Types pour les réponses API
export interface UseCase1Response {
  annee: number | null
  secteur: string | null
  region: string | null
  nombre_creations: number
}

export interface UseCase2Response {
  sexe: string
  secteur: string | null
  region: string | null
  nombre_entreprises: number
}

export interface UseCase3Response {
  effectifs: string
  secteur: string | null
  region: string | null
  nombre_entreprises: number
}

export interface UseCase4Response {
  region: string
  secteur_dominant: string
  nombre_entreprises: number
}

export interface UseCase5Response {
  categorie_juridique: number
  secteur: string | null
  region: string | null
  nombre_entreprises: number
}

// API functions
export const api = {
  // Use Case 1: Évolution des créations
  getCreations: async (params?: { year?: number; secteur?: string; region?: string }) => {
    const response = await apiClient.get<UseCase1Response[]>('/api/v1/usecase1/creations', { params })
    return response.data
  },

  // Use Case 2: Répartition par sexe dirigeants
  getSexeDirigeants: async (params?: { sexe?: string; secteur?: string; region?: string }) => {
    const response = await apiClient.get<UseCase2Response[]>('/api/v1/usecase2/sexe-dirigeants', { params })
    return response.data
  },

  // Use Case 3: Répartition des effectifs
  getEffectifs: async (params?: { secteur?: string; region?: string; effectif?: string }) => {
    const response = await apiClient.get<UseCase3Response[]>('/api/v1/usecase3/effectifs', { params })
    return response.data
  },

  // Use Case 4: Dominance sectorielle
  getDominanceSectorielle: async (params?: { year?: number }) => {
    const response = await apiClient.get<UseCase4Response[]>('/api/v1/usecase4/dominance-sectorielle', { params })
    return response.data
  },

  // Use Case 5: Types juridiques
  getTypesJuridiques: async (params?: { secteur?: string; region?: string; categorie_juridique?: number }) => {
    const response = await apiClient.get<UseCase5Response[]>('/api/v1/usecase5/types-juridiques', { params })
    return response.data
  },

  // Health check
  getHealth: async () => {
    const response = await apiClient.get('/health')
    return response.data
  },
}

export default api

