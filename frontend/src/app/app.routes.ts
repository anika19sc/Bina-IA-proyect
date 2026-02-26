import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { HomeComponent } from './components/home/home.component';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
    { path: 'login', component: LoginComponent },
    { path: 'chat', component: HomeComponent, data: { view: 'chat' } },
    { path: 'chat/:id', component: HomeComponent, data: { view: 'chat' } },
    { path: 'upload', component: HomeComponent, data: { view: 'upload' } },
    { path: 'search', component: HomeComponent, data: { view: 'search' } },
    { path: 'temario', component: HomeComponent, data: { view: 'bulk' } },
    { path: '', redirectTo: 'chat', pathMatch: 'full' },
    { path: '**', redirectTo: 'chat' }
];
