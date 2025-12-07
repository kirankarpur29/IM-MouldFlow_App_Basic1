import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import NewProject from './pages/NewProject'
import Analysis from './pages/Analysis'

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/new" element={<NewProject />} />
          <Route path="/analysis/:projectId" element={<Analysis />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
