import { Component, Inject, ViewChild } from '@angular/core';
import { MatDrawer, MatSidenav } from '@angular/material/sidenav';
import { ApiServiceService } from '../api-service.service';
import { MatIconRegistry } from '@angular/material/icon';
import { DomSanitizer } from '@angular/platform-browser';
import { Router, ActivatedRoute, NavigationEnd } from '@angular/router';
import { SharedServiceService } from '../services/shared-service.service';
import { Idle } from '@ng-idle/core';

@Component({
  selector: 'app-template',
  templateUrl: './template.component.html',
  styleUrls: ['./template.component.scss']
})
export class TemplateComponent {
  userName: string | undefined;
  userEmail: string | undefined;
  userPhoto: string | undefined;
  rolePA: boolean = false;
  roleSME: boolean = false;
  roleAdmin: boolean = false;
  isExpanded = true;
  showSubmenu: boolean = false;
  isShowing = false;
  showSubSubMenu: boolean = false;
  isDashboard: boolean = false;
  showLogoff: boolean = false;
  isGenerateRfpDisabled = false;

  // @ViewChild('sidenav') sidenav: MatDrawer | undefined;
  @ViewChild('sidenav') sidenav: MatSidenav | undefined;

  constructor(private apiService: ApiServiceService, private router: Router, private idle: Idle, private route: ActivatedRoute, private matIconRegistry: MatIconRegistry, private domSanitzer: DomSanitizer, private sharedService: SharedServiceService) {
    this.matIconRegistry.addSvgIcon('homea', this.domSanitzer.bypassSecurityTrustResourceUrl('assets/icons/imagea.svg'))
      .addSvgIcon('addb', this.domSanitzer
        .bypassSecurityTrustResourceUrl('assets/icons/imageb.svg'))
      .addSvgIcon('addc', this.domSanitzer
        .bypassSecurityTrustResourceUrl('assets/icons/imagec.svg'))
      .addSvgIcon('addd', this.domSanitzer
        .bypassSecurityTrustResourceUrl('assets/icons/imaged.svg'))
      .addSvgIcon('adde', this.domSanitzer
        .bypassSecurityTrustResourceUrl('assets/icons/imagee.svg'))
      .addSvgIcon('addf', this.domSanitzer
        .bypassSecurityTrustResourceUrl('assets/icons/imagef.svg'))
  }
  ngOnInit(): void {
    this.apiService.initialize();
    this.apiService.userName$.subscribe((name) => (this.userName = name));
    // this.apiService.userEmail$.subscribe((email) => (this.userEmail = email));
    this.apiService.userPhoto$.subscribe((photo) => (this.userPhoto = photo));
    let userRole = localStorage.getItem('role');
    console.log("From Template " + userRole);
    if (userRole != undefined) {
      console.log("role set! ", userRole);
      if (userRole == "PA") {
        this.rolePA = true;
        this.roleSME = false;
        this.roleAdmin = false;
      }
      else if (userRole == "SME") {
        this.roleSME = true;
        this.rolePA = false;
        this.roleAdmin = false;
      }
      else if (userRole == "Admin") {
        this.roleAdmin = true;
        this.rolePA = false;
        this.roleSME = false;
      }
      else {
        // this.rolePA = true;
        this.rolePA = false;
        this.roleSME = false;
        this.roleAdmin = false;
      }
    }

    console.log(localStorage.getItem('userName'));
    this.userName=localStorage.getItem('userName') as string;
    
    this.router.events.subscribe((event) => {
      if (event instanceof NavigationEnd) {
        const currentRoute = this.route.snapshot.firstChild?.routeConfig?.path;
        this.isDashboard = currentRoute === 'dashboard';
        this.isGenerateRfpDisabled = currentRoute === 'refinement' || currentRoute === 'review';
      }
    });
    this.sharedService.status$.subscribe(status => {
      this.isGenerateRfpDisabled = (status === 'In Progress');
    });
  }


  handleImageError(event: any) {
    event.target.src = 'assets/user.png';
  }

  mouseenter() {
    if (!this.isExpanded) {
      this.isShowing = true;
    }
  }

  mouseleave() {
    if (!this.isExpanded) {
      this.isShowing = false;
    }
  }

  logout() {
    localStorage.setItem("isUserLoggedIN", "false");
    localStorage.clear();
    //sessionStorage.clear();
    this.idle.stop();
    this.router.navigate(['']);
  }

  toggleLogout() {
    this.showLogoff = !this.showLogoff;
  }
}



