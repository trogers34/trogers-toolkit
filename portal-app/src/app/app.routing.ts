import { RouterModule, Routes } from '@angular/router';
import {AddUserComponent} from './add-user/add-user.component';
import {AppComponent} from './app.component';

const routes: Routes = [
  { path: 'add-user', component: AddUserComponent },
   { path: '', component: AppComponent }
];

export const routing = RouterModule.forRoot(routes);
