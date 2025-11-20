// Coordonnées des régions françaises pour Leaflet
export interface RegionCoordinates {
  name: string
  lat: number
  lng: number
  code?: string
}

export const REGIONS_COORDINATES: RegionCoordinates[] = [
  { name: 'Auvergne-Rhône-Alpes', lat: 45.75, lng: 4.85, code: '84' },
  { name: 'Bourgogne-Franche-Comté', lat: 47.24, lng: 6.02, code: '27' },
  { name: 'Bretagne', lat: 48.12, lng: -1.68, code: '53' },
  { name: 'Centre-Val de Loire', lat: 47.90, lng: 1.90, code: '24' },
  { name: 'Corse', lat: 42.15, lng: 9.15, code: '94' },
  { name: 'Grand Est', lat: 48.57, lng: 7.75, code: '44' },
  { name: 'Hauts-de-France', lat: 50.48, lng: 2.79, code: '32' },
  { name: 'Île-de-France', lat: 48.85, lng: 2.35, code: '11' },
  { name: 'Normandie', lat: 49.18, lng: -0.37, code: '28' },
  { name: 'Nouvelle-Aquitaine', lat: 44.84, lng: -0.58, code: '75' },
  { name: 'Occitanie', lat: 43.60, lng: 1.44, code: '76' },
  { name: 'Pays de la Loire', lat: 47.47, lng: -0.55, code: '52' },
  { name: "Provence-Alpes-Côte d'Azur", lat: 43.30, lng: 5.37, code: '93' },
  { name: 'Guadeloupe', lat: 16.27, lng: -61.51, code: '01' },
  { name: 'Guyane', lat: 3.93, lng: -53.12, code: '03' },
  { name: 'La Réunion', lat: -21.12, lng: 55.45, code: '04' },
  { name: 'Martinique', lat: 14.64, lng: -61.02, code: '02' },
  { name: 'Mayotte', lat: -12.83, lng: 45.17, code: '06' },
]

export const getRegionCoordinates = (regionName: string): RegionCoordinates | undefined => {
  return REGIONS_COORDINATES.find(
    (r) => r.name.toLowerCase() === regionName.toLowerCase()
  )
}

