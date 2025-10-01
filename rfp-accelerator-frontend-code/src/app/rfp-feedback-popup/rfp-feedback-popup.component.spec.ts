import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RfpFeedbackPopupComponent } from './rfp-feedback-popup.component';

describe('RfpFeedbackPopupComponent', () => {
  let component: RfpFeedbackPopupComponent;
  let fixture: ComponentFixture<RfpFeedbackPopupComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [RfpFeedbackPopupComponent]
    });
    fixture = TestBed.createComponent(RfpFeedbackPopupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
