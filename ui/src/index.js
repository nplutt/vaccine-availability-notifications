import React from 'react';
import ReactDOM from 'react-dom';
import {BrowserRouter, Route, Switch} from 'react-router-dom';
import './index.css';
import SignUp from './pages/SignUp'
import Preferences from "./pages/Preferences";
import 'bootstrap/dist/css/bootstrap.min.css';
import {Navbar, Nav} from 'react-bootstrap';



const navbar = (
    <Navbar collapseOnSelect expand="lg" bg="dark" variant="dark">
        <Navbar.Brand href="/">Covid Vaccine Notifications</Navbar.Brand>
        <Navbar.Toggle aria-controls="responsive-navbar-nav"/>
        <Navbar.Collapse id="responsive-navbar-nav">
            <Nav className="mr-auto">
                <Nav.Link href="/">Sign Up</Nav.Link>
                <Nav.Link href="/preferences">Preferences</Nav.Link>
            </Nav>
        </Navbar.Collapse>
    </Navbar>
);

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
      {navbar}
      {router}
  </React.StrictMode>,
  document.getElementById('root')
);

