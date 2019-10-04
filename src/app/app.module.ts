import { BrowserModule } from "@angular/platform-browser";
import { NgModule } from "@angular/core";
import { HttpClientModule } from "@angular/common/http";

import { AppRoutingModule } from "./app-routing.module";
import { AppComponent } from "./app.component";
import { HomeComponent } from "./home/home.component";
import { DetailsComponent } from "./details/details.component";
import { HeaderComponent } from "./header/header.component";
import { CartComponent } from "./cart/cart.component";

import { FlexLayoutModule } from '@angular/flex-layout';
import { FormsModule, ReactiveFormsModule } from "@angular/forms";

import { MatToolbarModule } from "@angular/material/toolbar";
import { MatButtonModule } from "@angular/material/button";
import { MatInputModule } from "@angular/material/input";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatIconModule } from "@angular/material/icon";
import { MatListModule } from "@angular/material/list";
import { MatCheckboxModule } from "@angular/material/checkbox";
import { MatCardModule } from "@angular/material/card";
import { MatSliderModule } from "@angular/material/slider";
import { MatMenuModule } from "@angular/material/menu";
import {MatTableModule, MatPaginatorModule,  MatSortModule, MatRadioModule, MatSelectModule, MatTooltipModule} from "@angular/material";
import { StarRatingModule } from 'angular-star-rating';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { WebsocketService } from './websocket.service';
import {DataService} from './data.service';

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    DetailsComponent,
    HeaderComponent,
    CartComponent
  ],
  imports: [
    BrowserAnimationsModule,
    MatTooltipModule,
    BrowserModule,
    ReactiveFormsModule,
    HttpClientModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    FlexLayoutModule,
    FormsModule,
    MatToolbarModule,
    MatButtonModule,
    MatInputModule,
    MatFormFieldModule,
    MatIconModule,
    MatListModule,
    MatCheckboxModule,
    MatCardModule,
    MatSliderModule,
    MatMenuModule,
    MatTableModule,
    MatPaginatorModule,
    MatSortModule,
    MatRadioModule,
    MatSelectModule,
    MatTooltipModule,
    StarRatingModule.forRoot()
  ],
  providers: [HomeComponent, DetailsComponent,DataService, WebsocketService],
  bootstrap: [AppComponent]
})
export class AppModule {}
