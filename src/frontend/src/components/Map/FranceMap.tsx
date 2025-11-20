import { MapContainer, TileLayer, useMap } from 'react-leaflet'
import { LatLngExpression } from 'leaflet'
import 'leaflet/dist/leaflet.css'
import './FranceMap.css'

interface FranceMapProps {
  children?: React.ReactNode
  center?: LatLngExpression
  zoom?: number
  className?: string
}

const DEFAULT_CENTER: LatLngExpression = [46.5, 2.5] // Centre de la France
const DEFAULT_ZOOM = 6

const MapUpdater = ({ center, zoom }: { center?: LatLngExpression; zoom?: number }) => {
  const map = useMap()
  if (center) {
    map.setView(center, zoom || map.getZoom())
  }
  return null
}

const FranceMap = ({ children, center = DEFAULT_CENTER, zoom = DEFAULT_ZOOM, className = '' }: FranceMapProps) => {
  return (
    <div className={`france-map-container ${className}`}>
      <MapContainer
        center={center}
        zoom={zoom}
        scrollWheelZoom={true}
        className="france-map"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {center && <MapUpdater center={center} zoom={zoom} />}
        {children}
      </MapContainer>
    </div>
  )
}

export default FranceMap

