import { HttpClient } from '@angular/common/http';
import { Component, NgZone, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { ApiServiceService } from '../api-service.service';
import Swal from 'sweetalert2';
import { Location } from '@angular/common';
import { BaseurlService } from '../services/baseurl.service';
import { Idle } from '@ng-idle/core';

interface RedirectURIs {
    [key: string]: string;
}

@Component({
    selector: 'app-login',
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.scss'],
    providers: [],
})
export class LoginComponent implements OnInit {
    userNameFormControl = new FormControl('', Validators.required);
    
      passwFormControl = new FormControl('', Validators.required);
      showGenericLogin:boolean=false;
      showSpinner=true;

    greeting: string | undefined;
    currentUrl: string | undefined;
    email: string | undefined;
    flagTimeout: boolean = true;
    userName: string | undefined;
    password: string | undefined;
    token: string | undefined;
    loginMessage: string | undefined;
    
    hide = true;
    
    constructor(private idle: Idle, private router: Router, private route: ActivatedRoute, private ngZone: NgZone, private baseurlService: BaseurlService, private httpClient: HttpClient, private apiService: ApiServiceService, private location: Location) {
    }

    ngOnInit() {
        const redirectUrl = sessionStorage.getItem('redirectUrl');
        console.log("Session Storage redirectUrl =", redirectUrl);
        if (redirectUrl) {
            sessionStorage.setItem('authorizedUser', 'true');
            const redirectUri = this.getRedirectUri();

        }
    }

    backToLogin(){
        console.log("back to login");
        this.showGenericLogin=false;        
        
    }

    getRedirectUri(): string {
        const currentUrl = window.location.href;
        const hostname = new URL(currentUrl).hostname;
        const redirectURIs: RedirectURIs = {
            'localhost': 'http://localhost:4200/',
        };
        return redirectURIs[hostname];
    }



    async userSignIn() {
        this.baseurlService.loadConfig();

        this.userNameFormControl.reset();
        this.passwFormControl.reset();

        this.showGenericLogin=true;
    }

    async generalSignIn(){
        console.log(this.userNameFormControl.value);
        console.log(this.passwFormControl.value);
        this.showGenericLogin=false;
        let user_login:any=this.userNameFormControl.value;
        let passw_login:any=this.passwFormControl.value;

        this.userNameFormControl.reset();
        this.passwFormControl.reset();
        const body={
            "username": user_login,
             "password": passw_login
        }
        this.showSpinner=false;
        localStorage.setItem('userName', user_login);
        this.apiService.generalSignInAPI(body).subscribe({
            next:(res:any)=>{
                console.log(res);
                this.showSpinner=true;

                if(res.exists === true){
                    let role = res.role;
                    console.log('role', role);
                    localStorage.setItem('role', role);

                    
                    localStorage.setItem('auth_token', res.token);
                    this.apiService.saveToken(res.token);
                    this.apiService.token = localStorage.getItem('auth_token') ?? undefined;

                    console.log('LS role', localStorage.getItem('role'));
                    let title = "";
                    if (role == "SME") title = "Home Page";
                    else if (role == "Admin") title = "Home Page";
                    else if (role == "PA") title = "Home Page";
                    else {
                        this.router.navigate(["/error"], { skipLocationChange: true });
                    }

                    if (localStorage.getItem('role')) {
                        console.log('-----Welcome back!');
                        localStorage.setItem("isUserLoggedIN", "true");
                        let status = localStorage.getItem('isUserLoggedIN') == 'true' ? true : false;
                        console.log("LOGIN ? :" + status);

                    }

                    this.router.navigate(["/dashboard"]);
                }else {
                    localStorage.clear()
                    Swal.fire({
                        title: '<span style="font-family: \'Google Sans\';">RFP Accelarator</span>',
                        html: `<span style="font-family: \'Google Sans\';">${res.message}</span>`,
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
                
            },
            error:(err:any)=>{
                localStorage.clear()
                this.showSpinner=true;
                console.log(err);
                this.showCustomAlert("Failed to load, try again later.");
                
            }
        }
       )

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
}
