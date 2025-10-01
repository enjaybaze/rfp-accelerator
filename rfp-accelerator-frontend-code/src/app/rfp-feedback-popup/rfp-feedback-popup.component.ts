import { Component, Inject, OnInit, ViewChild } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { ApiServiceService } from '../api-service.service';
import Swal from 'sweetalert2';
import { Router } from '@angular/router';
import { MatPaginator, PageEvent } from '@angular/material/paginator';


@Component({
  selector: 'app-rfp-feedback-popup',
  templateUrl: './rfp-feedback-popup.component.html',
  styleUrls: ['./rfp-feedback-popup.component.scss']
})
export class RfpFeedbackPopupComponent implements OnInit {
  @ViewChild(MatPaginator, { static: false }) paginator!: MatPaginator;
  displayedColumns: string[] = ['sNo', 'question', 'search_refinement', 'model_response'];
  rfpQuestionID: string | undefined;
  feedbackArray: any[] = [];
  isRfpQuestionIDPresent: boolean = false;
  filteredDetails: any[] = [];
  currentPage = 1;
  totalQuestions = 0;
  currentPageData: any = {};
  paginationDisabled: boolean = false;
  saveParams: any;
  data_exp: any;
  id: any;
  processedData: any;
  isButtonDisabled: boolean = false;

  constructor(@Inject(MAT_DIALOG_DATA) public data: any, private apiService: ApiServiceService, private router: Router, private dialogRef: MatDialogRef<RfpFeedbackPopupComponent>) {
    console.log("data= ", data);
    this.rfpQuestionID = data.rfpQuestionID;
    this.data_exp = data.export_request_id;
  }

  ngOnInit() {
    //  this.data_exp = this.apiService.reviewToFeedbackExpID;
    this.processData();
    this.checkRfpQuestionIDPresence();
  }

  processData() {
    this.processedData = JSON.parse(JSON.stringify(this.data));

    this.processedData.sheetName.forEach((sheet: { data: { index: any; }[]; }, sheetIndex: any) => {
      sheet.data.forEach((item: { index: any; }, itemIndex: number) => {
        item.index = itemIndex + 1; // Add index value (1-based index)
      });
    });
    this.feedbackArray = this.processedData.sheetName;
    console.log('Processed Data:', this.feedbackArray);
  }

  closeFeedback() {
    Swal.fire({
      title: '<span style="font-family: \'Google Sans\';">RFP Accelerator</span>',
      html:  '<span style="font-family: \'Google Sans\';">Are you sure you want to close? Your feedback will be lost.</span>',
      icon: 'question',
      showCancelButton: true,
      confirmButtonColor: '#0B57D0',
      cancelButtonColor: '#C2E7FF',
      confirmButtonText:  '<span style="font-family: \'Google Sans\';">Discard Changes</span>',
      cancelButtonText:  '<span style="font-family: \'Google Sans\';">Continue Editing</span>',
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
        this.dialogRef.close();
      } else {
      }
    });
  }

  hideQueryParams() {
    const baseUrl = window.location.origin + '/review';
    window.history.replaceState({}, '', baseUrl);
  }

  checkRfpQuestionIDPresence() {
    this.filteredDetails = [];
    for (const sheet of this.processedData.sheetName) {
      const matchingData = sheet.data.find((item: any) => item.id === this.rfpQuestionID);
      console.log("Matching data =", matchingData);
      if (matchingData) {
        this.filteredDetails.push({
          page_name: sheet.page_name,
          feedback_data: matchingData,
          total_Questions: sheet.data.length,
        });
        console.log("filteredDetails =", this.filteredDetails);
        this.totalQuestions = sheet.data.length;
      }
    }

    this.isRfpQuestionIDPresent = this.filteredDetails.length > 0;
    if (this.isRfpQuestionIDPresent) {
      this.currentPageData = this.filteredDetails[this.currentPage - 1].feedback_data;
      if (!this.currentPageData.feedback) {
        this.currentPageData.feedback = '';
      }
      console.log("current data =", this.currentPageData);
      this.paginationDisabled = this.currentPageData.index === 1 || this.currentPageData.index === this.totalQuestions;
    }
  }

  goToPage(data: any, selectedIndex: number) {
    this.filteredDetails = []; // Clear previous filtered data
    const sheetName = data[0].page_name;
    console.log("feedback data =", sheetName);
    this.filteredDetails = []; // Clear previous filtered data
    this.feedbackArray.forEach(sheet => {
      console.log(sheet.page_name);
      if (sheet.page_name === sheetName) {
        const matchingData = sheet.data.find((item: any) => item.index === selectedIndex);
        if (matchingData) {
          this.filteredDetails.push({
            page_name: sheet.page_name,
            feedback_data: matchingData,
            total_Questions: sheet.data.length,
          });
        }
        this.totalQuestions = sheet.data.length;
      }
    });

    this.isRfpQuestionIDPresent = this.filteredDetails.length > 0;
    if (this.isRfpQuestionIDPresent) {
      this.currentPageData = this.filteredDetails[0].feedback_data;
      console.log("filteredDetails >", this.filteredDetails);
      console.log("feedbackArray >", this.feedbackArray);// Assuming first item since filteredDetails is reset
      this.paginationDisabled = this.currentPageData.index === 1 || this.currentPageData.index === this.totalQuestions;
    }
  }

 saveReviewData() {
  this.isButtonDisabled = true;
   let saveArray: any[] = [];
    console.log("filteredDetails", this.filteredDetails);
    console.log("feedbackArray", this.feedbackArray);
  
    let saveData: any[] = this.feedbackArray.flatMap(item => item.data);
    saveData.forEach((item: any) => {
      saveArray.push({
        "question_id": item.id,
        "pa_final_response": "",
        "pa_feedback": item.pa_feedback,
        "pa_approve_reject_override": "",
        "response": item.result1,
      });
    });
    console.log("saveArray", saveArray);
    
    this.saveParams = {
      "expert_request_id": this.data_exp,
      "save": saveArray,
      "user_name": localStorage.getItem('userName'),
      "token": this.apiService.getToken()
    }
    
    console.log(this.saveParams);
    this.apiService.saveReviewData(this.saveParams).subscribe((res) => {
      if (res.status !== 200) {
        this.isButtonDisabled = false;
        this.showCustomAlertWarning("Failed to save feedback. Please try again later.");
      } else {
        this.isButtonDisabled = true;
        this.dialogRef.close(this.data_exp);
      }
    }, (error) => {
      this.showCustomAlertWarning("Failed to save feedback. Please try again later.");
    }).add(() => {
      // Re-enable the button if needed
      this.isButtonDisabled = false;
    });
  }
  

  showCustomAlertWarning(message: string) {
    Swal.fire({
      title: '<span style="font-family: \'Google Sans\';">Error</span>',
      html: '<span style="font-family: \'Google Sans\';">Failed to save feedback. Please try again later.</span>',
      icon: 'warning',
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

  toggleEditMode(element: any) {
    element.editMode = !element.editMode;
  }
}
