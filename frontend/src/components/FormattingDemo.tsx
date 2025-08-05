import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

// Demo component to showcase the new formatting
export default function FormattingDemo() {
  const demoResponse = `## 📋 Executive Summary
Based on the audit findings, this organization has several material weaknesses in their internal controls that require immediate attention.

## 🔍 Key Findings
- **Material Weakness #1**: Inadequate segregation of duties in the accounts payable process
- **Material Weakness #2**: Missing documentation for key control activities
- **Control Deficiency**: Insufficient monitoring of system access controls

## ⚠️ Risk Assessment
**Risk Level**: High
**Rationale**: Multiple material weaknesses indicate significant control gaps that could lead to financial misstatements or fraud.

## 📊 Compliance Framework
- **Framework**: SOX 404 - Internal Control over Financial Reporting
- **Control IDs**: COSO Principle 9, COSO Principle 10
- **Requirements**: Management assessment of internal controls effectiveness

## 🎯 Recommendations
1. **Immediate Actions**: 
   - Implement dual approval for all vendor payments over $10,000
   - Establish weekly access control reviews
2. **Short-term**: 
   - Develop comprehensive control documentation
   - Implement automated monitoring tools
3. **Long-term**: 
   - Establish continuous monitoring program
   - Regular control effectiveness assessments

## 📚 Source References
- Audit Report Section 3.2: Internal Control Deficiencies
- Management Letter: Recommendations for Improvement
- Testing Results: Accounts Payable Process Review`

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">🎨 AI Response Formatting Demo</h2>
      <p className="text-gray-600 mb-4">
        This demonstrates the new structured formatting for AI responses in the chat interface.
      </p>
      
      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <div className="chat-markdown">
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              h2: ({children}) => (
                <h2 className="text-lg font-semibold text-gray-900 mt-4 mb-2 first:mt-0">
                  {children}
                </h2>
              ),
              h3: ({children}) => (
                <h3 className="text-base font-medium text-gray-800 mt-3 mb-1">
                  {children}
                </h3>
              ),
              ul: ({children}) => (
                <ul className="list-disc list-inside space-y-1 my-2">
                  {children}
                </ul>
              ),
              ol: ({children}) => (
                <ol className="list-decimal list-inside space-y-1 my-2">
                  {children}
                </ol>
              ),
              li: ({children}) => (
                <li className="text-sm text-gray-700">
                  {children}
                </li>
              ),
              p: ({children}) => (
                <p className="text-sm text-gray-700 mb-2 last:mb-0">
                  {children}
                </p>
              ),
              strong: ({children}) => (
                <strong className="font-semibold text-gray-900">
                  {children}
                </strong>
              ),
              em: ({children}) => (
                <em className="italic text-gray-800">
                  {children}
                </em>
              ),
              blockquote: ({children}) => (
                <blockquote className="border-l-4 border-blue-500 pl-4 py-2 my-3 bg-blue-50">
                  {children}
                </blockquote>
              ),
              code: ({children}) => (
                <code className="bg-gray-100 px-1 py-0.5 rounded text-xs font-mono">
                  {children}
                </code>
              ),
              pre: ({children}) => (
                <pre className="bg-gray-100 p-3 rounded text-xs font-mono overflow-x-auto">
                  {children}
                </pre>
              ),
            }}
          >
            {demoResponse}
          </ReactMarkdown>
        </div>
      </div>
      
      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <h3 className="font-medium text-blue-900 mb-2">✨ Key Improvements</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Structured sections with clear headers and icons</li>
          <li>• Better visual hierarchy with proper spacing</li>
          <li>• Markdown rendering for lists, emphasis, and formatting</li>
          <li>• Professional styling suitable for audit reports</li>
          <li>• Consistent formatting across all AI responses</li>
        </ul>
      </div>
    </div>
  )
} 