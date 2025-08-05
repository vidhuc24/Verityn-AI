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
  const getQuestions = () => {
    const baseQuestions = [
      "What are the key findings in this document?",
      "What compliance requirements are addressed?",
      "Are there any material weaknesses identified?",
      "What remediation actions are recommended?"
    ]

    if (documentType === 'Access Review') {
      return [
        "What SOX controls are relevant to this access review?",
        "Are there any segregation of duties violations?",
        "What user access issues were identified?",
        "How effective are the current access controls?"
      ]
    }

    return baseQuestions
  }

  const questions = getQuestions()

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {questions.map((question, index) => (
        <button
          key={index}
          onClick={() => onQuestionSelect(question)}
          className="card hover:shadow-md transition-shadow duration-200 text-left p-4 border-2 border-transparent hover:border-blue-200"
        >
          <div className="flex items-start space-x-3">
            <div className="bg-blue-100 p-1 rounded">
              <span className="text-blue-600 text-sm">💡</span>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">
                {question}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Click to ask this question
              </p>
            </div>
          </div>
        </button>
      ))}
    </div>
  )
} 