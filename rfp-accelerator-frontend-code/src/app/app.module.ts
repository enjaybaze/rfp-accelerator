import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { provideHttpClient } from '@angular/common/http';
import { provideOAuthClient } from 'angular-oauth2-oidc';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { OAuthModule, OAuthService, OAuthStorage } from 'angular-oauth2-oidc';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { LoginComponent } from './login/login.component';
import { TemplateComponent } from './template/template.component';
import { UploadDocumentComponent } from './upload-document/upload-document.component';
import { RefinementComponent } from './refinement/refinement.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { ReviewComponent } from './review/review.component';
import { AngmaterialModule } from './angmaterial/angmaterial.module';
import { HttpClient } from '@angular/common/http';
import { ErrorComponent } from './error/error.component';
import { HashLocationStrategy, LocationStrategy, PathLocationStrategy } from '@angular/common';
import { NgIdleModule } from '@ng-idle/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import {MatNativeDateModule, MatRippleModule} from '@angular/material/core';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { RfpFeedbackPopupComponent } from './rfp-feedback-popup/rfp-feedback-popup.component';
import { MatDialogModule } from '@angular/material/dialog';
import { FormsModule } from '@angular/forms';

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    TemplateComponent,
    UploadDocumentComponent,
    RefinementComponent,
    DashboardComponent,
    ReviewComponent,
    ErrorComponent,
    RfpFeedbackPopupComponent,
  ],
  imports: [
    MatNativeDateModule,
    MatRippleModule,
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    AngmaterialModule,
    MatDatepickerModule,
    MatSidenavModule,
    MatListModule,
    MatIconModule,
    MatMenuModule,
    MatDialogModule,
    FormsModule,
    NgIdleModule.forRoot(),
    OAuthModule.forRoot(),
  ],
  // providers: [ HttpClient, {provide : LocationStrategy}],
  providers: [HttpClient,{provide : LocationStrategy, useClass: HashLocationStrategy}, provideHttpClient(),
  provideOAuthClient()],
  bootstrap: [AppComponent]
})
export class AppModule { }
