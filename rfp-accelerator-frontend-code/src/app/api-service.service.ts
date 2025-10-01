import { Injectable, OnInit } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BehaviorSubject, Observable, map, tap } from 'rxjs';
// import { environment } from 'src/environments/environment';
import { Router,ActivatedRoute } from '@angular/router';
import { Idle, DEFAULT_INTERRUPTSOURCES } from '@ng-idle/core';
import Swal from 'sweetalert2';
import { BaseurlService } from './services/baseurl.service';

// import { LoginComponent } from './login/login.component';
export interface searchRefinementTableData {
  qNo: number;
  question: string;
  searchRefinement: string;
}

@Injectable({
  providedIn: 'root'
})
export class ApiServiceService implements OnInit {
  public searchRefinementTableDatasource: any;
  public dashboardElement: any;
  public token: any;
  public tokenKey = 'auth_token';
  public finalReviewElement: any;
  public smeDashboardElement: any;
  public dashboardSearchData: any;
  public smeSearchData: any;
  public reviewResponseData: any;
  public expertRequestId: any;
  public accountName: any;
  public inputURL: any;
  public uploadRes: any;
  public adminViewSearchData: any;
  public exp_req_id: any;
  public no_of_questions: any;
  public feedbackElement: any;
  public feedbackFormExpId: any;
  public feedbackExpIdValue: any;
  public reviewToFeedbackExpID : any;
  public selectedSmeId: string | undefined;
  userNameSource = new BehaviorSubject<string | undefined>(localStorage?.getItem('userName') || undefined);
  userName$ = this.userNameSource.asObservable();
  userEmailSource = new BehaviorSubject<string | undefined>(localStorage?.getItem('userEmail') || undefined);
  userEmail$ = this.userEmailSource.asObservable();
  userPhotoSource = new BehaviorSubject<string | undefined>(localStorage?.getItem('userPhoto') || undefined);
  userPhoto$ = this.userPhotoSource.asObservable();
  private endpoint = "users";
  private domain: string | undefined;
  idleState = 'Not started.';
  tokenRefresh = false;
  timedOut = false;
  swalAlert: any; // Variable to store reference to Swal alert
  baseURL: string | undefined | null;
  aiModelBaseUrl: string | undefined | null;
  constructor(private httpClient: HttpClient, private route: ActivatedRoute, private baseurlService: BaseurlService, private router: Router, private idle: Idle) {
    // this.domain = environment.domain;
    const currentUrl = window.location.href;
    console.log("currentUrl",currentUrl);

    if(localStorage.getItem("isUserLoggedIN")){
      let res=localStorage.getItem("isUserLoggedIN");
      if(res=="true"){
        console.log("-----------------------------");
        
        console.log("user logged in");
        
        this.initialize();
      }
    }
  }

  //initialize() {}
  initialize() {
    console.log("initialize");
    console.log(this.idle);

    this.idle.stop();
    
    
    this.idle.setIdle(10500); // 2hr 55 minutes of inactivity (300 seconds)
    this.idle.setTimeout(9600); // 2hr 40min  before timeout (180 seconds)
    this.idle.setInterrupts(DEFAULT_INTERRUPTSOURCES);
    this.swalAlert = Swal;
    let timeoutWarningTimer: any;
    let timeoutWarningShown = false;

    // Subscribe to idle events
    this.idle.onIdleEnd.subscribe(() => {
      this.idleState = 'No longer idle.'
      console.log(this.idleState);
      this.reset();
    });
    this.idle.onIdleStart.subscribe(() => {
      console.log('idle.');
      timeoutWarningShown = false;
      this.tokenRefresh = false;
    });

    this.idle.onTimeoutWarning.subscribe((countdown: number) => {
      console.log("countdown:", countdown);
      
      if (!timeoutWarningShown) {
        const remainingTime = Math.ceil(countdown / 60); // Convert seconds to minutes
        this.showCustomAlert(`You're inactive. Session will expire soon. Click OK to continue or it will expire shortly`);
        timeoutWarningShown = true;
      }
    });

    this.idle.onTimeout.subscribe((countdown: number) => {
      if (timeoutWarningShown && !this.tokenRefresh) {
        this.showCustomAlertSessionTimeout(`Session is expired due to inactivity. Please log in again`);
        timeoutWarningShown = false;
      }
    });
  }

  reset() {
    this.idle.watch();
    this.timedOut = false;
  }

  ngOnInit() { }

  getConfigUrl() {
    this.baseURL = localStorage.getItem('baseURL');
    console.log("Base URL =", this.baseURL);
    this.aiModelBaseUrl = localStorage.getItem('aiModelBaseUrl');
    console.log("aiModelBaseUrl =", this.aiModelBaseUrl);
  }

  setUserData(name: string, photo: string, email: string) {
    this.userNameSource.next(name);
    this.userPhotoSource.next(photo);
    this.userEmailSource.next(email);

    localStorage.setItem('userName', name);
    localStorage.setItem('userPhoto', photo);
    localStorage.setItem('userEmail', email);
  }

  saveToken(token: string): void {
    localStorage.setItem(this.tokenKey, token);
    console.log('Token saved: ', token);
  }

  //Functon to retrive the token form localStorage
  getToken(): string | null {
    const token = localStorage.getItem(this.tokenKey);
    console.log('Token retrived:', token);
    return token;
  }

  generalSignInAPI(params: any): Observable<any> {
    this.getConfigUrl();
    const headers = new HttpHeaders()
      .append(
        'Content-Type',
        'application/json'
      );
    this.startIdleDetection();
    console.log("baseURL:"+this.baseURL);

    console.log(("-------"));
    

    console.log(this.httpClient
      .post<any>(this.baseURL + '/welcome', params, {
        headers: headers
      }));

    

    return this.httpClient
      .post<any>(this.baseURL + '/welcome', params, {
        headers: headers
      }).pipe(map(response => response))
  }

  private startIdleDetection() {
    this.idle.watch();
  }

  saveReviewData(params: any) {
    const headers = new HttpHeaders()
      .append(
        'Content-Type',
        'application/json'
      );
    return this.httpClient
      .post<any>(this.baseURL + '/new_save_review_demo', params, {
        headers: headers,
      })
  }

  

  rfpRefinement(params: any) {
    this.getConfigUrl();
    const headers = new HttpHeaders()
      .append(
        'Content-Type',
        'application/json'
      );
    return this.httpClient
      .post<any>(this.baseURL + '/rfp_refinement3', params, {
        headers: headers,

      })
  }



  refinementRunModel(params: any) {
    this.getConfigUrl();
    const headers = new HttpHeaders()
      .append(
        'Content-Type',
        'application/json'
      );
    return this.httpClient
      .post<any>(this.baseURL + '/run_model', params, {
        headers: headers,

      })
  }


  refinementRunModelTrigger(params: any) {
    this.getConfigUrl();
    const headers = new HttpHeaders()
      .append(
        'Content-Type',
        'application/json'
      );
    return this.httpClient
      .post<any>(this.aiModelBaseUrl + '/deps-query', params, {
        headers: headers,

      })
  }

  reviewTableLoad(params: any) {
    this.getConfigUrl();
    const headers = new HttpHeaders()
      .append(
        'Content-Type',
        'application/json'
      );
    return this.httpClient
      .post<any>(this.baseURL + '/new_load_review_demo', params, {
        headers: headers,
      })
  }


  deleteData(params: any) {
    this.getConfigUrl();
    const headers = new HttpHeaders()
      .append(
        'Content-Type',
        'application/json'
      );
    return this.httpClient
      .post<any>(this.baseURL + '/soft_remove', params, {
        headers: headers,

      })

  }

 

  downloadRfpResponses(params: any) {
    this.getConfigUrl();
    const headers = new HttpHeaders()
      .append(
        'Content-Type',
        'application/json'
      );
    return this.httpClient
      .post<any>(this.baseURL + '/download_file', params, {
        headers: headers,
      })
  }
  showCustomAlertSessionTimeout(message: any) {
    Swal.fire({
      title: '<span style="font-family: \'Google Sans\';">RFP Accelarator</span>',
      html: '<span style="font-family: \'Google Sans\';">Session is expired due to inactivity. Please log in again</span>',
      icon: 'warning', // You can change the icon (success, error, warning, info, question)
      confirmButtonText: '<span style="font-family: \'Google Sans\';">OK</span>',
      confirmButtonColor: '#0B57D0',
      allowOutsideClick: false,
      allowEscapeKey: false,
      customClass:{
        confirmButton: 'google-sans-button'
      },
      didRender: () => {
        const button = document.querySelector('.swal2-confirm') as HTMLElement;
        if (button) {
          button.style.borderRadius = '100px';
          button.style.fontFamily = 'Google Sans';
        }
      }
    }).then((result) => {
      if (result.isConfirmed) {
        this.closePopup();
        this.router.navigate(['']);
        localStorage.clear();
      }
    })
  }

  showCustomAlert(message: any) {
    Swal.fire({
      title: '<span style="font-family: \'Google Sans\';">RFP Accelarator</span>',
      html: '<span style="font-family: \'Google Sans\';">You\'re inactive. Session will expire soon. Click OK to continue or it will expire shortly</span>',
      icon: 'warning', // You can change the icon (success, error, warning, info, question)
      allowOutsideClick: false,
      confirmButtonText: '<span style="font-family: \'Google Sans\';">OK</span>',
      confirmButtonColor: '#0B57D0',
      allowEscapeKey: false,
      customClass:{
        confirmButton: 'google-sans-button'
      },
      didRender: () => {
        const button = document.querySelector('.swal2-confirm') as HTMLElement;
        if (button) {
          button.style.borderRadius = '100px';
          button.style.fontFamily = 'Google Sans';
        }
      }
    }).then((result) => {
      if (result.isConfirmed) {
        // this.tokenRefreshOnIdelWarning();
      }
    })
  }



  closePopup() {
    if (this.swalAlert) {
      this.swalAlert.close(); // Close the Swal alert if it exists
    }
  }


}