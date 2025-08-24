import { Lightbulb, ArrowRight, MessageSquare } from 'lucide-react'

interface QuestionSuggestionsProps {
  documentType: string
  complianceFramework: string
  onQuestionSelect: (question: string) => void
}

export default function QuestionSuggestions({ 
  documentType, 
  complianceFramework, 
  onQuestionSelect 
}: QuestionSuggestionsProps) {
  // Generate contextual questions based on document type and framework
  const generateQuestions = () => {
    const baseQuestions = [
      "What are the main compliance issues identified in this document?",
      "Which controls are deficient and what are the implications?",
      "What remediation steps are recommended?",
      "What is the overall risk assessment?",
      "Are there any material weaknesses identified?"
    ]

    const typeSpecificQuestions = {
      'access review': [
        "What access control deficiencies were found?",
        "Which users have excessive privileges?",
        "What segregation of duties issues exist?",
        "How many orphaned accounts were identified?"
      ],
      'risk assessment': [
        "What are the highest risk areas identified?",
        "Which controls are most critical?",
        "What is the likelihood vs impact analysis?",
        "Are there any emerging risks mentioned?"
      ],
      'financial reconciliation': [
        "What reconciliation discrepancies exist?",
        "Which accounts have outstanding items?",
        "What is the financial impact of findings?",
        "Are there any material misstatements?"
      ]
    }

    const frameworkSpecificQuestions = {
      'sox': [
        "Which SOX controls are deficient?",
        "What are the control objectives not met?",
        "Are there any material weaknesses in internal controls?",
        "What is the impact on financial reporting?"
      ],
      'pci-dss': [
        "Which PCI-DSS requirements are not met?",
        "What are the data security gaps?",
        "Are there any vulnerabilities in cardholder data handling?",
        "What is the compliance level assessment?"
      ],
      'iso 27001': [
        "Which information security controls are weak?",
        "What are the security policy gaps?",
        "Are there any asset management issues?",
        "What is the risk treatment status?"
      ]
    }

    const type = documentType?.toLowerCase() || ''
    const framework = complianceFramework?.toLowerCase() || ''

    let questions = [...baseQuestions]

    // Add type-specific questions
    for (const [key, typeQuestions] of Object.entries(typeSpecificQuestions)) {
      if (type.includes(key)) {
        questions = [...questions, ...typeQuestions]
        break
      }
    }

    // Add framework-specific questions
    for (const [key, frameworkQuestions] of Object.entries(frameworkSpecificQuestions)) {
      if (framework.includes(key)) {
        questions = [...questions, ...frameworkQuestions]
        break
      }
    }

    return questions.slice(0, 8) // Limit to 8 questions
  }

  const questions = generateQuestions()

  return (
    <div>
      <div className="flex items-center space-x-2 mb-4">
        <Lightbulb className="h-5 w-5 text-[#9600FF]" />
        <h3 className="text-lg font-semibold" style={{ color: '#E0E0E0' }}>Smart Questions</h3>
      </div>
      <p className="text-sm mb-4" style={{ color: '#A0A0A0' }}>
        AI-suggested questions to help you explore your document insights
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {questions.map((question, index) => (
          <button
            key={index}
            onClick={() => onQuestionSelect(question)}
            className="group relative p-4 text-left rounded-lg border transition-all duration-200 hover:shadow-sm"
            style={{ 
              backgroundColor: '#1A1A1A', 
              borderColor: '#A0A0A0',
              borderWidth: '1px'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = '#9600FF'
              e.currentTarget.style.backgroundColor = '#9600FF10'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = '#A0A0A0'
              e.currentTarget.style.backgroundColor = '#1A1A1A'
            }}
          >
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 mt-1">
                <MessageSquare className="h-4 w-4" style={{ color: '#A0A0A0' }} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium transition-colors" style={{ color: '#E0E0E0' }}>
                  {question}
                </p>
              </div>
              <div className="flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
                <ArrowRight className="h-4 w-4 text-[#9600FF]" />
              </div>
            </div>
          </button>
        ))}
      </div>
      
      <div className="mt-6 p-4 rounded-lg border" style={{ backgroundColor: '#9600FF10', borderColor: '#9600FF' }}>
        <div className="flex items-start space-x-3">
          <Lightbulb className="h-5 w-5 text-[#9600FF] flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium mb-1" style={{ color: '#E0E0E0' }}>
              Pro Tip
            </p>
            <p className="text-sm" style={{ color: '#A0A0A0' }}>
              Click on any question above to automatically send it to the chat interface. 
              You can also ask your own custom questions in the chat below.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
} 