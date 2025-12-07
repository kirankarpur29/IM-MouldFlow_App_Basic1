import FlowVisualization from './FlowVisualization'

interface ResultsPanelProps {
  result: any
  viewMode: 'designer' | 'customer'
  onGenerateReport: (type: string) => void
}

export default function ResultsPanel({ result, viewMode, onGenerateReport }: ResultsPanelProps) {
  const feasibilityColors: Record<string, string> = {
    feasible: 'bg-green-100 text-green-800 border-green-200',
    borderline: 'bg-amber-100 text-amber-800 border-amber-200',
    not_recommended: 'bg-red-100 text-red-800 border-red-200'
  }

  const severityColors: Record<string, string> = {
    low: 'border-blue-400',
    medium: 'border-amber-400',
    high: 'border-red-400'
  }

  return (
    <div className="space-y-4">
      {/* Feasibility Status */}
      <div className={`p-4 rounded-lg border-2 text-center ${feasibilityColors[result.feasibility.status]}`}>
        <div className="text-2xl font-bold mb-1">
          {result.feasibility.status.replace('_', ' ').toUpperCase()}
        </div>
        <div className="text-sm">Score: {result.feasibility.score}/100</div>
      </div>

      {/* Key Metrics */}
      <div className="bg-white rounded-lg shadow-sm p-4">
        <h3 className="font-semibold mb-3">Key Results</h3>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gray-50 p-3 rounded">
            <div className="text-2xl font-bold text-blue-600">
              {result.tonnage.recommended.toFixed(0)}T
            </div>
            <div className="text-xs text-gray-500">Recommended Tonnage</div>
          </div>
          <div className="bg-gray-50 p-3 rounded">
            <div className="text-2xl font-bold text-blue-600">
              {result.cycle_time.total_cycle.toFixed(1)}s
            </div>
            <div className="text-xs text-gray-500">Cycle Time</div>
          </div>
          <div className="bg-gray-50 p-3 rounded">
            <div className="text-2xl font-bold text-blue-600">
              {result.part_weight.toFixed(1)}g
            </div>
            <div className="text-xs text-gray-500">Part Weight</div>
          </div>
          <div className="bg-gray-50 p-3 rounded">
            <div className="text-2xl font-bold text-blue-600">
              {result.injection_pressure.toFixed(0)} MPa
            </div>
            <div className="text-xs text-gray-500">Injection Pressure</div>
          </div>
        </div>
      </div>

      {/* Designer-only details */}
      {viewMode === 'designer' && (
        <>
          {/* Detailed Numbers */}
          <div className="bg-white rounded-lg shadow-sm p-4">
            <h3 className="font-semibold mb-3">Process Details</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Fill Time</span>
                <span className="font-medium">{result.fill_time.toFixed(2)} s</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Cooling Time</span>
                <span className="font-medium">{result.cycle_time.cooling_time.toFixed(1)} s</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Gate Diameter</span>
                <span className="font-medium">{result.gate_diameter.toFixed(2)} mm</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Runner Diameter</span>
                <span className="font-medium">{result.runner_diameter.toFixed(2)} mm</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Tonnage Range</span>
                <span className="font-medium">
                  {result.tonnage.minimum.toFixed(0)} - {result.tonnage.conservative.toFixed(0)} T
                </span>
              </div>
            </div>
          </div>

          {/* Formulas */}
          <div className="bg-white rounded-lg shadow-sm p-4">
            <h3 className="font-semibold mb-3">Calculations</h3>
            <div className="bg-gray-50 p-3 rounded font-mono text-xs">
              <div>Clamp Force = A × n × P × SF</div>
              <div className="mt-1 text-gray-500">
                Reference: Rosato, Injection Molding Handbook
              </div>
            </div>
          </div>
        </>
      )}

      {/* Flow Visualization */}
      {result.part_id && (
        <div className="bg-white rounded-lg shadow-sm p-4">
          <h3 className="font-semibold mb-3">Flow Pattern</h3>
          <FlowVisualization partId={result.part_id} />
        </div>
      )}

      {/* Warnings */}
      {result.warnings && result.warnings.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-4">
          <h3 className="font-semibold mb-3">Warnings & Recommendations</h3>
          <div className="space-y-2">
            {result.warnings.map((warning: any, index: number) => (
              <div
                key={index}
                className={`p-3 border-l-4 bg-gray-50 rounded-r ${severityColors[warning.severity]}`}
              >
                <div className="text-sm">
                  {viewMode === 'customer' ? warning.customer_message : warning.designer_message}
                </div>
                {viewMode === 'designer' && warning.recommendation && (
                  <div className="text-xs text-gray-500 mt-1">
                    → {warning.recommendation}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Machine Recommendations */}
      {result.recommended_machines && result.recommended_machines.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm p-4">
          <h3 className="font-semibold mb-3">Recommended Machines</h3>
          <div className="space-y-2">
            {result.recommended_machines.map((rec: any, index: number) => (
              <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                <div>
                  <div className="font-medium">{rec.machine.name}</div>
                  <div className="text-xs text-gray-500">{rec.machine.tonnage}T</div>
                </div>
                <span className={`px-2 py-1 text-xs rounded ${
                  rec.suitability === 'ideal' ? 'bg-green-100 text-green-700' :
                  rec.suitability === 'acceptable' ? 'bg-blue-100 text-blue-700' :
                  'bg-amber-100 text-amber-700'
                }`}>
                  {rec.suitability}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Report Generation */}
      <div className="bg-white rounded-lg shadow-sm p-4">
        <h3 className="font-semibold mb-3">Generate Report</h3>
        <div className="flex gap-2">
          <button
            onClick={() => onGenerateReport(viewMode)}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Download {viewMode === 'customer' ? 'Customer' : 'Technical'} Report
          </button>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="text-xs text-gray-400 text-center p-2">
        This is an early feasibility tool, not a detailed CAE simulation.
        Results should be verified with full mold flow analysis.
      </div>
    </div>
  )
}
