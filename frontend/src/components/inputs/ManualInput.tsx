import { useState } from 'react'
import { api } from '../../api/client'

interface ManualInputProps {
  projectId: number
  onCreated: (part: any) => void
}

export default function ManualInput({ projectId, onCreated }: ManualInputProps) {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    length: '',
    width: '',
    height: '',
    avg_thickness: ''
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const result = await api.post(
        `/api/v1/parts/manual?project_id=${projectId}&name=${encodeURIComponent(formData.name || 'Manual Part')}`,
        {
          length: parseFloat(formData.length),
          width: parseFloat(formData.width),
          height: parseFloat(formData.height),
          avg_thickness: parseFloat(formData.avg_thickness)
        }
      )

      onCreated(result.data)
    } catch (error) {
      console.error('Failed to create part:', error)
      alert('Failed to create part from manual input')
    } finally {
      setLoading(false)
    }
  }

  const isValid = formData.length && formData.width && formData.height && formData.avg_thickness

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-800">
        <strong>Manual Input Mode</strong>
        <p className="mt-1">Results will be labeled as estimates without CAD geometry.</p>
      </div>

      <div>
        <label className="block text-sm text-gray-600 mb-1">Part Name</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
          placeholder="e.g., Housing Cover"
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="block text-sm text-gray-600 mb-1">Length (mm) *</label>
          <input
            type="number"
            required
            min="1"
            step="0.1"
            value={formData.length}
            onChange={(e) => setFormData({ ...formData, length: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            placeholder="100"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-600 mb-1">Width (mm) *</label>
          <input
            type="number"
            required
            min="1"
            step="0.1"
            value={formData.width}
            onChange={(e) => setFormData({ ...formData, width: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            placeholder="80"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-600 mb-1">Height (mm) *</label>
          <input
            type="number"
            required
            min="1"
            step="0.1"
            value={formData.height}
            onChange={(e) => setFormData({ ...formData, height: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            placeholder="50"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-600 mb-1">Avg. Thickness (mm) *</label>
          <input
            type="number"
            required
            min="0.5"
            max="20"
            step="0.1"
            value={formData.avg_thickness}
            onChange={(e) => setFormData({ ...formData, avg_thickness: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            placeholder="2.5"
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={loading || !isValid}
        className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? 'Creating...' : 'Create Part from Dimensions'}
      </button>
    </form>
  )
}
