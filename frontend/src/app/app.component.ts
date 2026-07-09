import { Component, OnInit } from '@angular/core';
import { NgIf } from '@angular/common';
import { ChatComponent } from './components/chat/chat.component';
import { SidebarComponent } from './components/sidebar/sidebar.component';
import { SessionService } from './services/session.service';
import { SessionSummary } from './models/session.models';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [NgIf, ChatComponent, SidebarComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit {
  sessions: SessionSummary[] = [];
  activeSessionId: string | null = null;
  sidebarVisible = true;
  confirmingId: string | null = null;

  constructor(private sessionService: SessionService) {}

  ngOnInit(): void {
    this.sidebarVisible = window.innerWidth > 768;
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

  onDeleteRequest(id: string): void {
    this.confirmingId = id;
  }

  confirmDelete(): void {
    const id = this.confirmingId;
    this.confirmingId = null;
    if (!id) return;
    this.sessionService.deleteSession(id).subscribe({
      next: () => {
        this.sessions = this.sessions.filter(s => s.id !== id);
        if (this.activeSessionId === id) {
          this.activeSessionId = null;
        }
      },
    });
  }

  cancelDelete(): void {
    this.confirmingId = null;
  }

  onPinSession(id: string): void {
    this.sessionService.pinSession(id).subscribe({
      next: () => this.loadSessions(),
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
