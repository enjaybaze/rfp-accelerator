import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SharedServiceService {
  private statusSubject = new BehaviorSubject<string>(localStorage.getItem('fileStatus') || '');
  status$ = this.statusSubject.asObservable();

  constructor() { }

  updateStatus(status: string){
    localStorage.setItem('fileStatus',status)
    this.statusSubject.next(status);
  }

  clearStatus(): void{
    localStorage.removeItem('fileStatus');
    this.statusSubject.next('');
  }
}
