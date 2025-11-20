import { Link } from 'react-router-dom'
import './Home.css'

const Home = () => {
  const useCases = [
    {
      path: '/usecase1',
      title: 'Évolution des créations',
      description: 'Analysez l\'évolution des créations d\'entreprises par année et secteur d\'activité',
      icon: '📈',
    },
    {
      path: '/usecase2',
      title: 'Répartition par sexe dirigeants',
      description: 'Visualisez la répartition par sexe des dirigeants selon les secteurs d\'activité',
      icon: '👥',
    },
    {
      path: '/usecase3',
      title: 'Répartition des effectifs',
      description: 'Explorez la répartition des effectifs par secteurs et territoires',
      icon: '👔',
    },
    {
      path: '/usecase4',
      title: 'Dominance sectorielle',
      description: 'Découvrez le secteur dominant par région',
      icon: '🏆',
    },
    {
      path: '/usecase5',
      title: 'Types juridiques',
      description: 'Analysez les types juridiques et catégories d\'entreprise par secteur et région',
      icon: '📋',
    },
  ]

  return (
    <div className="home">
      <div className="home-hero">
        <h1>Bienvenue sur Sirene DataViz</h1>
        <p className="home-subtitle">
          Plateforme de visualisation interactive des données Sirene
        </p>
        <p className="home-description">
          Explorez les données des entreprises françaises à travers 5 analyses interactives
          avec des cartes de France et des graphiques dynamiques.
        </p>
      </div>

      <div className="usecases-grid">
        {useCases.map((usecase) => (
          <Link key={usecase.path} to={usecase.path} className="usecase-card">
            <div className="usecase-icon">{usecase.icon}</div>
            <h3>{usecase.title}</h3>
            <p>{usecase.description}</p>
            <span className="usecase-link">Explorer →</span>
          </Link>
        ))}
      </div>
    </div>
  )
}

export default Home

