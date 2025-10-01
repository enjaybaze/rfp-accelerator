import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class BaseurlService {
  private baseURL: string | undefined;
  private aiModelBaseUrl: string | undefined;
  private configLoaded: boolean = false;

  constructor(private http: HttpClient) {
    this.loadConfig(); // Start loading config upon service instantiation
  }

  getConfig(): Observable<string> {
     return this.http.get('assets/config.txt', { responseType: 'text' });
  }

  loadConfig() {
    this.getConfig().subscribe(
      config => {
        console.log("Load Config");
        const lines = config.split('\n');
        const baseURLLine = lines.find(line => line.includes('baseURL'));
        const aiModelBaseUrlLine = lines.find(line => line.includes('aiModelBaseUrl'));
        if (baseURLLine && aiModelBaseUrlLine) {
          this.baseURL = baseURLLine.split('=')[1].trim();
          this.aiModelBaseUrl = aiModelBaseUrlLine.split('=')[1].trim();
          this.configLoaded = true;
          console.log(this.baseURL);
          
          localStorage.setItem('baseURL', this.baseURL);
          localStorage.setItem('aiModelBaseUrl', this.aiModelBaseUrl);

        } else {
          console.error('Invalid config file format.');
        }
      },
      error => {
        console.error('Error loading config file:', error);
      }
    );
  }

  // getBaseUrl(): string {
  //   if (!this.baseURL) {
  //     const storedAiModelBaseUrl = localStorage.getItem('baseURL');
  //     this.baseURL = storedAiModelBaseUrl !== null ? storedAiModelBaseUrl : undefined;
  //   }
  //   return this.baseURL!;
  // }

  // getAiModelBaseUrl(): string {
  //   if (!this.aiModelBaseUrl) {
  //     const storedAiModelBaseUrl = localStorage.getItem('aiModelBaseUrl');
  //     this.aiModelBaseUrl = storedAiModelBaseUrl !== null ? storedAiModelBaseUrl : undefined;
  //   }
  //   return this.aiModelBaseUrl!;
  // }
}