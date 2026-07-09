import { Component, OnInit } from '@angular/core';
import { ChatComponent } from './components/chat/chat.component';
import { SidebarComponent } from './components/sidebar/sidebar.component';
import { SessionService } from './services/session.service';
import { SessionSummary } from './models/session.models';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [ChatComponent, SidebarComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit {
  sessions: SessionSummary[] = [];
  activeSessionId: string | null = null;
  sidebarVisible = true;

  constructor(private sessionService: SessionService) {}

  ngOnInit(): void {
    this.loadSessions();
  }

  loadSessions(): void {
    this.sessionService.listSessions().subscribe({
      next: (list) => {
        this.sessions = list;
      },
      error: () => {
        this.sessions = [];
      },
    });
  }

  onSelectSession(id: string): void {
    this.activeSessionId = id;
  }

  onNewSession(): void {
    this.activeSessionId = null;
  }

  onDeleteSession(id: string): void {
    this.sessionService.deleteSession(id).subscribe({
      next: () => {
        this.sessions = this.sessions.filter(s => s.id !== id);
        if (this.activeSessionId === id) {
          this.activeSessionId = null;
        }
      },
    });
  }

  onSessionCreated(id: string): void {
    this.activeSessionId = id;
    this.loadSessions();
  }

  toggleSidebar(): void {
    this.sidebarVisible = !this.sidebarVisible;
  }
}
