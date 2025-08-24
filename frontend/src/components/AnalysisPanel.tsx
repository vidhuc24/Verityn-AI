import { CheckCircle, AlertTriangle, Info, Clock, FileText, Shield, TrendingUp } from 'lucide-react'

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

  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'compliant':
      case 'pass':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'non-compliant':
      case 'fail':
        return <AlertTriangle className="h-5 w-5 text-red-500" />
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />
      default:
        return <Info className="h-5 w-5 text-blue-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'compliant':
      case 'pass':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'non-compliant':
      case 'fail':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200'
    }
  }

  return (
    <div className="space-y-6">
      {/* Document Overview */}
      <div>
        <h3 className="mb-4" style={{ color: '#E0E0E0' }}>Document Overview</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="flex items-center space-x-3 p-4 rounded-lg" style={{ backgroundColor: '#1A1A1A' }}>
            <FileText className="h-5 w-5 text-[#9600FF]" />
            <div>
              <p className="text-sm font-medium" style={{ color: '#E0E0E0' }}>Document Type</p>
              <p className="text-sm capitalize" style={{ color: '#A0A0A0' }}>
                {results.documentType || 'Unknown'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 p-4 rounded-lg" style={{ backgroundColor: '#1A1A1A' }}>
            <Shield className="h-5 w-5 text-[#9600FF]" />
            <div>
              <p className="text-sm font-medium" style={{ color: '#E0E0E0' }}>Framework</p>
              <p className="text-sm" style={{ color: '#A0A0A0' }}>
                {results.complianceFramework || 'Not specified'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 p-4 rounded-lg" style={{ backgroundColor: '#1A1A1A' }}>
            <Clock className="h-5 w-5 text-[#9600FF]" />
            <div>
              <p className="text-sm font-medium" style={{ color: '#E0E0E0' }}>Analysis Date</p>
              <p className="text-sm" style={{ color: '#A0A0A0' }}>
                {new Date().toLocaleDateString()}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3 p-4 rounded-lg" style={{ backgroundColor: '#1A1A1A' }}>
            <TrendingUp className="h-5 w-5 text-[#9600FF]" />
            <div>
              <p className="text-sm font-medium" style={{ color: '#E0E0E0' }}>Confidence</p>
              <p className="text-sm" style={{ color: '#A0A0A0' }}>
                {results.confidence ? `${Math.round(results.confidence * 100)}%` : 'High'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Key Findings */}
      {results.findings && (
        <div>
          <h3 className="mb-4" style={{ color: '#E0E0E0' }}>Key Findings</h3>
          <div className="space-y-4">
            {Array.isArray(results.findings) ? (
              results.findings.map((finding: any, index: number) => (
                <div key={index} className="flex items-start space-x-3 p-4 rounded-lg" style={{ backgroundColor: '#1A1A1A' }}>
                  {getStatusIcon(finding.status)}
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h4 className="font-medium" style={{ color: '#E0E0E0' }}>{finding.title}</h4>
                      <span className={`badge ${getStatusColor(finding.status)}`}>
                        {finding.status}
                      </span>
                    </div>
                    <p className="text-sm" style={{ color: '#A0A0A0' }}>{finding.description}</p>
                    {finding.recommendation && (
                      <div className="mt-2 p-3 rounded border" style={{ backgroundColor: '#282828', borderColor: '#A0A0A0' }}>
                        <p className="text-sm font-medium mb-1" style={{ color: '#E0E0E0' }}>Recommendation:</p>
                        <p className="text-sm" style={{ color: '#A0A0A0' }}>{finding.recommendation}</p>
                      </div>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8" style={{ color: '#A0A0A0' }}>
                <Info className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No specific findings available</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Compliance Summary */}
      {results.complianceSummary && (
        <div>
          <h3 className="mb-4" style={{ color: '#E0E0E0' }}>Compliance Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-6 rounded-lg border" style={{ backgroundColor: '#1A1A1A', borderColor: '#A0A0A0' }}>
              <CheckCircle className="h-8 w-8 text-green-500 mx-auto mb-2" />
              <p className="text-2xl font-bold text-green-500">
                {results.complianceSummary.compliant || 0}
              </p>
              <p className="text-sm" style={{ color: '#A0A0A0' }}>Compliant Items</p>
            </div>
            
            <div className="text-center p-6 rounded-lg border" style={{ backgroundColor: '#1A1A1A', borderColor: '#A0A0A0' }}>
              <AlertTriangle className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
              <p className="text-2xl font-bold text-yellow-500">
                {results.complianceSummary.warnings || 0}
              </p>
              <p className="text-sm" style={{ color: '#A0A0A0' }}>Warnings</p>
            </div>
            
            <div className="text-center p-6 rounded-lg border" style={{ backgroundColor: '#1A1A1A', borderColor: '#A0A0A0' }}>
              <AlertTriangle className="h-8 w-8 text-red-500 mx-auto mb-2" />
              <p className="text-2xl font-bold text-red-500">
                {results.complianceSummary.nonCompliant || 0}
              </p>
              <p className="text-sm" style={{ color: '#A0A0A0' }}>Non-Compliant</p>
            </div>
          </div>
        </div>
      )}

      {/* Additional Analysis Data */}
      {results.additionalData && (
        <div>
          <h3 className="mb-4" style={{ color: '#E0E0E0' }}>Additional Analysis</h3>
          <div className="p-4 rounded-lg" style={{ backgroundColor: '#1A1A1A' }}>
            <pre className="text-sm overflow-x-auto" style={{ color: '#A0A0A0' }}>
              {JSON.stringify(results.additionalData, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  )
} 