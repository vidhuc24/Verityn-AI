import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const { message, document_id, conversation_id } = await request.json()
    
    if (!message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      )
    }

    // Call backend multi-agent workflow for chat
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    const response = await fetch(`${backendUrl}/workflow/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: message,
        document_id: document_id,
        conversation_id: conversation_id,
        include_web_search: true
      }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      return NextResponse.json(
        { error: errorData.detail || 'Chat failed' },
        { status: response.status }
      )
    }

    const result = await response.json()
    
    // Extract chat response from multi-agent workflow
    const chatResponse = {
      response: result.response || 'No response generated',
      conversation_id: result.conversation_id,
      sources: result.metadata?.sources || [],
      confidence: result.metadata?.confidence || 0.0,
      workflow_id: result.workflow_id,
      execution_time: result.metadata?.execution_time || 0
    }
    
    return NextResponse.json({
      success: true,
      chat: chatResponse,
      message: 'Chat response generated successfully'
    })

  } catch (error) {
    console.error('Chat error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
} 