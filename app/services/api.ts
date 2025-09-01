const API_BASE_URL = 'http://localhost:8000';

export interface ChatMessage {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  response: string;
  conversation_id: string;
  sources: Array<{
    content: string;
    metadata: any;
    similarity: number;
  }>;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ConversationDetail {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages: Array<{
    timestamp: string;
    user_message: string;
    bot_response: string;
    sources: any[];
  }>;
}

export interface SystemStats {
  total_chunks: number;
  unique_files: number;
  file_types: Record<string, number>;
  embedding_model: string;
  vector_db_path: string;
}

class ApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  async sendMessage(message: ChatMessage): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(message),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getConversations(): Promise<Conversation[]> {
    const response = await fetch(`${this.baseUrl}/conversations`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getConversation(conversationId: string): Promise<ConversationDetail> {
    const response = await fetch(`${this.baseUrl}/conversations/${conversationId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async deleteConversation(conversationId: string): Promise<void> {
    const response = await fetch(`${this.baseUrl}/conversations/${conversationId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  }

  async triggerIngestion(path?: string, incremental: boolean = true): Promise<void> {
    const response = await fetch(`${this.baseUrl}/ingest`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        path,
        incremental,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
  }

  async getIngestionStatus(): Promise<{status: string; progress: number; message: string}> {
    const response = await fetch(`${this.baseUrl}/ingest/status`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getStats(): Promise<SystemStats> {
    const response = await fetch(`${this.baseUrl}/stats`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async checkHealth(): Promise<{status: string; service: string}> {
    const response = await fetch(`${this.baseUrl}/health`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}

export const apiService = new ApiService();