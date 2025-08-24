import { Shield, AlertTriangle, CheckCircle } from 'lucide-react';

export function AnalysisCards() {
  const analysisData = [
    {
      title: 'Compliance Score',
      value: '94%',
      status: 'good',
      icon: Shield,
      description: 'High compliance level detected'
    },
    {
      title: 'Risk Factors',
      value: '3',
      status: 'warning',
      icon: AlertTriangle,
      description: 'Minor issues identified'
    },
    {
      title: 'Key Requirements',
      value: '12',
      status: 'good',
      icon: CheckCircle,
      description: 'Requirements extracted'
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'good':
        return 'text-green-500';
      case 'warning':
        return 'text-yellow-500';
      case 'danger':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  return (
    <div className="mb-6">
      <h3 className="mb-4" style={{ color: '#E0E0E0' }}>Document Analysis</h3>
      <div className="grid grid-cols-3 gap-4">
        {analysisData.map((item, index) => (
          <div 
            key={index}
            className="rounded-xl p-4 border border-[#A0A0A0]/20 hover:border-[#9600FF]/50 transition-all duration-300"
            style={{ backgroundColor: '#1A1A1A' }}
          >
            <div className="flex items-center gap-3 mb-3">
              <div className={`w-8 h-8 rounded-lg bg-gradient-to-r from-[#9600FF] to-[#4600C8] flex items-center justify-center`}>
                <item.icon className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-sm" style={{ color: '#A0A0A0' }}>
                  {item.title}
                </p>
                <p className="text-xl font-semibold" style={{ color: '#E0E0E0' }}>
                  {item.value}
                </p>
              </div>
            </div>
            <p className={`text-sm ${getStatusColor(item.status)}`}>
              {item.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}