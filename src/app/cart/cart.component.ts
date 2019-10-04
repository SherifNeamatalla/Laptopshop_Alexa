import { Component, OnInit } from "@angular/core";
import { moveIn, fallIn } from "../routing.animations";

@Component({
  selector: "app-cart",
  templateUrl: "./cart.component.html",
  styleUrls: ["./cart.component.scss"],
  animations: [moveIn(), fallIn()],
  host: { "[@moveIn]": "" }
})
export class CartComponent implements OnInit {
  constructor() {}

  ngOnInit() {}
}
