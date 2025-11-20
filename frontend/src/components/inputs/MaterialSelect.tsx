import { useState, useEffect } from 'react'
import { api } from '../../api/client'

interface Material {
  id: number
  name: string
  manufacturer: string
  category: string
  viscosity_class: string
  melt_temp_min: number
  melt_temp_max: number
}

interface MaterialSelectProps {
  value: number | null
  onChange: (id: number) => void
}

export default function MaterialSelect({ value, onChange }: MaterialSelectProps) {
  const [materials, setMaterials] = useState<Material[]>([])
  const [categories, setCategories] = useState<string[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadMaterials()
  }, [])

  const loadMaterials = async () => {
    try {
      const [materialsRes, categoriesRes] = await Promise.all([
        api.get('/api/v1/materials/'),
        api.get('/api/v1/materials/categories/list')
      ])
      setMaterials(materialsRes.data)
      setCategories(categoriesRes.data)
    } catch (error) {
      console.error('Failed to load materials:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredMaterials = selectedCategory
    ? materials.filter(m => m.category === selectedCategory)
    : materials

  const selectedMaterial = materials.find(m => m.id === value)

  if (loading) {
    return <div className="text-gray-500">Loading materials...</div>
  }

  return (
    <div className="space-y-3">
      {/* Category filter */}
      <div>
        <label className="block text-sm text-gray-600 mb-1">Category</label>
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
        >
          <option value="">All Categories</option>
          {categories.map(cat => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
      </div>

      {/* Material select */}
      <div>
        <label className="block text-sm text-gray-600 mb-1">Material</label>
        <select
          value={value || ''}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
        >
          <option value="">Select a material</option>
          {filteredMaterials.map(mat => (
            <option key={mat.id} value={mat.id}>
              {mat.name} {mat.manufacturer !== 'Generic' ? `(${mat.manufacturer})` : ''}
            </option>
          ))}
        </select>
      </div>

      {/* Selected material info */}
      {selectedMaterial && (
        <div className="bg-gray-50 p-3 rounded-lg text-sm">
          <div className="grid grid-cols-2 gap-2">
            <div>
              <span className="text-gray-500">Melt Temp:</span>{' '}
              {selectedMaterial.melt_temp_min}-{selectedMaterial.melt_temp_max}°C
            </div>
            <div>
              <span className="text-gray-500">Viscosity:</span>{' '}
              {selectedMaterial.viscosity_class}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
