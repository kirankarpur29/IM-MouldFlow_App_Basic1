import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { api } from '../../api/client'

interface ThicknessChartProps {
  partId: number
}

interface DistributionData {
  range_start: number
  range_end: number
  percentage: number
}

export default function ThicknessChart({ partId }: ThicknessChartProps) {
  const [data, setData] = useState<DistributionData[]>([])
  const [stats, setStats] = useState<{ min: number; avg: number; max: number } | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDistribution()
  }, [partId])

  const loadDistribution = async () => {
    try {
      const response = await api.get(`/api/v1/parts/${partId}/thickness-distribution`)
      setData(response.data.distribution)
      setStats({
        min: response.data.min_thickness,
        avg: response.data.avg_thickness,
        max: response.data.max_thickness
      })
    } catch (error) {
      console.error('Failed to load thickness distribution:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="h-40 bg-gray-50 rounded flex items-center justify-center">
        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  // Format data for chart
  const chartData = data.map(d => ({
    range: `${d.range_start.toFixed(1)}`,
    percentage: d.percentage,
    label: `${d.range_start.toFixed(1)}-${d.range_end.toFixed(1)}mm`
  }))

  return (
    <div>
      {stats && (
        <div className="flex justify-between text-xs text-gray-500 mb-2">
          <span>Min: {stats.min.toFixed(1)}mm</span>
          <span>Avg: {stats.avg.toFixed(1)}mm</span>
          <span>Max: {stats.max.toFixed(1)}mm</span>
        </div>
      )}
      <div className="h-32">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
            <XAxis
              dataKey="range"
              tick={{ fontSize: 10 }}
              tickLine={false}
              axisLine={false}
            />
            <YAxis hide />
            <Tooltip
              formatter={(value: number) => [`${value}%`, 'Volume']}
              labelFormatter={(label) => `Thickness: ${label}mm`}
              contentStyle={{ fontSize: 12 }}
            />
            <Bar
              dataKey="percentage"
              fill="#3b82f6"
              radius={[2, 2, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="text-xs text-gray-400 text-center">
        Wall Thickness Distribution (estimated)
      </p>
    </div>
  )
}
