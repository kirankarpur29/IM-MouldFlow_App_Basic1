interface AnalysisConfigProps {
  config: {
    cavity_count: number
    gate_type: string
    safety_factor: number
  }
  onChange: (config: any) => void
}

export default function AnalysisConfig({ config, onChange }: AnalysisConfigProps) {
  return (
    <div className="space-y-4">
      {/* Cavity Count */}
      <div>
        <label className="block text-sm text-gray-600 mb-1">Number of Cavities</label>
        <select
          value={config.cavity_count}
          onChange={(e) => onChange({ ...config, cavity_count: Number(e.target.value) })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
        >
          {[1, 2, 4, 8, 16].map(n => (
            <option key={n} value={n}>{n} {n === 1 ? 'cavity' : 'cavities'}</option>
          ))}
        </select>
      </div>

      {/* Gate Type */}
      <div>
        <label className="block text-sm text-gray-600 mb-1">Gate Type</label>
        <select
          value={config.gate_type}
          onChange={(e) => onChange({ ...config, gate_type: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
        >
          <option value="edge">Edge Gate</option>
          <option value="pin">Pin Gate</option>
          <option value="fan">Fan Gate</option>
          <option value="submarine">Submarine Gate</option>
        </select>
        <p className="text-xs text-gray-500 mt-1">
          {config.gate_type === 'edge' && 'Standard gate for most applications'}
          {config.gate_type === 'pin' && 'Small parts, minimal gate vestige'}
          {config.gate_type === 'fan' && 'Large flat parts, uniform flow'}
          {config.gate_type === 'submarine' && 'Auto-degating, hidden gate mark'}
        </p>
      </div>

      {/* Safety Factor */}
      <div>
        <label className="block text-sm text-gray-600 mb-1">
          Safety Factor: {config.safety_factor}
        </label>
        <input
          type="range"
          min="1.0"
          max="1.5"
          step="0.05"
          value={config.safety_factor}
          onChange={(e) => onChange({ ...config, safety_factor: Number(e.target.value) })}
          className="w-full"
        />
        <div className="flex justify-between text-xs text-gray-400">
          <span>1.0 (min)</span>
          <span>1.25 (typical)</span>
          <span>1.5 (conservative)</span>
        </div>
      </div>
    </div>
  )
}
