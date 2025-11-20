import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout/Layout'
import Home from './pages/Home'
import UseCase1 from './pages/UseCase1'
import UseCase2 from './pages/UseCase2'
import UseCase3 from './pages/UseCase3'
import UseCase4 from './pages/UseCase4'
import UseCase5 from './pages/UseCase5'

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/usecase1" element={<UseCase1 />} />
          <Route path="/usecase2" element={<UseCase2 />} />
          <Route path="/usecase3" element={<UseCase3 />} />
          <Route path="/usecase4" element={<UseCase4 />} />
          <Route path="/usecase5" element={<UseCase5 />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App

