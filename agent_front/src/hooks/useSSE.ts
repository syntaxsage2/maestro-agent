import type { SSEEvent, ChatRequest } from '../types/api';
import { getStreamChatUrl } from '../api/chat';

interface UseSSEOptions {
  onEvent: (event: SSEEvent) => void;
  onError?: (error: Error) => void;
  onComplete?: () => void;
}

export const useSSE = () => {
  const streamChat = async (
    request: ChatRequest,
    options: UseSSEOptions
  ): Promise<void> => {
    const { onEvent, onError, onComplete } = options;
    const url = getStreamChatUrl();

    console.log('🚀 Starting NO-RETRY SSE connection:', url);
    console.log('📤 Request:', request);

    let abortController: AbortController | null = new AbortController();
    let isCompleted = false;

    const handleComplete = () => {
      if (!isCompleted) {
        isCompleted = true;
        onComplete?.();
      }
    };

    try {
      const token = localStorage.getItem('access_token');
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      };

      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify(request),
        signal: abortController.signal,
      });

      if (!response.ok) {
        const text = await response.text();
        throw new Error(`SSE connection failed: ${response.status} ${text}`);
      }
      
      if (!response.body) {
         throw new Error('ReadableStream not yet supported in this browser.');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          console.log('✅ SSE stream finished cleanly by server.');
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        
        // Process complete chunks
        const lines = buffer.split('\n');
        // Keep the last partial line in the buffer
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim() === '') continue; // Skip empty keep-alive lines
          
          if (line.startsWith('data: ')) {
            const dataStr = line.substring(6).trim();
            if (!dataStr) continue;
            
            try {
              const event: SSEEvent = JSON.parse(dataStr);
              onEvent(event);
              
              if (event.event === 'done') {
                console.log('✅ SSE stream manually marked as done');
                // Optional: proactively break loop if server sends 'done' event payload
                // break; (We'll let it finish reading from body just in case metadata is flushed)
              }
            } catch (e) {
              console.error('❌ Failed to parse JSON chunk:', e, 'Raw:', dataStr);
            }
          }
        }
      }
      handleComplete();

    } catch (error: any) {
      if (error?.name === 'AbortError') {
        console.log('🔌 Request cleanly aborted.');
        handleComplete();
      } else {
        console.error('❌ SSE stream error:', error);
        onError?.(error instanceof Error ? error : new Error(String(error)));
      }
    } finally {
      if (abortController) {
         abortController.abort();
         abortController = null;
      }
    }
  };

  return { streamChat };
};
