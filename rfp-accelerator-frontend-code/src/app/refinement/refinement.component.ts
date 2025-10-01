import { Component, ViewChild, OnInit } from '@angular/core';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSort } from '@angular/material/sort';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ApiServiceService } from '../api-service.service';
import { Observable, Observer } from 'rxjs';
import { AsyncPipe } from '@angular/common';
import { Router } from '@angular/router';
import Swal from 'sweetalert2';
import { SharedServiceService } from '../services/shared-service.service';

export interface TableData {
  qNo: number;
  question: string;
  searchRefinement: string;
}

@Component({
  selector: 'app-refinement',
  templateUrl: './refinement.component.html',
  styleUrls: ['./refinement.component.scss']
})
export class RefinementComponent implements OnInit {
  @ViewChild(MatPaginator) paginator: MatPaginator | undefined;
  @ViewChild(MatSort) sort: MatSort | undefined;

  screen_title: string = 'PA - RFP Refinement';
  refinement_data: FormGroup = new FormGroup({
    expertRequestID_refinement: new FormControl('', [Validators.required]),
    accountName_refinement: new FormControl('', [Validators.required]),
  });
  accountName: any;
  id: any;
  displayedColumns: string[] = ['qNo', 'question', 'searchRefinement'];
  // dataSource = new MatTableDataSource();
  dataSource: any;
  i: any;
  dataArray: any;
  data: any;
  $user: any;
  activeTabIndex = 0;
  item: boolean | undefined;
  isEdit = false;
  disabled = false;
  pageSizeOptions = [10, 15, 25, 100];
  pageSize = this.pageSizeOptions[0];
  showFirstLastButtons = true;
  loading = false;
  no_of_questions: any;
  num_questions: any;
  totalQuestions: number = 0;
  length: number = 0;
  lengthCount: any;

  constructor(private apiService: ApiServiceService, private router: Router,private sharedService: SharedServiceService) {
    this.activeTabIndex = 0;
  }

  ngOnInit() {
    //this.apiService.initialize();
    this.dataArray = [];
    this.data = this.apiService.searchRefinementTableDatasource;
    console.log(this.data);
    this.dataArray = this.data.questions;
    console.log("Data questions: ")
    console.log(this.dataArray)
    let size = this.dataArray.length;
    console.log(size);
    this.i = 0;
    console.log("Printing index variable size : ")
    console.log(this.i)
    this.dataSource = new MatTableDataSource(this.dataArray[this.i].data);
    console.log("Final data source shich should display on UI: ")
    console.log(this.dataSource);
    let arr = [];
    arr = this.apiService.searchRefinementTableDatasource;
    this.accountName = this.data.account_name;
    this.id = this.data.expert_request_id;

  }

  tabChanged(index: number) {
    console.log(this.dataSource.data);
    console.log(this.dataArray[this.activeTabIndex].data);
    if (this.dataSource.data == this.dataArray[this.activeTabIndex].data) {
      this.activeTabIndex = index;
      this.dataSource = new MatTableDataSource(this.dataArray[index].data);
      console.log("data has not been edited");
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
    }
    else {

      this.activeTabIndex = index;
      this.dataSource = new MatTableDataSource(this.dataArray[index].data);
      console.log("data has been edited");
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
    }
  }

  ngAfterViewInit() {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  onPageChange(event: any) {
    this.pageSize = event.pageSize;
  }

  refinementRunModel() {
    this.disabled = true;
    let username = localStorage.getItem('userName');
    const modelData = {
      "expert_request_id": this.id,
      "user_name": username,
      "token": this.apiService.getToken()
    };
    const expId = this.id;

    let modelJson = {
      "run": modelData,
      "token": this.apiService.getToken()
    };
    console.log(modelData);
    this.loading = true; // Show spinner when the API call is initiated
    this.apiService.refinementRunModel(modelJson).subscribe((res) => {
      console.log(res);
      if (res.model_requested === true) {
        this.apiService.refinementRunModelTrigger(modelData).subscribe((result) => {
          console.log(result);
          this.apiService.exp_req_id = expId;
          console.log(this.apiService.exp_req_id);
          this.router.navigate(['/review'], {
            queryParams: { param: 'Generate RFP' },
            skipLocationChange: true
          });
          // this.checkProgressWithSpinner(modelData);
        },
          (error) => {
            this.loading = false;
            this.showCustomAlertWarning("Failed to load, try again later");
          }
        );
      }
    },
      (error) => {
        this.loading = false;
        this.showCustomAlertWarning("Failed to load, try again later.");
      }
    );
  }

 

  onEdit(item: any) {
    item.isEdit = true;

  }

  onSave(item: any) {
    item.isEdit = false;
    console.log(this.dataArray[this.activeTabIndex].data);

  }

  deleteRfp() {
    this.sharedService.clearStatus();
    let value = { "expert_request_id": this.id, "token": this.apiService.getToken() };
    this.apiService.deleteData(value).subscribe((res) => {
      console.log(res);
      if (res.removed == true) {
        this.router.navigate(['/uploadDocument'],{ skipLocationChange: true });
      }
    });
  }

  showCustomAlert(res: any) {
    if (res.Processed == "true") {
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

  showCustomAlertWarning(message: any) {
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
}