import {
  Component,
  OnInit,
  ViewChild,
  HostListener,
  ElementRef,
  OnDestroy
} from "@angular/core";
import { FormBuilder, FormGroup, FormControl, FormArray } from "@angular/forms";
import { NgForm } from "@angular/forms";
import { DataService } from "../data.service";
import { Laptop } from "../laptop";
import data from "../../assets/dummyData.json";
import { MatPaginator } from "@angular/material/paginator";
import { MatTableDataSource, MatSort } from "@angular/material";
import { DataSource } from "@angular/cdk/table";
import * as $ from "jquery/dist/jquery.min.js";
import { WebsocketService } from "../websocket.service";

declare const callme: any;

@Component({
  selector: "app-home",
  templateUrl: "./home.component.html",
  styleUrls: ["./home.component.scss"]
})
export class HomeComponent implements OnInit, OnDestroy {
  // dummyData = <any>data;
  state: string = "";
  laptops: any[] = [];
  attributes: any[] = [];
  displayedColumns: string[] = ["image", "name", "price"];
  dataSource: MatTableDataSource<Laptop>;

  @ViewChild(MatPaginator) paginator: MatPaginator;
  @ViewChild(MatSort) sort: MatSort;

  sortingOptions: string[] = [
    "Relevance (default)",
    "Price (asc)",
    "Price (desc)",
    "Star Rating"
  ];

  brands = [
    { id: "acer", name: "Acer" },
    { id: "apple", name: "Apple" },
    { id: "dell", name: "Dell" },
    { id: "asus", name: "Asus" },
    { id: "fujitsu", name: "Fujitsu" },
    { id: "hp", name: "HP" },
    { id: "huawei", name: "Huawei" },
    { id: "lenovo", name: "Lenovo" },
    { id: "medion", name: "Medion" },
    { id: "msi", name: "MSI" },
    { id: "razer", name: "Razer" },
    { id: "samsung", name: "Samsung" },
    { id: "sony", name: "Sony" },
    { id: "toshiba", name: "Toshiba" }
  ];

  prices = [
    { id: { maxValue: 200 }, name: "< 200 €" },
    { id: { minValue: 200, maxValue: 400 }, name: "200 - 400 €" },
    { id: { minValue: 400, maxValue: 600 }, name: "400 - 600 €" },
    { id: { minValue: 600, maxValue: 800 }, name: "600 - 800 €" },
    { id: { minValue: 800, maxValue: 1000 }, name: "800 - 1000 €" },
    { id: { minValue: 1000 }, name: "> 1000 €" }
  ];

  ratings = [
    { id: { minValue: 4, maxValue: 5 }, name: "4 Stars and more" },
    { id: { minValue: 3, maxValue: 5 }, name: "3 Stars and more" },
    { id: { minValue: 2, maxValue: 5 }, name: "2 Stars and more" },
    { id: { minValue: 1, maxValue: 5 }, name: "1 Star and more" }
  ];

  processorManufacturers = [
    { id: "amd", name: "AMD" },
    { id: "intel", name: "Intel" }
  ];

  screenSizes = [
    { id: { maxValue: 10 }, name: "< 25 cm (10'')" },
    { id: { minValue: 11, maxValue: 12 }, name: "28 - 30 cm (11''-12'')" },
    { id: { minValue: 13, maxValue: 14 }, name: "33 - 36 cm (13''-14'')" },
    { id: { minValue: 15, maxValue: 16 }, name: "38 - 41 cm (15''-16'')" },
    { id: { minValue: 17 }, name: "> 43 cm (17'')" }
  ];

  processorCores = [
    { id: 2, name: "2 Cores" },
    { id: 4, name: "4 Cores" },
    { id: 6, name: "6 Cores" },
    { id: 8, name: "8 Cores" }
  ];

  processorSpeeds = [
    { id: { maxValue: 1.5 }, name: "< 1.5 GHz" },
    { id: { minValue: 1.5, maxValue: 1.9 }, name: "1.5 - 1.9 GHZ" },
    { id: { minValue: 2, maxValue: 2.9 }, name: "2 - 2.9 GHz" },
    { id: { minValue: 3 }, name: "> 3 GHz" }
  ];

  hardDriveTypes = [
    { id: "hdd", name: "HDD" },
    { id: "ssd", name: "SSD" },
    { id: "hybrid", name: "Hybrid" }
  ];

  hardDriveSizes = [
    { id: { maxValue: 128 }, name: "< 128 GB" },
    { id: { minValue: 128, maxValue: 256 }, name: "128 - 256 GB" },
    { id: { minValue: 256, maxValue: 512 }, name: "256 - 512 GB" },
    { id: { minValue: 512, maxValue: 1000 }, name: "512 - 1 TB" },
    { id: { minValue: 1000, maxValue: 2000 }, name: "1 - 2 TB" }
  ];

  operatingSystems = [
    { id: "windows", name: "Windows" },
    { id: "mac os", name: "MacOS" },
    { id: "linux", name: "Linux" }
  ];

  ramOptions = [
    { id: 2, name: "2 GB" },
    { id: 4, name: "4 GB" },
    { id: 6, name: "6 GB" },
    { id: 8, name: "8 GB" },
    { id: 12, name: "12 GB" },
    { id: 16, name: "16 GB" },
    { id: 24, name: "24 GB" },
    { id: 32, name: "32 GB" }
  ];

  weights = [
    { id: { maxValue: 1 }, name: "< 1 kg" },
    { id: { minValue: 1, maxValue: 1.5 }, name: "1 - 1.5 kg" },
    { id: { minValue: 1.5, maxValue: 2 }, name: "1.5 - 2 kg" },
    { id: { minValue: 2, maxValue: 2.5 }, name: "2 - 2.5 kg" },
    { id: { minValue: 2.5 }, name: "> 2.5 kg" }
  ];

  widgetForm = this.fb.group({
    brandName: this.fb.group({
      brandNameValue: this.fb.array([]),
      weight: [1]
    }),
    price: this.fb.group({
      priceRange: this.fb.array([]),
      weight: [1]
    }),
    avgRating: this.fb.group({
      avgRatingRange: this.fb.array([]),
      weight: [1]
    }),
    processorManufacturer: this.fb.group({
      processorManufacturerValue: this.fb.array([]),
      weight: [1]
    }),
    screenSize: this.fb.group({
      screenSizeRange: this.fb.array([]),
      weight: [1]
    }),
    processorCount: this.fb.group({
      processorCountValue: this.fb.array([]),
      weight: [1]
    }),
    processorSpeed: this.fb.group({
      processorSpeedRange: this.fb.array([]),
      weight: [1]
    }),
    hardDriveType: this.fb.group({
      hardDriveTypeValue: this.fb.array([]),
      weight: [1]
    }),
    hardDriveSize: this.fb.group({
      hardDriveSizeRange: this.fb.array([]),
      weight: [1]
    }),
    operatingSystem: this.fb.group({
      operatingSystemValue: this.fb.array([]),
      weight: [1]
    }),
    ram: this.fb.group({
      ramValue: this.fb.array([]),
      weight: [1]
    }),
    itemWeight: this.fb.group({
      itemWeightRange: this.fb.array([]),
      weight: [1]
    })
  });

  globalForm = new FormGroup({
    globalSearch: new FormControl()
  });
  arr;
  constructor(private dataService: DataService, private fb: FormBuilder) {}

  ngOnInit() {
    if (this.dataService.firstTime) {
      this.getSample();
      this.dataService.firstTime = false;
    } else {
      this.getLaptops();
    }
    this.arr = new Array(12);
    this.arr["brandName"] = 0 ;
    this.arr["price"] = 0;
    this.arr["avgRating"] = 0;
    this.arr["processorManufacturer"] = 0;
    this.arr["screenSize"] = 0;
    this.arr["processorCount"] = 0;
    this.arr["processorSpeed"] = 0;
    this.arr["hardDriveType"] = 0;
    this.arr["hardDriveSize"] = 0;
    this.arr["operatingSystem"] = 0;
    this.arr["ram"] = 0;
    this.arr["itemWeight"] = 0;
  }

  get brandNames() {
    return this.widgetForm.get("brandNames") as FormArray;
  }

  // get processorManufacturers() {
  //   return this.widgetForm.get("processorManufacturers") as FormArray;
  // }

  applyFilter(filterValue: string) {
    this.dataSource.filter = filterValue.trim().toLowerCase();
  }


  onHover(index:string) {
    //Sherif here, no idea why the hell arr has either 0 or 1, but noticed in onInputChange that arr[index ] = 1 only when weight = 5 so abused this.
    if(index != null  && this.arr[index] === 1){
        return "You chose weight 5 for this field, this means all the results will have the chosen value for this field."
    }
  }

  sortTable(sortingOption: string): void {
    if (sortingOption === "Price (asc)") {
      this.sort.sort({ id: "price", start: "asc", disableClear: false });
    }
    else if (sortingOption === "Price (desc)") {
      this.sort.sort({ id: "price", start: "desc", disableClear: false });
    }
    else if (sortingOption === "Star Rating") {
      this.sort.sort({ id: "avgRating", start: "desc", disableClear: false });
    }
    else {
      this.sort.sort({ id: "vaguenessScore", start: "desc", disableClear: false });
    }

  }


  onSubmit() {
    if (this.widgetForm.touched) {
      // console.log(this.widgetForm.value);
      // console.log(JSON.stringify(this.widgetForm.value));
      this.dataService
        .search(JSON.stringify(this.widgetForm.value))
        .subscribe(laptops => {
          //@ts-ignore
          this.dataService.laptops = laptops[0];
          // console.log(laptops[1]);
          this.attributes = [];
          // @ts-ignore
          this.laptops = laptops[0];
          let attributes = laptops[1];
          for (let attributesKey in attributes) {
            for (let y in attributes[attributesKey]) {
              let values = "";
              if (y.includes("Value")) {
                length = attributes[attributesKey][y].length;
                for (var i = 0; i < length; i++) {
                  values += attributes[attributesKey][y][i];
                  if (i != length - 1) {
                    values += "," + " ";
                  }
                }
              } else if (y.includes("Range")) {
                length = attributes[attributesKey][y].length;
                for (var i = 0; i < length; i++) {
                  let range = "";
                  if (!("maxValue" in attributes[attributesKey][y][i])) {
                    range = " > " + attributes[attributesKey][y][i]["minValue"];
                  } else if (!("minValue" in attributes[attributesKey][y][i])) {
                    range = "< " + attributes[attributesKey][y][i]["maxValue"];
                  } else {
                    range =
                      attributes[attributesKey][y][i]["minValue"] +
                      " - " +
                      attributes[attributesKey][y][i]["maxValue"];
                  }
                  values += range;
                  if (i != length - 1) {
                    values += "," + " ";
                  }
                }
              }
              let obj = {};
              if (attributesKey == "hardDriveSize") {
                obj["ssdSize"] = values;
                obj["hddSize"] = values;
              } else {
                obj[attributesKey] = values;
              }
              this.attributes.push(obj);
              break;
            }
            this.dataService.attributes = this.attributes;
          }
          this.dataSource = new MatTableDataSource(this.laptops);
          this.dataSource.sort = this.sort;
          this.dataSource.paginator = this.paginator;
        });
      window.scroll(0, 0);
    }
  }

  getSample() {
    this.dataService.getSample().subscribe(data => {
      this.dataService.laptops = data;
      this.laptops = data;
      this.dataSource = new MatTableDataSource(this.laptops);
      this.dataSource.sort = this.sort;
      this.dataSource.paginator = this.paginator;
    });
  }

  onChange(event, groupName, fieldName) {
    let field = (<FormArray>(
      this.widgetForm.controls[groupName].get(fieldName)
    )) as FormArray;

    if (event.checked) {
      field.push(new FormControl(event.source.value));
      field.markAsTouched();
    } else {
      const i = field.controls.findIndex(x => x.value === event.source.value);
      field.removeAt(i);
    }
  }

  getLaptops() {
    this.laptops = this.dataService.laptops;
    this.attributes = this.dataService.attributes;
    console.log(this.laptops[0].matched);
    this.dataSource = new MatTableDataSource(this.laptops);
    this.dataSource.sort = this.sort;
    this.dataSource.paginator = this.paginator;
  }
  onInputChange(event: any, index: string) {
    // console.log(event.value);
    if (event.value == 5) {
      this.arr[index] = 1;
    } else {
      this.arr[index] = 0;
    }
  }
  createRange(number) {
    var items: number[] = [];
    for (var i = 1; i <= number; i++) {
      items.push(i);
    }
    return items;
  }

  checkMatched(element: string) {
    if (element) {
      return true;
    }
    return false;
  }

  send() {
    // this.websocket.sendMessage('helllo');
  }

  ngOnDestroy() {
    // this.subscription.unsubscribe();
  }
}
