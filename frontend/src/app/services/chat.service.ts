import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Message {
    id: number;
    sender: 'user' | 'ai';
    content: string;
    timestamp: string;
    case_id: number;
}

@Injectable({
    providedIn: 'root'
})
export class ChatService {
    private apiUrl = 'http://localhost:8000/chat';

    constructor(private http: HttpClient) { }

    getHistory(caseId: number): Observable<Message[]> {
        return this.http.get<Message[]>(`${this.apiUrl}/${caseId}`);
    }

    sendMessage(caseId: number, content: string): Observable<Message> {
        return this.http.post<Message>(this.apiUrl, { case_id: caseId, sender: 'user', content });
    }
}
