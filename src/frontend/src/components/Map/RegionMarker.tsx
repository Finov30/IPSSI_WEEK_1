import { CircleMarker, Popup } from 'react-leaflet'
import { LatLngExpression } from 'leaflet'
import { getRegionCoordinates } from '@/utils/regions'

interface RegionMarkerProps {
  region: string
  value: number
  maxValue: number
  color?: string
  popupContent?: React.ReactNode
}

const RegionMarker = ({ region, value, maxValue, color = '#3388ff', popupContent }: RegionMarkerProps) => {
  const coords = getRegionCoordinates(region)
  
  if (!coords) return null

  // Taille du cercle proportionnelle à la valeur (min 10px, max 50px)
  const radius = Math.max(10, Math.min(50, (value / maxValue) * 50))
  
  // Opacité basée sur la valeur
  const opacity = Math.max(0.3, Math.min(1, value / maxValue))

  return (
    <CircleMarker
      center={[coords.lat, coords.lng] as LatLngExpression}
      radius={radius}
      pathOptions={{
        fillColor: color,
        color: '#fff',
        fillOpacity: opacity,
        weight: 2,
      }}
    >
      <Popup>
        {popupContent || (
          <div>
            <strong>{region}</strong>
            <br />
            Valeur: {value.toLocaleString()}
          </div>
        )}
      </Popup>
    </CircleMarker>
  )
}

export default RegionMarker

