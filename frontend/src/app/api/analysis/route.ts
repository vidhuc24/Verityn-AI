import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { document_id } = await request.json()
    
    if (!document_id) {
      return NextResponse.json(
        { error: 'Document ID is required' },
        { status: 400 }
      )
    }

    // Call backend multi-agent workflow
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const response = await fetch(`${backendUrl}/workflow/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        document_id: document_id,
        analysis_type: 'classification'
      }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      return NextResponse.json(
        { error: errorData.detail || 'Analysis failed' },
        { status: response.status }
      )
    }

    const result = await response.json()
    
    // Extract analysis results from multi-agent workflow
    const analysisResults = {
      documentType: result.classification?.document_type || 'Unknown',
      complianceFramework: result.classification?.compliance_framework || 'Unknown',
      riskLevel: result.classification?.risk_level || 'Unknown',
      confidence: result.classification?.confidence || 0.0,
      metadata: result.classification?.metadata || {}
    }
    
    return NextResponse.json({
      success: true,
      analysis: analysisResults,
      workflow_id: result.workflow_id,
      message: 'Document analysis completed'
    })

  } catch (error) {
    console.error('Analysis error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
} 