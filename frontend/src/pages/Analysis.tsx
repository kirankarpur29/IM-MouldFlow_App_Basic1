import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '../api/client'
import ModelViewer from '../components/viewer/ModelViewer'
import FileUpload from '../components/inputs/FileUpload'
import ManualInput from '../components/inputs/ManualInput'
import MaterialSelect from '../components/inputs/MaterialSelect'
import AnalysisConfig from '../components/inputs/AnalysisConfig'
import ResultsPanel from '../components/results/ResultsPanel'
import FlowVisualization from '../components/results/FlowVisualization'
import ThicknessChart from '../components/results/ThicknessChart'

interface Part {
  id: number
  name: string
  file_type?: string
  is_manual?: boolean
  geometry: {
    volume_cm3: number
    projected_area_cm2: number
    max_thickness: number
    min_thickness: number
    avg_thickness: number
    bbox_x: number
    bbox_y: number
    bbox_z: number
  }
}

export default function Analysis() {
  const { projectId } = useParams()
  const [viewMode, setViewMode] = useState<'designer' | 'customer'>('designer')
  const [inputMode, setInputMode] = useState<'file' | 'manual'>('file')
  const [part, setPart] = useState<Part | null>(null)
  const [materialId, setMaterialId] = useState<number | null>(null)
  const [analysisConfig, setAnalysisConfig] = useState({
    cavity_count: 1,
    gate_type: 'edge',
    safety_factor: 1.15
  })
  const [analysisResult, setAnalysisResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handlePartUploaded = (uploadedPart: Part) => {
    setPart(uploadedPart)
    setAnalysisResult(null)
  }

  const runAnalysis = async () => {
    if (!part || !materialId) {
      alert('Please upload a part and select a material')
      return
    }

    setLoading(true)
    try {
      const response = await api.post('/api/v1/analysis/', {
        part_id: part.id,
        material_id: materialId,
        ...analysisConfig
      })
      setAnalysisResult(response.data)
    } catch (error) {
      console.error('Analysis failed:', error)
      alert('Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const generateReport = async (reportType: string) => {
    if (!analysisResult) return

    try {
      const response = await api.post('/api/v1/reports/generate', {
        analysis_id: analysisResult.id,
        report_type: reportType,
        format: 'pdf'
      })

      // Download the report
      const downloadResponse = await api.get(
        `/api/v1/reports/${response.data.id}/download`,
        { responseType: 'blob' }
      )

      const url = window.URL.createObjectURL(new Blob([downloadResponse.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `report_${reportType}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Report generation failed:', error)
      alert('Failed to generate report')
    }
  }

  return (
    <div className="space-y-6">
      {/* View Toggle */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Mold Flow Analysis</h1>
        <div className="flex bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setViewMode('designer')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              viewMode === 'designer'
                ? 'bg-white shadow text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Designer View
          </button>
          <button
            onClick={() => setViewMode('customer')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              viewMode === 'customer'
                ? 'bg-white shadow text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Customer View
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Panel - Input */}
        <div className="space-y-4">
          {/* 3D Viewer / File Upload / Manual Input */}
          <div className="bg-white rounded-lg shadow-sm p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Part Geometry</h2>
              {!part && (
                <div className="flex bg-gray-100 rounded p-0.5 text-xs">
                  <button
                    onClick={() => setInputMode('file')}
                    className={`px-2 py-1 rounded ${inputMode === 'file' ? 'bg-white shadow' : ''}`}
                  >
                    CAD File
                  </button>
                  <button
                    onClick={() => setInputMode('manual')}
                    className={`px-2 py-1 rounded ${inputMode === 'manual' ? 'bg-white shadow' : ''}`}
                  >
                    Manual
                  </button>
                </div>
              )}
            </div>
            {part ? (
              <div>
                {part.is_manual || part.file_type === 'manual' ? (
                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-center mb-4">
                    <div className="text-3xl mb-2">📐</div>
                    <div className="font-medium text-amber-800">Manual Input</div>
                    <div className="text-xs text-amber-600">Estimated - No CAD</div>
                  </div>
                ) : (
                  <ModelViewer partId={part.id} />
                )}
                <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
                  <div className="bg-gray-50 p-2 rounded">
                    <span className="text-gray-500">Volume:</span>{' '}
                    <span className="font-medium">{part.geometry.volume_cm3} cm³</span>
                  </div>
                  <div className="bg-gray-50 p-2 rounded">
                    <span className="text-gray-500">Proj. Area:</span>{' '}
                    <span className="font-medium">{part.geometry.projected_area_cm2} cm²</span>
                  </div>
                  <div className="bg-gray-50 p-2 rounded">
                    <span className="text-gray-500">Thickness:</span>{' '}
                    <span className="font-medium">
                      {part.geometry.min_thickness}-{part.geometry.max_thickness} mm
                    </span>
                  </div>
                  <div className="bg-gray-50 p-2 rounded">
                    <span className="text-gray-500">Size:</span>{' '}
                    <span className="font-medium">
                      {part.geometry.bbox_x}×{part.geometry.bbox_y}×{part.geometry.bbox_z}
                    </span>
                  </div>
                </div>
                {/* Thickness Distribution Chart */}
                <div className="mt-4">
                  <ThicknessChart partId={part.id} />
                </div>
                {/* Reset button */}
                <button
                  onClick={() => { setPart(null); setAnalysisResult(null) }}
                  className="mt-3 text-sm text-blue-600 hover:underline"
                >
                  Upload different part
                </button>
              </div>
            ) : inputMode === 'file' ? (
              <FileUpload projectId={Number(projectId)} onUploaded={handlePartUploaded} />
            ) : (
              <ManualInput projectId={Number(projectId)} onCreated={handlePartUploaded} />
            )}
          </div>

          {/* Material Selection */}
          <div className="bg-white rounded-lg shadow-sm p-4">
            <h2 className="text-lg font-semibold mb-4">Material</h2>
            <MaterialSelect value={materialId} onChange={setMaterialId} />
          </div>

          {/* Analysis Configuration (Designer only) */}
          {viewMode === 'designer' && (
            <div className="bg-white rounded-lg shadow-sm p-4">
              <h2 className="text-lg font-semibold mb-4">Process Configuration</h2>
              <AnalysisConfig config={analysisConfig} onChange={setAnalysisConfig} />
            </div>
          )}

          {/* Run Analysis Button */}
          <button
            onClick={runAnalysis}
            disabled={loading || !part || !materialId}
            className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Analyzing...' : 'Run Analysis'}
          </button>
        </div>

        {/* Right Panel - Results */}
        <div>
          {analysisResult ? (
            <ResultsPanel
              result={analysisResult}
              viewMode={viewMode}
              onGenerateReport={generateReport}
            />
          ) : (
            <div className="bg-white rounded-lg shadow-sm p-8 text-center">
              <div className="text-gray-400 text-4xl mb-4">📊</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Analysis Yet</h3>
              <p className="text-gray-600">
                Upload a part, select a material, and run the analysis to see results
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
