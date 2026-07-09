import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { SessionSummary, SessionDetail } from '../models/session.models';

@Injectable({ providedIn: 'root' })
export class SessionService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  listSessions(): Observable<SessionSummary[]> {
    return this.http.get<SessionSummary[]>(`${this.baseUrl}/sessions`);
  }

  getSession(sessionId: string): Observable<SessionDetail> {
    return this.http.get<SessionDetail>(`${this.baseUrl}/sessions/${sessionId}`);
  }

  updateTitle(sessionId: string, title: string): Observable<SessionSummary> {
    return this.http.put<SessionSummary>(`${this.baseUrl}/sessions/${sessionId}/title`, { title });
  }

  deleteSession(sessionId: string): Observable<{ ok: boolean }> {
    return this.http.delete<{ ok: boolean }>(`${this.baseUrl}/sessions/${sessionId}`);
  }
}
