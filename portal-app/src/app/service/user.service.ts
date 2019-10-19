import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {User} from '../model/user.model';

@Injectable({
  providedIn: 'root'
})
export class UserService {

    constructor(private http: HttpClient) { }
    baseUrl = 'http://localhost:8080/user-portal/users';

    createUser(user: User) {
    return this.http.post(this.baseUrl, user);
  }

}
