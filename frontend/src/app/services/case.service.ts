import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Case {
    id: number;
    title: string;
    description: string;
    created_at: string;
}

@Injectable({
    providedIn: 'root'
})
export class CaseService {
    private apiUrl = 'http://localhost:8000/cases';

    constructor(private http: HttpClient) { }

    getCases(): Observable<Case[]> {
        return this.http.get<Case[]>(this.apiUrl);
    }

    createCase(title: string, description: string): Observable<Case> {
        return this.http.post<Case>(this.apiUrl, { title, description });
    }
}
