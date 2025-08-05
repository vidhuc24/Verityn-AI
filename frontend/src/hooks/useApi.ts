import { useState, useCallback } from 'react';
import { api } from '@/lib/api';
import {
  DocumentResponse,
  ChatRequest,
  ChatResponse,
  ChatMessage,
  QuestionSuggestionRequest,
  QuestionSuggestionResponse,
  FileUploadResponse,
  ApiError,
} from '@/types/api';

// Generic hook for API calls with loading and error states
export function useApiCall<T, P extends any[]>(
  apiFunction: (...args: P) => Promise<T>
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);

  const execute = useCallback(
    async (...args: P) => {
      setLoading(true);
      setError(null);
      try {
        const result = await apiFunction(...args);
        setData(result);
        return result;
      } catch (err) {
        const apiError = err as ApiError;
        setError(apiError);
        throw apiError;
      } finally {
        setLoading(false);
      }
    },
    [apiFunction]
  );

  return { data, loading, error, execute };
}

// Document upload hook
export function useDocumentUpload() {
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<FileUploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const uploadDocument = useCallback(async (file: File, description?: string) => {
    setUploading(true);
    setError(null);
    try {
      const result = await api.uploadDocument(file, description);
      setUploadResult(result);
      if (!result.success) {
        setError(result.error || 'Upload failed');
      }
      return result;
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.error);
      throw apiError;
    } finally {
      setUploading(false);
    }
  }, []);

  return { uploading, uploadResult, error, uploadDocument };
}

// Chat hook
export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sending, setSending] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);

  const sendMessage = useCallback(async (request: ChatRequest) => {
    setSending(true);
    try {
      const response = await api.sendChatMessage(request);
      
      // Add messages to the conversation
      const newMessages = [...messages];
      newMessages.push({ role: 'user', content: request.message });
      newMessages.push(response.message);
      
      setMessages(newMessages);
      setConversationId(response.conversation_id);
      
      return response;
    } catch (err) {
      console.error('Chat error:', err);
      throw err;
    } finally {
      setSending(false);
    }
  }, [messages]);

  const clearConversation = useCallback(() => {
    setMessages([]);
    setConversationId(null);
  }, []);

  return {
    messages,
    sending,
    conversationId,
    sendMessage,
    clearConversation,
  };
}

// Question suggestions hook
export function useQuestionSuggestions() {
  const [suggestions, setSuggestions] = useState<QuestionSuggestionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getSuggestions = useCallback(async (request: QuestionSuggestionRequest) => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.getQuestionSuggestions(request);
      setSuggestions(result);
      return result;
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.error);
      throw apiError;
    } finally {
      setLoading(false);
    }
  }, []);

  return { suggestions, loading, error, getSuggestions };
}

// Documents list hook
export function useDocuments() {
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = useCallback(async (skip = 0, limit = 100) => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.getDocuments(skip, limit);
      setDocuments(result);
      return result;
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.error);
      throw apiError;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteDocument = useCallback(async (documentId: string) => {
    try {
      await api.deleteDocument(documentId);
      // Remove from local state
      setDocuments(prev => prev.filter(doc => doc.document_id !== documentId));
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.error);
      throw apiError;
    }
  }, []);

  return { documents, loading, error, fetchDocuments, deleteDocument };
}

// Health check hook
export function useHealthCheck() {
  return useApiCall(api.health);
} 