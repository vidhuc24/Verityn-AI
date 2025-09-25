import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { query, document_id, document_type, framework } = body

    // Validate required fields
    if (!query || !document_id) {
      return NextResponse.json(
        { error: 'Query and document_id are required' },
        { status: 400 }
      )
    }

    // Call backend web search API
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000'
    const response = await fetch(`${backendUrl}/api/web-search/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        document_id,
        document_type,
        framework
      }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'Web search failed')
    }

    const searchResults = await response.json()
    return NextResponse.json(searchResults)

  } catch (error) {
    console.error('Web search error:', error)
    return NextResponse.json(
      { 
        error: error instanceof Error ? error.message : 'Web search failed',
        success: false,
        results: [],
        compliance_insights: []
      },
      { status: 500 }
    )
  }
}

export async function GET() {
  // Health check endpoint
  try {
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000'
    const response = await fetch(`${backendUrl}/api/web-search/health`)
    
    if (!response.ok) {
      throw new Error('Web search service unhealthy')
    }

    const healthData = await response.json()
    return NextResponse.json(healthData)

  } catch (error) {
    console.error('Web search health check error:', error)
    return NextResponse.json(
      { 
        status: 'unhealthy',
        service: 'web-search',
        error: error instanceof Error ? error.message : 'Health check failed'
      },
      { status: 500 }
    )
  }
}
