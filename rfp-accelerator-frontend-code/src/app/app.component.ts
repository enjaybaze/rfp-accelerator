import { Component } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { NgZone } from '@angular/core';
import { Router } from '@angular/router';
import { ApiServiceService } from './api-service.service';
import { Location } from '@angular/common';
import Swal from 'sweetalert2';
// import { Router, ActivatedRoute, ParamMap } from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'RFP_Accelerator';

  constructor(private apiService: ApiServiceService, private location: Location, private router:Router) {
    // this.apiService.get().subscribe(next: () => {
    //   // do something
    // });
    // this.refreshAfterCertainTime();
  }
  
  // refreshAfterCertainTime() {
  //   const refreshInterval = 600000; // Time in milliseconds (e.g., 3000000 ms = 50 minutes)
  //   setTimeout(() => {
  //    window.location.href='/login';
  //   }, refreshInterval);
  //   setTimeout(() =>{
  //     Swal.fire({
  //       title: 'Alert',
  //       text: "Please save all your data, application going to refresh in 10 mins",
  //       icon: 'warning', // You can change the icon (success, error, warning, info, question)
  //       confirmButtonText: 'OK'
  //     });
  //   },30000);
  // }
}
