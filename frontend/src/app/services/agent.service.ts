import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Observer } from 'rxjs';
import { AgentEvent } from '../models/agent.models';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AgentService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  sendMessage(message: string, sessionId: string): Observable<AgentEvent> {
    return new Observable((observer: Observer<AgentEvent>) => {
      const controller = new AbortController();

      fetch(`${this.baseUrl}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, session_id: sessionId }),
        signal: controller.signal,
      }).then(async (response) => {
        if (!response.body) {
          observer.error(new Error('No response body'));
          return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const event: AgentEvent = JSON.parse(line.slice(6));
                observer.next(event);
                if (event.type === 'done') {
                  observer.complete();
                  return;
                }
              } catch (e) {
                console.error('Failed to parse SSE event:', line, e);
              }
            }
          }
        }
      }).catch((err) => {
        if (err.name !== 'AbortError') {
          observer.error(err);
        }
      });

      return () => controller.abort();
    });
  }

  getTools(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/tools`);
  }

  getHistory(sessionId: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/sessions/${sessionId}/history`);
  }
}
