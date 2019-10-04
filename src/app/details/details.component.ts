import { Component, Input, OnInit } from "@angular/core";
import { DataService } from "../data.service";
import { Laptop } from "../laptop";
import { HomeComponent } from "../home/home.component";
import { moveIn, fallIn } from "../routing.animations";

import { HttpClient } from 'selenium-webdriver/http';
import { HttpResponse } from '@angular/common/http';
import { FormsModule, NgForm } from '@angular/forms';
import { NgModule } from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {Observable} from 'rxjs';
import { keyValuesToMap } from '@angular/flex-layout/extended/typings/style/style-transforms';
import {WebsocketService} from '../websocket.service';
import {MatTableDataSource} from '@angular/material';


@Component({
  selector: "app-details",
  templateUrl: "./details.component.html",
  styleUrls: ["./details.component.scss"],
})
export class DetailsComponent implements OnInit {

  asin;
  brandName: string;
  laptops: Laptop[] = [];
  item: Laptop;
  firstTime  = true;
  constructor(private dataService: DataService,
              private route: ActivatedRoute,
              private homeFeatures: HomeComponent, private router:Router) {

    this.dataService.getResult()
      .subscribe((message) => {
        this.router.navigate(['home']);
        this.dataService.laptops = message;
      });
  }


  ngOnInit() {
    this.asin = this.route.snapshot.params['asin'];
    this.showDetails();

  }

  showDetails() {
    this.dataService.getLaptop_details(this.asin).subscribe(data => {
      this.item = data[0];
      this.sendItem();
      // console.log(this.item.imagePath);
    });
  }

  sendItem(){
    let laptop = "{";
    const mapped = Object.keys(this.item).map(key => ({ type: key, value: this.item[key] }));
    console.log(mapped);
    for(let i in mapped){
      if (mapped[i]['type'] == 'asin' || mapped[i]['type'] == 'productTitle' || mapped[i]['type'] == 'displayResolutionSize'
        || mapped[i]['type'] == 'productDimension'){
        continue;
      }
      if ((mapped[i]['type'] == 'hddSize' && mapped[i]['value'] == 0) || (mapped[i]['type'] == 'ssdSize' && mapped[i]['value'] == 0)) {
        continue;
      }
      if (mapped[i]['value'] == null) {
        continue;
      }
      if (mapped[i]['type'] == 'price') {
        laptop = laptop + '"' + mapped[i]['type'] + '"';
        laptop += ' :{';
        laptop += '"' + 'value' + '"';
        laptop += ':' + '"' + mapped[i]['value'] + '"';
        laptop += ', ';
        laptop += '"weight" : 1 },'
      } else{
        laptop = laptop + '"' + mapped[i]['type'] + '"';
        laptop += ' :{';
        laptop += '"' + mapped[i]['type'] + 'Value' + '"';
        laptop += ':' + '"' + mapped[i]['value'] + '"';
        laptop += ', ';
        laptop += '"weight" : 1 },'
      }

    }
    laptop = laptop.substring(0, laptop.length - 1);
    laptop += "}";
    // console.log(laptop);
    laptop = JSON.parse(JSON.stringify(laptop));
    // console.log(laptop);
    this.dataService.setLaptop(laptop).subscribe(data=>console.log(data));
  }

  sendLaptops(){
    this.dataService.getCritizedResult();
  }
}
