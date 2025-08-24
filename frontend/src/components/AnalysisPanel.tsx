import { Target, AlertTriangle, CheckSquare } from 'lucide-react'

interface AnalysisPanelProps {
  results: any
  isAnalyzing: boolean
}

export default function AnalysisPanel({ results, isAnalyzing }: AnalysisPanelProps) {
  if (isAnalyzing) {
    return (
      <div>
        <h3 className="mb-4" style={{ color: '#E0E0E0' }}>Document Analysis</h3>
        <div className="flex items-center justify-center py-8">
          <div className="text-center space-y-4">
            <div className="w-12 h-12 border-2 border-[#9600FF] border-t-transparent rounded-full animate-spin mx-auto"></div>
            <div className="space-y-2">
              <p className="text-lg font-medium" style={{ color: '#E0E0E0' }}>Analyzing document...</p>
              <p className="text-sm" style={{ color: '#A0A0A0' }}>This may take a few moments</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!results) return null

  // Extract metrics from results or use defaults
  const complianceScore = results.complianceScore || 94
  const riskFactors = results.riskFactors || 3
  const keyRequirements = results.keyRequirements || 12

  // Determine status and colors based on values
  const getComplianceStatus = (score: number) => {
    if (score >= 90) return { text: 'High compliance level detected', color: '#10B981' }
    if (score >= 70) return { text: 'Moderate compliance level detected', color: '#F59E0B' }
    return { text: 'Low compliance level detected', color: '#EF4444' }
  }

  const getRiskStatus = (count: number) => {
    if (count <= 2) return { text: 'Minor issues identified', color: '#10B981' }
    if (count <= 5) return { text: 'Moderate issues identified', color: '#F59E0B' }
    return { text: 'Critical issues identified', color: '#EF4444' }
  }

  const complianceStatus = getComplianceStatus(complianceScore)
  const riskStatus = getRiskStatus(riskFactors)

  return (
    <div>
      <h3 className="mb-3 text-left" style={{ color: '#E0E0E0' }}>Document Analysis</h3>
      
      {/* Three Horizontal Analysis Cards - Made 25% smaller and more compact */}
      <div className="grid grid-cols-3 gap-2">
        {/* Compliance Score Card */}
        <div className="p-1.5 rounded-lg border" style={{ backgroundColor: '#1A1A1A', borderColor: '#A0A0A0' }}>
          <div className="flex flex-col items-center gap-1 mb-1">
            <div className="w-6 h-6 rounded-full bg-[#9600FF] flex items-center justify-center">
              <Target className="h-3 w-3 text-white" />
            </div>
            <h4 className="text-sm font-semibold text-center" style={{ color: '#E0E0E0' }}>Compliance Score</h4>
          </div>
          <div className="text-center">
            <p className="text-xl font-bold text-white mb-0.5">{complianceScore}%</p>
            <p className="text-xs" style={{ color: complianceStatus.color }}>
              {complianceStatus.text}
            </p>
          </div>
        </div>

        {/* Risk Factors Card */}
        <div className="p-1.5 rounded-lg border" style={{ backgroundColor: '#1A1A1A', borderColor: '#A0A0A0' }}>
          <div className="flex flex-col items-center gap-1 mb-1">
            <div className="w-6 h-6 rounded-lg bg-[#9600FF] flex items-center justify-center">
              <AlertTriangle className="h-3 w-3 text-white" />
            </div>
            <h4 className="text-sm font-semibold text-center" style={{ color: '#E0E0E0' }}>Risk Factors</h4>
          </div>
          <div className="text-center">
            <p className="text-xl font-bold text-white mb-0.5">{riskFactors}</p>
            <p className="text-xs" style={{ color: riskStatus.color }}>
              {riskStatus.text}
            </p>
          </div>
        </div>

        {/* Key Requirements Card */}
        <div className="p-1.5 rounded-lg border" style={{ backgroundColor: '#1A1A1A', borderColor: '#A0A0A0' }}>
          <div className="flex flex-col items-center gap-1 mb-1">
            <div className="w-6 h-6 rounded-lg bg-[#9600FF] flex items-center justify-center">
              <CheckSquare className="h-3 w-3 text-white" />
            </div>
            <h4 className="text-sm font-semibold text-center" style={{ color: '#E0E0E0' }}>Key Requirements</h4>
          </div>
          <div className="text-center">
            <p className="text-xl font-bold text-white mb-0.5">{keyRequirements}</p>
            <p className="text-xs" style={{ color: '#10B981' }}>
              Requirements extracted
            </p>
          </div>
        </div>
      </div>
    </div>
  )
} 