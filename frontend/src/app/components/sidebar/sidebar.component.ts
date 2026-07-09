import { Component, EventEmitter, Input, Output } from '@angular/core';
import { NgFor, NgIf, DatePipe } from '@angular/common';
import { SessionSummary } from '../../models/session.models';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [NgFor, NgIf, DatePipe],
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.scss'],
})
export class SidebarComponent {
  @Input() sessions: SessionSummary[] = [];
  @Input() activeSessionId: string | null = null;
  @Output() selectSession = new EventEmitter<string>();
  @Output() newSession = new EventEmitter<void>();
  @Output() deleteSession = new EventEmitter<string>();
  @Output() pinSession = new EventEmitter<string>();

  confirmingId: string | null = null;

  onSelect(id: string): void {
    if (this.confirmingId) return;
    this.selectSession.emit(id);
  }

  onNew(): void {
    this.confirmingId = null;
    this.newSession.emit();
  }

  onPin(event: Event, id: string): void {
    event.stopPropagation();
    this.confirmingId = null;
    this.pinSession.emit(id);
  }

  onDelete(event: Event, id: string): void {
    event.stopPropagation();
    this.confirmingId = id;
  }

  confirmDelete(id: string): void {
    this.confirmingId = null;
    this.deleteSession.emit(id);
  }

  cancelDelete(): void {
    this.confirmingId = null;
  }
}
