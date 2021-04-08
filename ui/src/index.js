import React from 'react';
import ReactDOM from 'react-dom';
import {BrowserRouter, Route, Switch} from 'react-router-dom';
import './index.css';
import SignUp from './pages/SignUp'
import Preferences from "./pages/Preferences";
import 'bootstrap/dist/css/bootstrap.min.css';


const router = (
    <BrowserRouter>
        <Switch>
            <Route exact path="/" component={SignUp}/>
            <Route exact path="/preferences" component={Preferences}/>
        </Switch>
    </BrowserRouter>
);

ReactDOM.render(
  <React.StrictMode>
      {router}
  </React.StrictMode>,
  document.getElementById('root')
);

