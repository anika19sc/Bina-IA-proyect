import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
    providedIn: 'root'
})
export class DocumentService {
    // Replace with your actual backend API URL
    private apiUrl = 'http://localhost:8000/upload';

    constructor(private http: HttpClient) { }

    uploadFile(file: File, caseId?: number): Observable<any> {
        const formData = new FormData();
        formData.append('file', file);
        if (caseId) {
            formData.append('case_id', caseId.toString());
        }

        return this.http.post(this.apiUrl, formData);
    }
}
