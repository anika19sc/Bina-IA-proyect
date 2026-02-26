import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
    selector: 'app-document-viewer',
    standalone: true,
    imports: [CommonModule],
    templateUrl: './document-viewer.component.html',
    styleUrl: './document-viewer.component.scss'
})
export class DocumentViewerComponent {
    encryptionStatus = 'Cifrado AES-256';
    isLocked = true;
}
