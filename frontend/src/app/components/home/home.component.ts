import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { SidebarComponent } from '../sidebar/sidebar.component';
import { DocumentViewerComponent } from '../document-viewer/document-viewer.component';
import { LegalChatComponent } from '../legal-chat/legal-chat.component';
import { DocumentService } from '../../services/document.service';
import { CaseService, Case } from '../../services/case.service';

import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, SidebarComponent, DocumentViewerComponent, LegalChatComponent, FormsModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent implements OnInit {
  currentView: string = 'chat'; // Default to chat as requested

  uploadStatus: 'idle' | 'uploading' | 'success' | 'error' = 'idle';
  selectedFile: File | null = null;
  selectedCaseId: number | null = null;
  cases: Case[] = [];
  errorMessage: string = '';

  topicList: string[] = [
    'Abuso Sexual', 'Homicidio', 'Femicidio', 'Violencia de Género',
    'Narcotráfico', 'Trata de Personas', 'Estafas', 'Robo a Mano Armada',
    'Secuestro', 'Extorsión', 'Ciberdelitos', 'Grooming',
    'Derecho de Familia', 'Divorcios', 'Custodia', 'Adopción',
    'Violencia Doméstica', 'Maltrato Infantil', 'Derecho Laboral', 'Despidos',
    'Accidentes de Tránsito', 'Mala Praxis', 'Propiedad Intelectual', 'Contratos',
    'Desalojos', 'Usurpación', 'Derecho Penal Juvenil', 'Delitos Fiscales',
    'Lavado de Activos', 'Corrupción', 'Derechos Humanos', 'Discriminación',
    'Aborto Legal', 'Eutanasia', 'Portación de Armas', 'Delitos Ambientales',
    'Protección Animal', 'Derecho Sucesorio', 'Herencias', 'Quiebras'
  ];

  constructor(
    private documentService: DocumentService,
    private caseService: CaseService,
    private route: ActivatedRoute
  ) { }

  ngOnInit() {
    this.route.data.subscribe(data => {
      if (data['view']) {
        this.currentView = data['view'];
        this.resetUploadState();
      }
    });

    // Load cases for the dropdown
    this.caseService.getCases().subscribe(cases => {
      this.cases = cases;
    });
  }

  // Helper to reset state when view changes
  private resetUploadState() {
    if (this.currentView !== 'upload') {
      this.uploadStatus = 'idle';
      this.selectedFile = null;
    }
  }

  // Deprecated but kept for compatibility if needed (unused now)
  onMenuSelect(viewId: string) {
    this.currentView = viewId;
    this.resetUploadState();
  }

  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file) {
      this.selectedFile = file;
      this.uploadStatus = 'idle';
    }
  }

  onUpload() {
    if (!this.selectedFile) return;

    this.uploadStatus = 'uploading';
    this.documentService.uploadFile(this.selectedFile, this.selectedCaseId || undefined).subscribe({
      next: (response) => {
        console.log('Upload success', response);
        this.uploadStatus = 'success';
        this.selectedFile = null; // Clear file after success
      },
      error: (error) => {
        console.error('Upload error', error);
        this.uploadStatus = 'error';
        this.errorMessage = 'Error al conectar con el servidor. Asegúrate que el backend esté corriendo.';
      }
    });
  }
}
