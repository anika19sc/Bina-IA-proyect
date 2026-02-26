import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { ChatService, Message } from '../../services/chat.service';

@Component({
    selector: 'app-legal-chat',
    standalone: true,
    imports: [CommonModule, FormsModule],
    templateUrl: './legal-chat.component.html',
    styleUrl: './legal-chat.component.scss'
})
export class LegalChatComponent implements OnInit {
    messages: any[] = [];
    newMessage = '';
    caseId: number | null = null;
    isLoading = false;

    constructor(
        private chatService: ChatService,
        private route: ActivatedRoute
    ) { }

    ngOnInit() {
        this.route.paramMap.subscribe(params => {
            const id = params.get('id'); // Assuming route is chat/:id
            if (id) {
                this.caseId = +id;
                this.loadChatHistory();
            } else {
                // Default or empty state
                this.messages = [];
            }
        });
    }

    loadChatHistory() {
        if (!this.caseId) return;
        this.isLoading = true;
        this.chatService.getHistory(this.caseId).subscribe({
            next: (msgs) => {
                this.messages = msgs;
                this.isLoading = false;
            },
            error: () => this.isLoading = false
        });
    }

    sendMessage() {
        if (this.newMessage.trim() && this.caseId) {
            const content = this.newMessage;
            this.newMessage = ''; // Clear input immediately

            // Optimistic update
            this.messages.push({ sender: 'user', content: content, timestamp: new Date().toISOString() });

            this.isLoading = true;
            this.chatService.sendMessage(this.caseId!, content).subscribe({
                next: (response) => {
                    this.messages.push(response); // Add AI response
                    this.isLoading = false;
                },
                error: (err) => {
                    console.error('Error sending message', err);
                    this.isLoading = false;
                }
            });
        } else if (!this.caseId) {
            alert("Por favor selecciona un caso del menú lateral para comenzar el chat.");
        }
    }
}
