import { Component, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { CaseService, Case } from '../../services/case.service';

interface MenuItem {
  id: string; // Added ID for easier handling
  icon: string;
  label: string;
  route: string; // Added route property
  active?: boolean;
  expanded?: boolean;
  children?: { label: string; active?: boolean }[];
}

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.scss'
})
export class SidebarComponent implements OnInit {
  @Output() menuSelect = new EventEmitter<string>();
  cases: Case[] = [];

  constructor(private router: Router, private caseService: CaseService) { }

  ngOnInit() {
    this.caseService.getCases().subscribe(cases => {
      this.cases = cases;
    });
  }

  menuItems: MenuItem[] = [
    { id: 'upload', icon: '', label: 'Subir archivos', route: '/upload', active: false },
    { id: 'search', icon: '', label: 'Búsqueda Semántica', route: '/search', active: false },
    { id: 'bulk', icon: '', label: 'Biblioteca de Casos', route: '/temario', active: false },
  ];

  toggleExpand(item: MenuItem) {
    if (item.children) {
      item.expanded = !item.expanded;
    } else {
      // Deactivate all others
      this.menuItems.forEach(i => i.active = false);
      item.active = true;
      this.router.navigate([item.route]);
    }
  }

  selectChat(caseId?: number) {
    this.menuItems.forEach(i => i.active = false);
    if (caseId) {
      this.router.navigate(['/chat', caseId]);
    } else {
      this.router.navigate(['/chat']);
    }
  }
}
