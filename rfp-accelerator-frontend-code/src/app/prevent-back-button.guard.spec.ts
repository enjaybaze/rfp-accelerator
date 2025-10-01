import { TestBed } from '@angular/core/testing';
import { CanDeactivateFn } from '@angular/router';

import { preventBackButtonGuard } from './prevent-back-button.guard';

describe('preventBackButtonGuard', () => {
  const executeGuard: CanDeactivateFn = (...guardParameters) => 
      TestBed.runInInjectionContext(() => preventBackButtonGuard(...guardParameters));

  beforeEach(() => {
    TestBed.configureTestingModule({});
  });

  it('should be created', () => {
    expect(executeGuard).toBeTruthy();
  });
});
