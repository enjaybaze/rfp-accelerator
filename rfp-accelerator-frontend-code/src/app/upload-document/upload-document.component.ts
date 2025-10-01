import { Component, OnDestroy } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { ApiServiceService } from '../api-service.service';
import { UploadDocumentService } from '../services/upload-document.service';
import { Data, Router } from '@angular/router';
import { map } from 'rxjs/operators';
import Swal from 'sweetalert2';
import { SharedServiceService } from '../services/shared-service.service';
import { Subscription } from 'rxjs';

export interface TableData {
  qNo: string;
  question: string;
  searchRefinement: string;
}

@Component({
  selector: 'app-upload-document',
  templateUrl: './upload-document.component.html',
  styleUrls: ['./upload-document.component.scss']
})
export class UploadDocumentComponent implements OnDestroy {
  urlError: boolean = false;
  upload: FormGroup = new FormGroup({
    expertRequestID: new FormControl('', [Validators.required]),
    RfpName: new FormControl('', [Validators.required]),
    accountName: new FormControl('', [Validators.required]),
    rfpUrl: new FormControl('', [Validators.required]),
  });
  expertRequestID: string = '';
  RfpName: string = '';
  accountName: string = ''
  rfpUrl: string = '';
  loading = false;
  fieldCheck: boolean = false;
  no_of_questions: any;
  showSpinner = false;
  fileInProgress: boolean | undefined = false;
  subscription: Subscription | undefined;


  constructor(private apiService: ApiServiceService, private router: Router, private fb: FormBuilder, private uploadDocumentService: UploadDocumentService, private sharedService: SharedServiceService) { }

  ngOnInit() {
    this.apiService.initialize();
    this.fieldCheck = this.RfpName !== '' && this.accountName !== '' && this.rfpUrl !== '';
    this.subscription = this.sharedService.status$.subscribe(status => {
      this.fileInProgress = (status === 'In Progress');
    });
    this.fileInProgress = (localStorage.getItem('fileStatus') === 'In Progress');
  }
  get expertRequestIDInput() {
    return this.upload.get('expertRequestID');
  }
  get RfpNameInput() {
    return this.upload.get('RfpName');
  }
  get accountNameInput() {
    return this.upload.get('accountName');
  }
  get rfpUrlInput() {
    return this.upload.get('rfpUrl');
  }

  areFieldsFilled() {
    this.fieldCheck = this.RfpName.length > 0 && this.accountName.length > 0 && this.rfpUrl.length > 0;
    return this.fieldCheck;
  }

  uploadDocuments(): void {
    this.loading = true;
    this.areFieldsFilled();
    if (this.rfpUrl && !this.rfpUrl.startsWith("https://docs.google.com/spreadsheets/d/")) {
      this.urlError = true;
      this.loading = false;
      return;
    }
    else this.urlError = false;
    this.loading = true;
    this.fieldCheck = true;
    let ldap = localStorage.getItem('email');
    console.log(this.RfpName);
    console.log(this.accountName);
    console.log(this.rfpUrl);
    const uploadBodyParameters = {
      "name": this.RfpName,
      "account_name": this.accountName,
      "file_url": this.rfpUrl,
      "user_ldap": localStorage.getItem('userName') as string,
      "token": this.apiService.getToken()
    };
    console.log(uploadBodyParameters);
    this.uploadDocumentService.uploadDocument(uploadBodyParameters).subscribe((res) => {
      console.log(res);
      this.uploadDocumentService.no_of_questions = res.num_questions;
      if (res.Uploaded == true) {
        console.log("Inside IF document uploaded successfully");
        const refinementBodyParameters = {
          "expert_request_id": res.expert_request_id,
          "token": this.apiService.getToken()
        };
        this.apiService.rfpRefinement(refinementBodyParameters).subscribe((refinementResult) => {
          if (refinementResult.Fetched = true) {
            var element_data = refinementResult;
            console.log(element_data + "data of element_data");
            this.apiService.searchRefinementTableDatasource = element_data;
            console.log("searchRefinementData inside refinementResult");
            this.loading = false;
            this.router.navigate(['/refinement'], { skipLocationChange: true });
          }
        });
      }
      else {
        if (res.message) {
          this.loading = false;
          this.showCustomAlert(res);
        }
      }
    },
      // Error callback: Handle errors
      (error) => {
        this.loading = false;
        this.showCustomAlertError("Failed to upload document, try again later.");
      }
    );
  }

  uploadDocument(): void {
    console.log("Dashboard Status = ", this.fileInProgress);
    if (this.fileInProgress) {
      Swal.fire({
        title: '<span style="font-family: \'Google Sans\';">RFP Accelerator</span>',
        html: '<div style="margin-right: -5px;"><span style="font-family: \'Google Sans\'; text-align: left;display: flex;">You cannot upload another document while a file is in progress. Please generate the response for \'InProgress\' ID from the dashboard.</span></div>',
        icon: 'warning', // You can change the icon (success, error, warning, info, question)
        confirmButtonText: '<span style="font-family: \'Google Sans\';">Go to Dashboard</span>',
        confirmButtonColor: '#0B57D0',
        allowOutsideClick: false, // Prevents closing by clicking outside
        allowEscapeKey: false,
        customClass: {
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
        this.router.navigate(['/dashboard'], { skipLocationChange: true });
      });
    }
    else {
      this.uploadDocuments();
    }
  }

  resetData(): void {
    this.fieldCheck = false;
    this.upload.reset();
    this.urlError = false;
    // this.language = "English";
  }

  backToDashboard() {
    this.fieldCheck = false;
    this.urlError = false;
    this.router.navigate(['/dashboard']);
  }

  showCustomAlert(res: any) {
    if (res.Uploaded == "true") {
      Swal.fire({
        title: '<span style="font-family: \'Google Sans\';">Success</span>',
        html: `<span style="font-family: \'Google Sans\';">${res.message}</span>`,
        icon: 'success', // You can change the icon (success, error, warning, info, question)
        confirmButtonText: '<span style="font-family: \'Google Sans\';">OK</span>',
        confirmButtonColor: '#0B57D0',
        allowOutsideClick: false, // Prevents closing by clicking outside
        allowEscapeKey: false,
        customClass: {
          confirmButton: 'google-sans-button'
        },
        didRender: () => {
          const button = document.querySelector('.swal2-confirm') as HTMLElement;
          if (button) {
            button.style.borderRadius = '100px';
            button.style.fontFamily = 'Google Sans';
          }
        }
      });
    }
    else {
      Swal.fire({
        title: '<span style="font-family: \'Google Sans\';">Failed</span>',
        html: `<span style="font-family: \'Google Sans\';">${res.message}</span>`,
        icon: 'warning', // You can change the icon (success, error, warning, info, question)
        confirmButtonText: '<span style="font-family: \'Google Sans\';">OK</span>',
        confirmButtonColor: '#0B57D0',
        allowOutsideClick: false, // Prevents closing by clicking outside
        allowEscapeKey: false,
        customClass: {
          popup: 'custom-popup-class',
          confirmButton: 'google-sans-button'
        },
        didRender: () => {
          const button = document.querySelector('.swal2-confirm') as HTMLElement;
          if (button) {
            button.style.borderRadius = '100px';
            button.style.fontFamily = 'Google Sans';
          }
        }
      });
    }
  }

  showCustomAlertError(message: any) {
    Swal.fire({
      title: '<span style="font-family: \'Google Sans\';">RFP Accelarator</span>',
      html: '<span style="font-family: \'Google Sans\';">Failed to upload document, try again later.</span>',
      icon: 'warning', // You can change the icon (success, error, warning, info, question)
      confirmButtonText: '<span style="font-family: \'Google Sans\';">OK</span>',
      confirmButtonColor: '#0B57D0',
      allowOutsideClick: false, // Prevents closing by clicking outside
      allowEscapeKey: false,
      customClass: {
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
      this.loading = false;
    });
  }

  showCustomAlertForUnauthenticatedUser(message: any, redirectToLogin: boolean = false) {
    Swal.fire({
      title: '<span style="font-family: \'Google Sans\';">RFP Accelarator</span>',
      html: `<span style="font-family: \'Google Sans\';">${message}</span>`,
      icon: 'warning', // You can change the icon (success, error, warning, info, question)
      confirmButtonText: '<span style="font-family: \'Google Sans\';">OK</span>',
      confirmButtonColor: '#0B57D0',
      allowOutsideClick: false, // Prevents closing by clicking outside
      allowEscapeKey: false,
      customClass: {
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
      if (result.isConfirmed && redirectToLogin) {
        this.router.navigate(['/'], { skipLocationChange: true });
      }
    });
  }

  uploadFileDone():void{
    this.sharedService.clearStatus();
  }

  ngOnDestroy(): void {
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }
}