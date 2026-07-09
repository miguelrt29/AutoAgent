import { Component, ElementRef, ViewChild } from '@angular/core';
import { NgFor, NgIf, NgClass, JsonPipe, DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { AgentService } from '../../services/agent.service';
import { ChatSession, ChatMessage } from '../../models/agent.models';
import { MarkdownPipe } from '../../pipes/markdown.pipe';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [NgFor, NgIf, NgClass, JsonPipe, DatePipe, FormsModule, MarkdownPipe],
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss'],
})
export class ChatComponent {
  @ViewChild('chatContainer') chatContainer!: ElementRef;
  @ViewChild('inputEl') inputEl!: ElementRef;

  sessionId = crypto.randomUUID();
  userInput = '';

  chatSession: ChatSession = {
    sessionId: this.sessionId,
    messages: [],
    toolCalls: [],
    isStreaming: false,
  };

  constructor(private agentService: AgentService) {}

  badgeClass(tool: string): string {
    const map: Record<string, string> = {
      web_search: 'web_search',
      read_file: 'read_file',
      write_file: 'write_file',
      send_email: 'send_email',
      call_api: 'call_api',
      run_command: 'run_command',
    };
    return map[tool] || '';
  }

  onInput(event: Event): void {
    const el = event.target as HTMLTextAreaElement;
    el.style.height = '44px';
    el.style.height = Math.min(el.scrollHeight, 120) + 'px';
  }

  onKeyDown(event: Event): void {
    const ke = event as KeyboardEvent;
    if (ke.shiftKey) return;
    ke.preventDefault();
    this.sendMessage();
  }

  sendMessage(): void {
    const text = this.userInput.trim();
    if (!text || this.chatSession.isStreaming) return;

    const userMsg: ChatMessage = { role: 'user', content: text, timestamp: new Date() };
    this.chatSession.messages.push(userMsg);
    this.userInput = '';
    this.resetTextareaHeight();

    this.chatSession.isStreaming = true;

    const assistantMsg: ChatMessage = { role: 'assistant', content: '', timestamp: new Date() };
    this.chatSession.messages.push(assistantMsg);

    this.agentService.sendMessage(text, this.sessionId).subscribe({
      next: (event) => {
        switch (event.type) {
          case 'tool_call':
            this.chatSession.toolCalls.push({
              tool: event.tool!,
              input: event.input!,
              timestamp: new Date(),
            });
            break;

          case 'text': {
            const last = this.chatSession.messages[this.chatSession.messages.length - 1];
            if (last && last.role === 'assistant') {
              last.content += event.content;
            } else {
              this.chatSession.messages.push({
                role: 'assistant',
                content: event.content || '',
                timestamp: new Date(),
              });
            }
            break;
          }

          case 'error': {
            const last = this.chatSession.messages[this.chatSession.messages.length - 1];
            if (last && last.role === 'assistant') {
              last.content = `⚠ Error: ${event.message}`;
            } else {
              this.chatSession.messages.push({
                role: 'assistant',
                content: `⚠ Error: ${event.message}`,
                timestamp: new Date(),
              });
            }
            break;
          }
        }
        this.scrollToBottom();
      },
      error: (err) => {
        console.error('Stream error:', err);
        const msg = err.message || err.toString();
        const last = this.chatSession.messages[this.chatSession.messages.length - 1];
        if (last && last.role === 'assistant') {
          last.content = `Error de conexión: ${msg}`;
        } else {
          this.chatSession.messages.push({
            role: 'assistant',
            content: `Error de conexión: ${msg}`,
            timestamp: new Date(),
          });
        }
        this.chatSession.isStreaming = false;
        this.scrollToBottom();
      },
      complete: () => {
        this.chatSession.isStreaming = false;
        const last = this.chatSession.messages[this.chatSession.messages.length - 1];
        if (last && last.role === 'assistant' && !last.content) {
          this.chatSession.messages.pop();
        }
        this.scrollToBottom();
      },
    });
  }

  private resetTextareaHeight(): void {
    setTimeout(() => {
      if (this.inputEl) {
        this.inputEl.nativeElement.style.height = '44px';
      }
    });
  }

  private scrollToBottom(): void {
    requestAnimationFrame(() => {
      if (this.chatContainer) {
        this.chatContainer.nativeElement.scrollTop =
          this.chatContainer.nativeElement.scrollHeight;
      }
    });
  }
}
