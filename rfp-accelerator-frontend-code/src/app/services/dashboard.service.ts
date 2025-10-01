import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BaseurlService } from './baseurl.service';

@Injectable({
  providedIn: 'root'
})
export class DashboardService {

  baseURL: string | null | undefined;
  aiModelBaseUrl: string | null | undefined;
  public no_of_questions: any;
  constructor(private httpClient: HttpClient, private baseurlService:BaseurlService) { 
  }

  getConfigUrl() {
    this.baseURL = localStorage.getItem('baseURL');
    console.log("Base URL =", this.baseURL);
    this.aiModelBaseUrl = localStorage.getItem('aiModelBaseUrl');
    console.log("aiModelBaseUrl =", this.baseURL);
  }

  dashboardTableSearch(params: any) {
    this.getConfigUrl();
    const headers = new HttpHeaders()
      .append(
        'Content-Type',
        'application/json'
      );
    return this.httpClient
      .post<any>(this.baseURL + '/new_dashboard_search', params, {
        headers: headers,

      })
  }

}
