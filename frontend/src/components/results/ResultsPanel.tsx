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
    <div className="space-y-6">
      {/* Feasibility Status - Enhanced */}
      <div className={`p-6 rounded-2xl border-2 text-center shadow-lg ${feasibilityColors[result.feasibility.status]}`}>
        <div className="text-xs font-semibold uppercase tracking-wider mb-2 opacity-75">
          Feasibility Assessment
        </div>
        <div className="text-3xl font-bold mb-2">
          {result.feasibility.status.replace('_', ' ').toUpperCase()}
        </div>
        <div className="text-sm font-medium">
          Confidence Score: {result.feasibility.score}/100
        </div>
      </div>

      {/* Key Metrics - Enhanced with gradients */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
        <div className="flex items-center gap-2 mb-5">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-lg flex items-center justify-center">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h3 className="text-lg font-bold text-gray-900">Key Results</h3>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-4 rounded-xl border border-blue-100">
            <div className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              {result.tonnage.recommended.toFixed(0)}T
            </div>
            <div className="text-xs text-gray-600 font-medium mt-1">Recommended Tonnage</div>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-pink-50 p-4 rounded-xl border border-purple-100">
            <div className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              {result.cycle_time.total_cycle.toFixed(1)}s
            </div>
            <div className="text-xs text-gray-600 font-medium mt-1">Cycle Time</div>
          </div>
          <div className="bg-gradient-to-br from-emerald-50 to-teal-50 p-4 rounded-xl border border-emerald-100">
            <div className="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
              {result.part_weight.toFixed(1)}g
            </div>
            <div className="text-xs text-gray-600 font-medium mt-1">Part Weight</div>
          </div>
          <div className="bg-gradient-to-br from-amber-50 to-orange-50 p-4 rounded-xl border border-amber-100">
            <div className="text-3xl font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
              {result.injection_pressure.toFixed(0)} MPa
            </div>
            <div className="text-xs text-gray-600 font-medium mt-1">Injection Pressure</div>
          </div>
        </div>
      </div>

      {/* Designer-only details */}
      {viewMode === 'designer' && (
        <>
          {/* Detailed Numbers - Enhanced */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
            <div className="flex items-center gap-2 mb-5">
              <div className="w-8 h-8 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                </svg>
              </div>
              <h3 className="text-lg font-bold text-gray-900">Process Details</h3>
            </div>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg">
                <span className="text-gray-700 font-medium">Fill Time</span>
                <span className="font-bold text-blue-600">{result.fill_time.toFixed(2)} s</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-gray-50 to-purple-50 rounded-lg">
                <span className="text-gray-700 font-medium">Cooling Time</span>
                <span className="font-bold text-purple-600">{result.cycle_time.cooling_time.toFixed(1)} s</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-gray-50 to-emerald-50 rounded-lg">
                <span className="text-gray-700 font-medium">Gate Diameter</span>
                <span className="font-bold text-emerald-600">{result.gate_diameter.toFixed(2)} mm</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-gray-50 to-teal-50 rounded-lg">
                <span className="text-gray-700 font-medium">Runner Diameter</span>
                <span className="font-bold text-teal-600">{result.runner_diameter.toFixed(2)} mm</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-gradient-to-r from-gray-50 to-amber-50 rounded-lg">
                <span className="text-gray-700 font-medium">Tonnage Range</span>
                <span className="font-bold text-amber-600">
                  {result.tonnage.minimum.toFixed(0)} - {result.tonnage.conservative.toFixed(0)} T
                </span>
              </div>
            </div>
          </div>

          {/* Formulas - Enhanced */}
          <div className="bg-gradient-to-br from-slate-900 to-blue-900 rounded-2xl shadow-lg p-6 text-white">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-lg font-bold">Engineering Calculations</h3>
            </div>
            <div className="bg-white/10 backdrop-blur-sm p-4 rounded-xl border border-white/20">
              <div className="font-mono text-sm font-semibold mb-2">
                Clamp Force = A × n × P × SF
              </div>
              <div className="text-xs text-blue-200">
                Reference: Rosato, Injection Molding Handbook
              </div>
            </div>
          </div>
        </>
      )}

      {/* Flow Visualization */}
      {result.part_id && (
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <div className="flex items-center gap-2 mb-5">
            <div className="w-8 h-8 bg-gradient-to-br from-cyan-100 to-blue-100 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-cyan-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-gray-900">Flow Pattern</h3>
          </div>
          <FlowVisualization partId={result.part_id} />
        </div>
      )}

      {/* Warnings */}
      {result.warnings && result.warnings.length > 0 && (
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <div className="flex items-center gap-2 mb-5">
            <div className="w-8 h-8 bg-gradient-to-br from-amber-100 to-orange-100 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-gray-900">Warnings & Recommendations</h3>
          </div>
          <div className="space-y-3">
            {result.warnings.map((warning: any, index: number) => (
              <div
                key={index}
                className={`p-4 border-l-4 bg-gradient-to-r from-gray-50 to-white rounded-r-xl ${severityColors[warning.severity]}`}
              >
                <div className="text-sm font-medium text-gray-900">
                  {viewMode === 'customer' ? warning.customer_message : warning.designer_message}
                </div>
                {viewMode === 'designer' && warning.recommendation && (
                  <div className="text-xs text-gray-600 mt-2 flex items-start gap-1">
                    <span className="text-blue-500 font-bold">→</span>
                    {warning.recommendation}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Machine Recommendations */}
      {result.recommended_machines && result.recommended_machines.length > 0 && (
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6">
          <div className="flex items-center gap-2 mb-5">
            <div className="w-8 h-8 bg-gradient-to-br from-green-100 to-emerald-100 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-gray-900">Recommended Machines</h3>
          </div>
          <div className="space-y-3">
            {result.recommended_machines.map((rec: any, index: number) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-green-50 rounded-xl border border-gray-100 hover:shadow-md transition-shadow">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-green-100 to-emerald-100 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                    </svg>
                  </div>
                  <div>
                    <div className="font-bold text-gray-900">{rec.machine.name}</div>
                    <div className="text-sm text-gray-600">{rec.machine.tonnage}T Capacity</div>
                  </div>
                </div>
                <span className={`px-3 py-1.5 text-xs font-bold rounded-full ${
                  rec.suitability === 'ideal' ? 'bg-green-100 text-green-700 border border-green-200' :
                  rec.suitability === 'acceptable' ? 'bg-blue-100 text-blue-700 border border-blue-200' :
                  'bg-amber-100 text-amber-700 border border-amber-200'
                }`}>
                  {rec.suitability}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Report Generation */}
      <div className="bg-gradient-to-br from-indigo-600 to-purple-600 rounded-2xl shadow-xl p-6 text-white">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 bg-white/20 backdrop-blur-sm rounded-lg flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-bold">Generate Report</h3>
        </div>
        <button
          onClick={() => onGenerateReport(viewMode)}
          className="w-full px-6 py-3 bg-white text-indigo-600 rounded-xl hover:bg-blue-50 transition-all duration-200 font-bold shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 flex items-center justify-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
          </svg>
          Download {viewMode === 'customer' ? 'Customer Summary' : 'Technical'} Report (PDF)
        </button>
      </div>

      {/* Disclaimer */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-center">
        <p className="text-xs text-blue-700 font-medium">
          ⚠️ This is an early feasibility assessment tool, not a detailed CAE simulation.
        </p>
        <p className="text-xs text-blue-600 mt-1">
          Results should be verified with full mold flow analysis before finalizing tool design.
        </p>
      </div>
    </div>
  )
}
