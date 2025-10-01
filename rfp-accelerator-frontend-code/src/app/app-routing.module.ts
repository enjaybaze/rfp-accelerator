import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { AppComponent } from './app.component';
import { TemplateComponent } from './template/template.component';
import { UploadDocumentComponent } from './upload-document/upload-document.component';
import { RefinementComponent } from './refinement/refinement.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { ReviewComponent } from './review/review.component';
import { ErrorComponent } from './error/error.component';
import { preventBackButtonGuard } from './prevent-back-button.guard';

const routes: Routes = [
  { path: '', component: LoginComponent },
  {
    path:'',
    component: TemplateComponent,
    children:[
      { path: 'uploadDocument', component: UploadDocumentComponent },
      { path: 'refinement', component: RefinementComponent },
      { path: 'review', component: ReviewComponent},
      // { path: 'dashboard', component: DashboardComponent, canDeactivate:[preventBackButtonGuard]},
      { path: 'dashboard', component: DashboardComponent},
      { path: '', redirectTo:'/login', pathMatch:'full'},
      { path: 'error', component: ErrorComponent},
      
    ]
  },
  { path:'', redirectTo:'/template/homepage', pathMatch:'full'},
   { path: '**', redirectTo: '/homepage' }
  // { path: 'homepage', component: HomepageComponent},
  // {path:'', redirectTo:'/login', pathMatch:'full'},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }