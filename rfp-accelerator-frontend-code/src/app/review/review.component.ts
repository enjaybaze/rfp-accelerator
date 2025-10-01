import { Component, OnInit, ViewChild } from '@angular/core';
import { MatPaginator, MatPaginatorModule } from '@angular/material/paginator';
import { MatTableDataSource, MatTableModule } from '@angular/material/table';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSort } from '@angular/material/sort';
import { ApiServiceService } from '../api-service.service';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { lastValueFrom, of, throwError } from 'rxjs';
import { catchError, retryWhen, delay, switchMap } from 'rxjs/operators';
import Swal from 'sweetalert2';
import * as XLSX from 'xlsx';
import { jsDocComment } from '@angular/compiler';
import { UploadDocumentService } from '../services/upload-document.service';
import { RfpFeedbackPopupComponent } from '../rfp-feedback-popup/rfp-feedback-popup.component';
import { MatDialog } from '@angular/material/dialog';
import { animate, state, style, transition, trigger } from '@angular/animations';
export interface TableData {
  sNo: any;
  question: string;
  searchRefinement: string;
  rfpAcceleratorResponse: string;
  feedback: string;
}

@Component({
  selector: 'app-review',
  templateUrl: './review.component.html',
  styleUrls: ['./review.component.scss']
})
export class ReviewComponent implements OnInit {
  @ViewChild(MatPaginator) paginator: MatPaginator | undefined;
  @ViewChild(MatSort) sort: MatSort | undefined;

  screen_title: string = 'PA - Review';
  displayedColumns: string[] = ['sNo', 'question', 'searchRefinement', 'rfpAcceleratorResponse', 'feedback'];
  dataSource: any;
  responseData: any;
  isEdit = false;
  isSaveResponse = false;
  isEditResponse = false;
  enableCheckbox = false;
  isEditFeedback = false;
  selected: any;
  runButton = false;
  editSearchRef = false;
  loading: boolean = false;
  dataSourceArray = [];
  showHide: boolean[] = [];
  prevDataSourceArray = [];
  combinedArray: any = [];
  allRowsExpanded: boolean = false;
  expandedElement: any;
  pageSizeOptions = [10, 15, 25, 100];
  pageSize = this.pageSizeOptions[0];
  editedRows: Set<number> = new Set<number>();

  form: FormGroup = new FormGroup({
  });
  accountName: any;
  id: any;
  pa_feedback: any;
  data: any;
  i: any;
  activeTabIndex = 0;
  modelResponse: any;
  feedback: any;
  approve: any;
  saveParams: any;
  expId: any;
  showSpinner = false;
  responseCompletion: any;
  timerCompletion: any;
  counter: any;
  limit: any;
  final_hit: any;
  x: any;
  totalTimeElapsed: number = 0;
  totalTime: number | undefined;
  data_exp: any;
  isFeedbackSaved: boolean = false;
  isFeedbackAdded: boolean = false;
  saveClicked: boolean = false;
  isFeedbackEdited = false;
  responseCompleted = false;
  feedbackEdited: boolean = false;
  exportEdited: boolean = true;
  totalQuestions: number = 0;
  feedback_request_id: any;
  length: number = 0;
  lengthCount: any;
  sheetsArray: any[] = [];
  disabled = false;
  showFirstLastButtons = true;
  showLess: any = '/assets/icons/collapse_more.svg';
  showMore: any = '/assets/icons/expand_more.svg';
  collapse: any = '/assets/icons/collapseall.svg';
  expand: any = '/assets/icons/expandall.svg';
  data_exp_review: any;
  fromRefinementPage: string | null = null;
  delayMs = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));
  constructor(private apiService: ApiServiceService, private dialog: MatDialog, private route: ActivatedRoute, private uploadDocumentService: UploadDocumentService, private fb: FormBuilder, private router: Router) { }

  ngOnInit() {
    this.responseData = [];
    this.route.queryParams.subscribe(params => {
      this.fromRefinementPage = params['param'];
      console.log('Received param1:', this.fromRefinementPage);
    });

    this.showHide = this.responseData.map(() => false);
    let dashboardComponentStatus = this.apiService.dashboardElement || { dashboard_status: 'Not Available' };
    console.log(dashboardComponentStatus);
    this.data_exp = dashboardComponentStatus.expert_request_id;
    console.log(this.data_exp);
    this.data_exp_review = this.apiService.exp_req_id;
    console.log(this.data_exp_review);
    //this.apiService.reviewToFeedbackExpID = this.data_exp_review;
    this.limit = this.uploadDocumentService.no_of_questions * 3;
    this.counter = 1;
    // this.loadData(this.data_exp);
    console.log("Response Completion= ", this.responseCompletion);
    if (this.fromRefinementPage != "Generate RFP" && (dashboardComponentStatus && dashboardComponentStatus.dashboard_status === "In Progress" || dashboardComponentStatus.dashboard_status === "Completed")) {
      console.log("From Dashboard");
      this.loadData(this.data_exp);
      dashboardComponentStatus = null;
    }
    else {
      console.log("From Review screen");
      console.log(this.data_exp_review);
      this.limit = this.uploadDocumentService.no_of_questions * 3;
      this.loadData(this.data_exp_review);
      //this.loadDataHit(this.data_exp_review);
    }
  }

  toggleAll() {
    this.allRowsExpanded = !this.allRowsExpanded;
    if (this.allRowsExpanded) {
      this.showHide = this.responseData[0].data.map(() => true);
    } else {
      this.showHide = this.responseData[0].data.map(() => false);
    }
  }

  toggle(index: number) {
    this.showHide[index] = !this.showHide[index];
  }

  loadDataHit(data: any) {
    this.loading = true;
    this.responseCompleted = false;
    console.log("counter= ", this.responseCompletion);
    let tokenValue = this.apiService.getToken();
    if ((this.counter <= this.limit || this.responseCompletion !== 100)) {
      const interval = setInterval(() => {
        this.counter++;

        let final_hit = this.counter === this.limit ? 1 : 0;

        let input = {
          "expert_request_id": data,
          "final_hit": final_hit,
          "token": this.apiService.getToken()
        };
      //  console.log(this.data_exp);

        this.apiService.reviewTableLoad(input).subscribe((res) => {
          console.log(res);

          if (res.data.waiting_data !== undefined) {
            this.combinedArray = res.data.processed_data.concat(res.data.waiting_data, res.data.error_data);
          } else {
            this.combinedArray = res.data.processed_data.concat(res.data.error_data);
          }

          if (res.Model_Finished === false) {
            this.responseCompletion = Math.floor(res.Model_Progress);
            this.timerCompletion = res.live_sec;
            if (this.combinedArray.length > 0) {
              const groupedByPageName = this.combinedArray.reduce((acc: any, obj: any) => {
                const { page_name, ...rest } = obj;
                acc.set(page_name, [...(acc.get(page_name) || []), rest]);
                return acc;
              }, new Map());

              this.data = Array.from(groupedByPageName, ([page_name, data]) => ({ page_name, data }));

              this.data.forEach((row: any) => {
                row.data.forEach((item: any) => {
                  if (item.run_model_status === "processed" || item.run_model_status === "error") {
                    item.rfpAcceleratorResponse = item.result1;
                  }
                });
              });

              this.dataSource = new MatTableDataSource(Array.from(this.data[0].data));
              this.responseData = this.data;
              this.dataSource.paginator = this.paginator;
              this.dataSource.sort = this.sort;
              // this.loading = false;
            }

          } else {
            clearInterval(interval); // Stop the interval if Model_Finished is true
            this.loading = false;
            this.responseCompleted = true;
            this.responseCompletion = Math.floor(res.Model_Progress);
            this.timerCompletion = res.live_sec;
            console.log("load_review else");

            if (this.combinedArray.length > 0) {
              const groupedByPageName = this.combinedArray.reduce((acc: any, obj: any) => {
                const { page_name, ...rest } = obj;
                acc.set(page_name, [...(acc.get(page_name) || []), rest]);
                return acc;
              }, new Map());

              this.data = Array.from(groupedByPageName, ([page_name, data]) => ({ page_name, data }));

              this.data.forEach((row: any) => {
                row.data.forEach((item: any) => {
                  if (item.run_model_status === "processed" || item.run_model_status === "error") {
                    item.rfpAcceleratorResponse = item.result1;
                  }
                });
              });

              this.dataSource = new MatTableDataSource(Array.from(this.data[0].data));
              this.responseData = this.data;
              this.dataSource.paginator = this.paginator;
              this.dataSource.sort = this.sort;
              //  this.loading = false;
              this.responseCompletion = res.Model_Progress;
              this.tabChanged(this.activeTabIndex);
              // this.tabChanged();
            }
          }

          if (this.responseCompletion === 100) {
            this.showSpinner = false;
            this.responseCompleted = true;
          }
        }, (error) => {
          clearInterval(interval);
          this.loading = false;
          if (this.apiService.getToken() != null) {
            this.showCustomAlertWarning("Failed to load the data, try again later.");
          }
        });

      }, 5000); // Interval runs every 5000ms (5 seconds)
    } else {
      console.log("Condition failed, stopping interval.");
      this.loading = false; // Ensure spinner is hidden if condition fails
    }
  }

  async loadData(data: any) {
    // this.loading = true;

    let final_hit = this.counter === this.limit ? 1 : 0;
    let input = {
      "expert_request_id": data,
      "final_hit": final_hit,
      "token": this.apiService.getToken()
    };

    try {
      // Define the observable with retry logic and delay
      const response$ = this.apiService.reviewTableLoad(input).pipe(
        retryWhen(errors =>
          errors.pipe(
            switchMap((error, index) => {
              const retryCount = index + 1;
              console.log(`Retry attempt: ${retryCount}`);
              if (retryCount >= 3) { // Number of retries
                return throwError(() => new Error('Max retry attempts reached'));
              }
              return this.delayMs(2000); // Delay between retries (2 seconds)
            })
          )
        ),
        catchError(error => {
          console.error('Error in API call:', error);
          this.showCustomAlertWarning("Failed to load, try again later.");
          this.showSpinner = false;
          return of(null); // Return null or empty observable if needed
        })
      );

      // Await for the result
      const res = await lastValueFrom(response$);
      console.log("Response data= ", res?.data);

      if (res?.data) {
        if (res.data.waiting_data !== undefined) {
          this.combinedArray = res.data.processed_data.concat(res.data.waiting_data, res.data.error_data);
        } else {
          this.combinedArray = res.data.processed_data.concat(res.data.error_data);
        }

        if (res.Model_Finished === false) {
          console.log("Data reload");
          this.responseCompletion = 0;

          if (this.combinedArray.length > 0) {
            const groupedByPageName = this.combinedArray.reduce((acc: any, obj: any) => {
              const { page_name, ...rest } = obj;
              acc.set(page_name, [...(acc.get(page_name) || []), rest]);
              return acc;
            }, new Map());

            this.data = Array.from(groupedByPageName, ([page_name, data]) => ({ page_name, data }));

            this.data.forEach((row: any) => {
              row.data.forEach((item: any) => {
                this.responseCompleted = true;
                item.isEditResponse = false;
                item.isEdit = false;
                item.isSaveFeedback = false;
                item.isEditFeedback = true;
                if (item.run_model_status === "waiting") {
                  item.rfpAcceleratorResponse = 'waiting';
                }
              });
            });

            this.responseData = this.data;
            this.dataSource = new MatTableDataSource(Array.from(this.data[0].data));
            this.dataSource.paginator = this.paginator;
            this.dataSource.sort = this.sort;

            if (this.responseCompletion !== 100) {
              await this.loadDataHit(data); // Wait for loadDataHit to complete
            }
          }
        } else {
          this.responseCompletion = Math.floor(res.Model_Progress);
          this.timerCompletion = res.live_sec;
          if (this.combinedArray.length > 0) {
            const groupedByPageName = this.combinedArray.reduce((acc: any, obj: any) => {
              const { page_name, ...rest } = obj;
              acc.set(page_name, [...(acc.get(page_name) || []), rest]);
              return acc;
            }, new Map());

            this.data = Array.from(groupedByPageName, ([page_name, data]) => ({ page_name, data }));

            this.data.forEach((row: any) => {
              row.data.forEach((item: any) => {
                if (item.run_model_status === "processed" || item.run_model_status === "exported" || item.run_model_status === "error") {
                  item.rfpAcceleratorResponse = item.result1;
                }
              });
            });

            this.responseData = this.data;
            this.dataSource = new MatTableDataSource(Array.from(this.data[0].data));
            this.dataSource.paginator = this.paginator;
            this.dataSource.sort = this.sort;
            this.responseCompleted = true;
            console.log(this.activeTabIndex);
            this.tabChanged(this.activeTabIndex);
            if (this.responseCompletion !== 100) {
              await this.loadDataHit(data); // Wait for loadDataHit to complete
            }
          }
        }
      } else {
        console.error('No data received from API');
      }
    } catch (error) {
      console.error('Error processing data:', error);
      this.showSpinner = false;
    }
  }


  tabChanged(index: number) {
    console.log(this.data[this.activeTabIndex]);
    console.log(this.dataSource.data);
    if (index != this.activeTabIndex) {
      this.activeTabIndex = index;
      this.dataSource = new MatTableDataSource(this.data[index].data);
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
      console.log("sheet tab has been changed");
    }
    else {
      this.activeTabIndex = index;
      this.dataSource = new MatTableDataSource(this.data[index].data);
      this.dataSource.paginator = this.paginator;
      this.dataSource.sort = this.sort;
      console.log("sheet tab has been changed");
    }
  }

  filterEditedRows() {
    console.log("Inside filterEditedRows");
    this.prevDataSourceArray = [...this.dataSourceArray];
    this.dataSourceArray = this.dataSourceArray.filter((row: any) => !this.editedRows.has(row.id));
    console.log(this.prevDataSourceArray);
    this.dataSource = new MatTableDataSource(this.dataSourceArray);
  }

  onPageChange(event: any) {
    this.pageSize = event.pageSize;
  }

  finalRepsonseSave() {
    this.isSaveResponse = false;
    this.isEditResponse = true;
  }

  finalRepsonseEdit() {
    this.isSaveResponse = true;
    this.isEditResponse = false;
  }

  onSave(item: any) {
    item.isEdit = false;
    item.checked = false;
    console.log(item.id);
    this.editedRows.add(item.id);
    console.log(this.editedRows);
  }

  saveData() {
    this.saveClicked = true;
    let saveArray: any[] = [];
    let saveData = this.dataSource.data;
    saveData.forEach((item: any) => {
      saveArray.push({

        "question_id": item.id,
        "pa_final_response": "",
        "pa_feedback": item.pa_feedback,
        "pa_approve_reject_override": "",
        "response": item.result1,
      });
    });

    this.saveParams = {
      "expert_request_id": this.data_exp,
      "save": saveArray,
      "user_name": localStorage.getItem('userName'),
      "token": this.apiService.getToken()
    }
    console.log(this.saveParams);
    this.apiService.saveReviewData(this.saveParams).subscribe((res) => {
      console.log(res);
      if (res.Saved === true) {
        Swal.fire({
          title: '<span style="font-family: \'Google Sans\';">Success</span>',
          html: '<span style="font-family: \'Google Sans\';">Feedback saved successfully.</span>',
          icon: 'success',
          confirmButtonColor: '#0B57D0',
          confirmButtonText: '<span style="font-family: \'Google Sans\';">OK</span>',
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
          if (result.isConfirmed) {
            this.apiService.exp_req_id = this.id;
          }
        });
        this.isFeedbackSaved = true;
      }
    },
      (error) => {
        this.showCustomAlertError("Failed to load, try again later.");
      });
    this.feedbackEdited = false;
    this.exportEdited = true;

  }

  onEditFeedback(element: any) {
    
    element.isFeedbackEdited = true;
    this.feedbackEdited = false;
    this.exportEdited = false;
  }

  onSaveFeedback(element: any) {

    element.isFeedbackEdited = false;
    this.feedbackEdited = true;

  }

  enableEdit(item: any) {
    if (item.checked) {
      item.isEdit = true;
    }
    else {
      item.isEdit = false;
    }
  }

  showCustomAlert(message: any) {
    Swal.fire({
      title: '<span style="font-family: \'Google Sans\';">RFP Accelarator</span>',
      html: `<span style="font-family: \'Google Sans\';">${message}</span>`,
      icon: 'warning', // You can change the icon (success, error, warning, info, question)
      confirmButtonText: '<span style="font-family: \'Google Sans\';">OK</span>',
      confirmButtonColor: '#0B57D0',
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

  openRfpFeedbackPopup(questionId: string) {
    console.log("Feedback pop up");
    const questionID = questionId;
    let feedbackArray: any[] = [];
    let feedbackData = this.dataSource.data;
    feedbackData.forEach((item: any) => {
      this.feedback_request_id = item.expert_request_id;
      feedbackArray.push({
        "s_no": item.q_id,
        "expert_request_id": item.expert_request_id,
        "question_id": item.id,
        "question": item.question,
        "pa_feedback": "",
        "model_response": item.result1,
        "search_refinement": item.search_refinement,
      });
    });

    const dialogRef = this.dialog.open(RfpFeedbackPopupComponent, {
      data: {
        rfpQuestionID: questionID,
        saveArray: feedbackArray,  // Pass saveArray to RfpFeedbackPopupComponent
        sheetName: this.responseData,
        export_request_id: this.feedback_request_id,
      },
      disableClose: true,
    });

    dialogRef.afterClosed().subscribe((result: any) => {
      console.log(result);
      //this.dataSource =result;
      if (result) {
        this.loadData(result);
      }
    });
  }

  downloadResponses() {
    this.showSpinner = true;
    let isFeedbackEdited = this.dataSource.data.some((item: any) => item.isEditFeedback);
    if (this.isFeedbackAdded) {
      if (this.saveClicked == false) {
        if (!this.isFeedbackSaved || this.isFeedbackSaved) {
          Swal.fire({
            title: '<span style="font-family: \'Google Sans\';">Feedback added is not saved</span>',
            html: '<span style="font-family: \'Google Sans\';">Do you want to proceed without saving?</span>',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#0B57D0',
            confirmButtonText: '<span style="font-family: \'Google Sans\';">Yes</span>',
            cancelButtonColor: '#C2E7FF',
            cancelButtonText: '<span style="font-family: \'Google Sans\';">No</span>',
            allowOutsideClick: false, // Prevents closing by clicking outside
            allowEscapeKey: false,
            customClass: {
              confirmButton: 'google-sans-button',
              cancelButton: 'google-sans-button'
            },
            didRender: () => {
              const confirmButton = document.querySelector('.swal2-confirm') as HTMLElement;
              const cancelButton = document.querySelector('.swal2-cancel') as HTMLElement;
              if (confirmButton) {
                confirmButton.style.borderRadius = '100px';
                confirmButton.style.fontFamily = 'Google Sans';
              }
              if (cancelButton) {
                cancelButton.style.borderRadius = '100px';
                cancelButton.style.fontFamily = 'Google Sans';
                cancelButton.style.color = 'black';
              }
            }
          }).then((result) => {
            if (result.isConfirmed) {
              this.proceedWithDownload();
            }
            else {
              this.showSpinner = false;
            }
          });
        } else {
          this.proceedWithDownload();
        }
      }
      else {
        this.proceedWithDownload();
      }
    } else {
      this.proceedWithDownload();
    }
  }


  proceedWithDownload() {
    let download_file_id;
    if (this.fromRefinementPage != "Generate RFP"){
      download_file_id = this.data_exp;
    }
    else{
      download_file_id = this.data_exp_review;
    }
    let data = {
      "expert_request_id": download_file_id,
      "user_name": localStorage.getItem('userName'),
      "token": this.apiService.getToken()
    };

    this.apiService.downloadRfpResponses(data).subscribe((res) => {
      console.log(res);
      this.loading = false;
      if (res.Downloaded === true) {
        Swal.fire({
          title: '<span style="font-family: \'Google Sans\';">Success</span>',
          html: '<span style="font-family: \'Google Sans\';">Exported successfully</span>',
          icon: 'success',
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
            
          }
        }).then((result) => {
          if (result.isConfirmed) {
            this.showSpinner = false;
            let link = res.Link_to_sheet;
            console.log(link);
            window.open(link, '_blank');
          }
          else{
            this.showSpinner = false;
          }
        });
      }
    },
      (error) => {
        this.showSpinner = false;
        this.showCustomAlertError("Failed to load, try again later.");
      }
    );
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
    }).then((result) => {
      this.loading = false;
    });
  }

  ngOnDestroy() {
    this.clearData(); // Ensure cleanup when the component is destroyed
  }

  clearData() {
    this.data_exp = null;
    this.data_exp_review = null;
  }

  showCustomAlertError(message: any) {
    Swal.fire({
      title: '<span style="font-family: \'Google Sans\';">RFP Accelarator</span>',
      html: '<span style="font-family: \'Google Sans\';">Failed to load, try again later.</span>',
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

}