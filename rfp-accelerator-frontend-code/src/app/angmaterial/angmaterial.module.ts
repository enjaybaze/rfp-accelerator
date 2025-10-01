import { NgModule } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import {MatToolbarModule} from '@angular/material/toolbar';
import { MatDividerModule } from '@angular/material/divider';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatInputModule } from '@angular/material/input';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import {ReactiveFormsModule } from '@angular/forms';
import {MatTabsModule} from '@angular/material/tabs';
import {MatSidenavModule} from '@angular/material/sidenav';
import {MatTableDataSource, MatTableModule} from '@angular/material/table';
import {MatPaginator, MatPaginatorModule} from '@angular/material/paginator';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import {MatSelectModule} from '@angular/material/select';
import {MatRadioModule} from '@angular/material/radio';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {MatTooltipModule} from '@angular/material/tooltip';
import { MatSlideToggleModule} from '@angular/material/slide-toggle';

// import { MatHorizontalScrollModule } from '@angular/material/horizontal-scroll';
// import { CommonModule } from '@angular/common';

const angMaterialComponent =[ 
  MatCardModule,
  MatFormFieldModule,
  MatInputModule,
  FormsModule,
  MatSidenavModule,
  MatListModule,
  ReactiveFormsModule,
  MatButtonModule,
  MatToolbarModule,
  MatTabsModule,
  MatCheckboxModule,
  MatProgressSpinnerModule,
  // MatPaginator, 
  MatPaginatorModule,
  // MatTableDataSource, 
  MatTableModule,
  MatRadioModule,
  MatIconModule,
  MatTooltipModule,
  MatDividerModule,
  MatProgressBarModule,
  HttpClientModule,
  MatSelectModule,
  MatSlideToggleModule
  
  // MatHorizontalScrollModule];
];

@NgModule({
  imports: [angMaterialComponent],
  exports:[angMaterialComponent]
})
export class AngmaterialModule { }
