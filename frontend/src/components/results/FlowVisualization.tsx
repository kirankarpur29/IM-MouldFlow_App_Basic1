import { useState, useEffect } from 'react'
import { api } from '../../api/client'

interface FlowVisualizationProps {
  partId: number
  gateX?: number
  gateY?: number
}

export default function FlowVisualization({ partId, gateX, gateY }: FlowVisualizationProps) {
  const [svgContent, setSvgContent] = useState<string>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadVisualization()
  }, [partId, gateX, gateY])

  const loadVisualization = async () => {
    setLoading(true)
    setError(null)

    try {
      const params = new URLSearchParams()
      if (gateX !== undefined) params.append('gate_x', gateX.toString())
      if (gateY !== undefined) params.append('gate_y', gateY.toString())

      const response = await api.get(
        `/api/v1/parts/${partId}/flow-visualization?${params.toString()}`,
        { responseType: 'text' }
      )

      setSvgContent(response.data)
    } catch (err) {
      console.error('Failed to load flow visualization:', err)
      setError('Failed to load flow visualization')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center text-gray-500">
        {error}
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg p-2">
      <div
        className="w-full flex justify-center"
        dangerouslySetInnerHTML={{ __html: svgContent }}
      />
      <p className="text-xs text-gray-500 text-center mt-2">
        Approximate flow pattern - not a detailed simulation
      </p>
    </div>
  )
}
