import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { MatPaginator, MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatSort } from '@angular/material/sort';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { ApiServiceService } from '../api-service.service';
import { Router } from '@angular/router';
import Swal from 'sweetalert2';
import { empty, flatMap } from 'rxjs';
import { DashboardService } from '../services/dashboard.service';
import { SharedServiceService } from '../services/shared-service.service';
import { LocationStrategy, PlatformLocation } from '@angular/common';

export interface TableData {
  rfpID: string;
  rfpName: string;
  accountName: string;
  status: string;
  submissionDate: string;
  download: string;
}

interface DataObject {
  [key: string]: any;
}

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  @ViewChild(MatPaginator) paginator: MatPaginator | undefined;
  @ViewChild(MatSort) sort: MatSort | undefined;
  @ViewChild('input') input: ElementRef | undefined;
  screen_title: string = 'Dashboard';
  dashboard_upload: FormGroup<any> = this.fb.group({
    expertRequestID: ['', Validators.required],
    accountName: ['', Validators.required],
    region: ['', Validators.required],
    fromDate: ["2024-01-01", Validators.required],
    toDate: [this.getCurrentDate(), Validators.required],
    language: ['', Validators.required],
  });
  expertRequestID: any;
  accountName: any;
  region: any;
  fromDate: any;
  toDate: any;
  language: string = "English";
  searchDataArray: any;
  searchData: any;
  pageSizeOptions = [10, 25, 40, 100];
  pageSize = this.pageSizeOptions[0];
  showFirstLastButtons = true;
  disabled = false;
  displayedColumns: string[] = ['rfpID', 'rfpName', 'accountName', 'status', 'submissionDate', 'download'];
  dataSource: any;
  resDataArray: any;
  cardDataArray: any;
  totalGeneratedRFPs: any;
  totalUploadedRFPs: any;
  avgResponseTime: any;
  totalGeneratedRFPsnd: any = '0';
  totalUploadedRFPsnd: any = '0';
  avgResponseTimend: any = '- S';
  waiting: any;
  dateError: boolean = false;
  refreshIcon: boolean = false;
  intervalId: any | null = null;
  loading: boolean = false;
  userName: string | undefined;
  pageEvent: PageEvent | undefined;
  isAscending = true;
  dataArray: any;
  isInProgress = false;
  showUserName:string|undefined;

  constructor(private apiService: ApiServiceService, private router: Router, private fb: FormBuilder, private dashboardService: DashboardService, private sharedService: SharedServiceService, private platformLocation: LocationStrategy) { 
    // history.pushState(null,'',window.location.href);
    // this.platformLocation.onPopState(()=>{
    //   history.pushState(null,'',window.location.href);
    // });
  }

  ngOnInit() {
    console.log("Session Remove for Authorized User =", sessionStorage.getItem('authorizedUser'))
    //this.dataSource = { data: [] };
    sessionStorage.removeItem('authorizedUser');
    sessionStorage.removeItem('redirectUrl');
    this.apiService.initialize();
    this.loading = true;
    // this.apiService.userName$.subscribe((name) => (this.userName = name));
    this.userName = localStorage.getItem('userName') as string;
    console.log(("_____________"));
    
    console.log(this.userName);
    
    this.userName=localStorage.getItem('userEmail') as string;
    const dashboardBodyParameters = {
      "user_name": localStorage.getItem('userName') as string,
      "search": {},
      "token": this.apiService.getToken()
    };
    console.log(dashboardBodyParameters);
    this.showUserName=localStorage.getItem('userName') as string;
    this.dashboardService.dashboardTableSearch(dashboardBodyParameters).subscribe((res) => {
      if (res.message == "User not authenticated") {
        this.showCustomAlertForUnauthenticatedUser("Failed to load, try again later.", true);
      } else if (res.status != 200) {
        this.loading = false;
        this.showCustomAlert("Failed to load, try again later.");
      }
      this.resDataArray = Object.values(res.data);
      this.resDataArray.sort((a: { sort_val: number; }, b: { sort_val: number; }) => a.sort_val - b.sort_val);
      this.updateOpenEditIcon();
      this.cardDataArray = res.data[0].stats;
      this.totalGeneratedRFPs = this.cardDataArray.total_generated_responses;
      this.totalUploadedRFPs = this.cardDataArray.total_uploaded_rfps;
      this.avgResponseTime = this.cardDataArray.avg_response_time;
      this.dataArray = this.resDataArray[0];

      // Create a new object excluding the 'stats' property
      const filteredDataArray: DataObject = Object.keys(this.dataArray)
        .filter(key => key !== 'stats')  // Exclude 'stats'
        .reduce((obj, key) => {
          obj[key] = this.dataArray[key];
          return obj;
        }, {} as DataObject);

      const resultArray = Object.values(filteredDataArray);
      console.log("Result Array for table =", resultArray);
      this.dataSource = new MatTableDataSource(resultArray);
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
      this.loading = false;
      // this.ascendingRfpID();
      this.sortData();
      this.isInProgress = resultArray.some((item: any) =>
        item.dashboard_status === 'In Progress');
      this.sharedService.updateStatus(this.isInProgress ? 'In Progress' : '');
    },
      // Error callback: Handle errors
      (error) => {
        this.loading = false;
        this.showCustomAlert("Failed to load, try again later.");
      }
    );
  }

  ngAfterViewInit() {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  createRfp() {
    
    this.router.navigate(['/uploadDocument'],{ skipLocationChange: true });
  }

  updateOpenEditIcon() {
    this.resDataArray.forEach((item: any) => {
      if (item.dashboard_status === 'RFP Uploaded') {
        item.review_button = "disabled";
        item.search_refinement_button = "disabled";
      } else if (['Queued', 'Processing', 'Ready for PA Review', 'Uploaded'].includes(item.dashboard_status)) {
        item.upload_button = "disabled";
      }
    });
  }

  refreshOnToggle() {
    this.refreshIcon = !this.refreshIcon;
    if (this.refreshIcon) {
      this.intervalId = setInterval(() => {
        this.dashboardSearch();
      }, 60000);
    }
    else {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  ngOnDestroy() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  }

  getCurrentDate(): string {
    const today = new Date();
    const year = today.getFullYear();
    const month = (today.getMonth() + 1).toString().padStart(2, '0'); // January is 0!
    const day = today.getDate().toString().padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  onPageChange(event: any) {
    this.pageSize = event.pageSize;
  }

  reset() {
    this.expertRequestID = '';
    this.accountName = '';
    this.region = '';
    this.language = "English";
  }

  filterData($event: any) {
    const filterValue = $event.target.value.toLowerCase();
    this.dataSource.filter = filterValue.trim().toLowerCase();
    this.dataSource.filterPredicate = (data: any, filter: any) => {
      const columnsToFilter = ['expert_request_id', 'upload_time', 'account_name', 'dashboard_status'];
      let found = false;
      columnsToFilter.forEach(column => {
        if (data[column] && data[column].toString().toLowerCase().includes(filter)) {
          found = true;
        }
      });
      return found;
    };
  }

  review_edit(element: any) {
    console.log("clicked", element);
    if ((element.dashboard_status == 'Ready for PA Review' || element.dashboard_status == 'Exported') && element.review_button == 'enabled') {
      this.apiService.dashboardElement = element;
      // this.router.navigate(["/review"]);
      this.router.navigate(['/review'], { skipLocationChange: true });
    }
  }

  feedback_edit(element: any) {
    console.log('feedback clicked', element);
    this.apiService.feedbackElement = element;
    this.apiService.feedbackFormExpId = element.expert_request_id;
    console.log(this.apiService.feedbackFormExpId);
    this.router.navigate(['/feedback'], { skipLocationChange: true });
  }

  refinement_edit(element: any) {
    // let token = localStorage.getItem('credential');
    console.log("clicked", element);
    if (element.search_refinement_button == 'enabled') {
      this.apiService.dashboardElement = element;
      const refinementBodyParameters = { "expert_request_id": this.apiService.dashboardElement.expert_request_id, "token": this.apiService.getToken() };
      this.apiService.rfpRefinement(refinementBodyParameters).subscribe((refinementResult) => {
        if (refinementResult.Fetched = true) {
          var element_data = refinementResult;
          console.log(element_data + "data of element_data");
          this.apiService.searchRefinementTableDatasource = element_data;
          this.router.navigate(['/refinement'], { skipLocationChange: true });
        }
      });
    }
  }

  // navigateToReview(element: any) {
  //   console.log("navigation clicked");
  //   if ((element.dashboard_status == 'In Progress' || element.dashboard_status == 'Completed')) {
  //     this.apiService.dashboardElement = element;
  //     console.log(this.apiService.dashboardElement);
  //     this.router.navigate(['/review'], { skipLocationChange: true });
  //   }
  //   if ((element.dashboard_status == 'Uploaded')) {
  //     this.apiService.dashboardElement = element;
  //     console.log(this.apiService.dashboardElement);
  //     this.router.navigate(['/refinement'], { skipLocationChange: true });
  //   }
  // }

  navigateToReview(element: any) {
    console.log("navigation clicked");
    if (element.dashboard_status == 'Completed') {
      this.apiService.dashboardElement = element;
      console.log(this.apiService.dashboardElement);
      this.router.navigate(['/review'], { skipLocationChange: true });
    }
    else if (element.dashboard_status == 'In Progress') {
      if (element.search_refinement_button == 'enabled') {
        const refinementBodyParameters = {
          "expert_request_id": element.expert_request_id,
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
      else if (element.search_refinement_button == 'disabled') {
        this.apiService.dashboardElement = element;
        console.log(this.apiService.dashboardElement);
        this.router.navigate(['/review'], { skipLocationChange: true });
      }
    }
  }

  toggleSortOrder() {
    this.isAscending = !this.isAscending;
    this.sortData();
  }

  sortData() {
    if (this.isAscending) {
      this.dataSource.data = this.dataSource.data.sort((a: any, b: any) => {
        return a.sort_val - b.sort_val;
      });
    } else {
      this.dataSource.data = this.dataSource.data.sort((a: any, b: any) => {
        return b.sort_val - a.sort_val;
      });
    }
    this.dataSource.data.forEach((element: any, index: any) => {
      if (this.isAscending) {
        // element.rfpID = index + 1;
        const totalItems = this.dataSource.data.length;
        element.rfpID = totalItems - index;
      }
      else {
        element.rfpID = index + 1;
        // const totalItems = this.dataSource.data.length;
        // element.rfpID = totalItems - index ;
      }
    });
  }


  downloadResponses(element: any) {
    this.loading = true;
    let data = {
      "expert_request_id": element.expert_request_id,
      "user_name": localStorage.getItem('userName'),
      "token": this.apiService.getToken()
    };
    this.apiService.downloadRfpResponses(data).subscribe((res) => {
      console.log(res);
      if (res.Downloaded === true) {
        this.loading = false;
        Swal.fire({
          title: '<span style="font-family: \'Google Sans\';">Success</span>',
          html: '<span style="font-family: \'Google Sans\';">Exported successfully</span>',
          icon: 'success',
          // showCancelButton: true,
          // confirmButtonColor: '#0B57D0',
          // confirmButtonText: '<span style="font-family: \'Google Sans\';">Yes</span>',
          // cancelButtonColor: '#C2E7FF',
          // cancelButtonText: '<span style="font-family: \'Google Sans\';">View Responses</span>',
          confirmButtonColor: '#0B57D0',
          confirmButtonText: '<span style="font-family: \'Google Sans\';">View Responses</span>',
          allowOutsideClick: false, // Prevents closing by clicking outside
          allowEscapeKey: false,
          customClass: {
            confirmButton: 'google-sans-button',
            // cancelButton: 'google-sans-button'
          },
          didRender: () => {
            const confirmButton = document.querySelector('.swal2-confirm') as HTMLElement;
            // const cancelButton = document.querySelector('.swal2-cancel') as HTMLElement;
            if (confirmButton) {
              confirmButton.style.borderRadius = '100px';
              confirmButton.style.fontFamily = 'Google Sans';
            }
            // if (cancelButton) {
            //   cancelButton.style.borderRadius = '100px';
            //   cancelButton.style.fontFamily = 'Google Sans';
            //   cancelButton.style.color = 'black';
            // }
          }
        }).then((result) => {
          if (result.isConfirmed) {
            let link = res.Link_to_sheet;
            console.log(link);
            window.open(link, '_blank');
          }
        });
      }
    },
      (error) => {
        this.loading = false;
        this.showCustomAlert("Failed to load, try again later.");
      }
    );
  }

  
  dashboardSearch() {
    // let token = localStorage.getItem('credential');
    this.loading = true;
    const data = {
      "user_name": localStorage.getItem('userName'),
      "search": {
        "expert_request_id": this.dashboard_upload.get('expertRequestID')?.value || empty,
        "account_name": this.dashboard_upload.get('accountName')?.value || empty,
        "region": this.dashboard_upload.get('region')?.value || empty,
        "language": this.dashboard_upload.get('language')?.value || 'English'
      },
      "token": this.apiService.getToken()
    };
    this.dashboardService.dashboardTableSearch(data).subscribe((res) => {
      console.log(res);
      if (res.status != 200) {
        this.loading = false;
        this.showCustomAlert("Failed to search, try again later.");
      }
      this.resDataArray = Object.values(res.data);
      this.resDataArray.sort((a: { sort_val: number; }, b: { sort_val: number; }) => a.sort_val - b.sort_val);
      this.updateOpenEditIcon();
      this.dataSource = new MatTableDataSource(this.resDataArray);
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
      this.loading = false;
      console.log(res.data);
    },
      (error) => {
        this.loading = false;
        this.showCustomAlert("Failed to search, try again later.");
      }
    );
    if (this.input && this.input.nativeElement) {
      this.input.nativeElement.value = '';
    }
  }

  showCustomAlert(message: any) {
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
    });
  }

  showCustomAlertForSucess(message: any) {
    Swal.fire({
      title: '<span style="font-family: \'Google Sans\';">RFP Accelarator</span>',
      html: `<span style="font-family: \'Google Sans\';">${message}</span>`,
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
        this.router.navigate(['/']);
        localStorage.clear();
      }
    });
  }

}
