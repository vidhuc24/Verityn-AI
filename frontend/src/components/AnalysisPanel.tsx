interface AnalysisPanelProps {
  results: any
  isAnalyzing: boolean
}

export default function AnalysisPanel({ results, isAnalyzing }: AnalysisPanelProps) {
  if (isAnalyzing) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="card">
            <div className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded mb-2"></div>
              <div className="h-6 bg-gray-200 rounded"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (!results) return null

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="card">
        <div className="flex items-center space-x-3">
          <div className="bg-blue-100 p-2 rounded-lg">
            <span className="text-blue-600 font-bold">📄</span>
          </div>
          <div>
            <p className="text-sm text-gray-600">Document Type</p>
            <p className="text-lg font-semibold text-gray-900">
              {results.documentType}
            </p>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="flex items-center space-x-3">
          <div className="bg-green-100 p-2 rounded-lg">
            <span className="text-green-600 font-bold">✓</span>
          </div>
          <div>
            <p className="text-sm text-gray-600">Compliance Framework</p>
            <p className="text-lg font-semibold text-gray-900">
              {results.complianceFramework}
            </p>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${
            results.riskLevel === 'High' ? 'bg-red-100' :
            results.riskLevel === 'Medium' ? 'bg-yellow-100' : 'bg-green-100'
          }`}>
            <span className={`font-bold ${
              results.riskLevel === 'High' ? 'text-red-600' :
              results.riskLevel === 'Medium' ? 'text-yellow-600' : 'text-green-600'
            }`}>
              ⚠️
            </span>
          </div>
          <div>
            <p className="text-sm text-gray-600">Risk Level</p>
            <p className="text-lg font-semibold text-gray-900">
              {results.riskLevel}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
} 