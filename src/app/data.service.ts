import { Injectable } from "@angular/core";
import { HttpClient, HttpHeaders } from "@angular/common/http";
import { Laptop } from "./laptop";
import { Observable } from 'rxjs';
import * as io from 'socket.io-client';
import {Router} from '@angular/router';

@Injectable({
  providedIn: "root"
})
export class DataService {
  //sampleUrl = "../assets/amazonDataSample.json";
  private url = 'http://localhost:5004/';
  private socket;
  laptops : any[];
  attributes : any[];
  firstTime = true ;
  laptop : Laptop;

  httpOptions = {
    headers: new HttpHeaders({
      'Content-Type':  'application/json',
      // 'Authorization': 'my-auth-token'
    })
  };

  constructor(private http: HttpClient, private router:Router) {
     this.socket = io.connect(this.url);
  }

  getSample() : Observable<Laptop[]>{
    return this.http.get<Laptop[]>('/api/sample');
  }

  search(file:any): Observable<Laptop[]>{
    return this.http.post<Laptop[]>('/api/search', file, this.httpOptions);
  }

  searchText(file:any): Observable<any[]>{
    return this.http.post<any[]>('/api/searchText', file, this.httpOptions);
  }

  getLaptop_details(asin:String){
    return this.http.get<Laptop>('/api/' + asin,this.httpOptions);
  }

  setLaptop(laptop): Observable<Laptop>{
    return this.http.post<Laptop>('/alexa/setter', laptop, this.httpOptions);
  }
  getCritizedResult(): Observable<Laptop[]> {
      return this.http.get<Laptop[]>('/alexa/getQuery')
  }


  public getResult(): Observable<Laptop[]> {
      return new Observable<Laptop[]>(observer => {
              this.socket.on('result', (data) => {
                observer.next(data);
              });
          });
  }

}
