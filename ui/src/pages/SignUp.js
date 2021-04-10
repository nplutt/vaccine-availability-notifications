import React, {Component} from 'react';
import {Jumbotron} from 'react-bootstrap'
import UserPreferencesForm from "../components/UserPreferencesForm";
import api from '../lib/api'

class SignUp extends Component {
    constructor(props) {
        super(props);
        this.state = {
            userCreated: false,
            loading: false,
            error: false,
        };
    }

    onFormSubmit = async data => {
        this.setState({ loading: true });
        const result = await api.user.post(data);
        this.setState({ loading: false });
        if (result.status === 201) {
            this.setState({ userCreated: true })
        } else {
            this.setState({ error: true });
        }
    }



    render() {
        const { userCreated, loading } = this.state;

        return (
            <div style={{ marginBottom: 100 }}>
                <Jumbotron style={{
                    marginRight: 'auto',
                    marginLeft: 'auto',
                    maxWidth: 1000,
                    backgroundColor: 'white',
                    textAlign: 'center',
                }}>
                    <h2>Get email notifications when COVID-19 vaccination appointments open up near you!</h2>
                </Jumbotron>
                {userCreated ? (
                    <div style={{
                        marginRight: 'auto',
                        marginLeft: 'auto',
                        backgroundColor: 'white',
                        textAlign: 'center',
                    }}>
                        <p>Thanks for the info! You will now receive email notifications when locations near you have new vaccination appointments available.</p>
                        <p>If you don't recieve a welcome email, please check your <b>junk or spam</b> folders.</p>
                    </div>
                ) : (
                    <UserPreferencesForm
                        formSubmitText="Sign Up"
                        onFormSubmit={this.onFormSubmit}
                        loading={loading}
                    />
                )}
                <Jumbotron style={{
                    marginRight: 'auto',
                    marginLeft: 'auto',
                    maxWidth: 1000,
                    backgroundColor: 'white',
                    textAlign: 'left',
                    paddingBottom: 0,
                }}>
                    <h2>About</h2>
                    <div>
                        Finding a vaccination appointment can be very frustrating and time
                        consuming, hopefully this tool can help make that easier! Feel free to
                        email any questions to <a href="mailto:nplutt.vaccine@gmail.com">nplutt.vaccine@gmail.com</a> and
                        report issues to <a href="https://github.com/nplutt/vaccine-availability-notifications/issues">Github</a>.
                    </div>
                    <br/>
                    <div>
                        This website is inspired by and made possible thanks to <a href="https://vaccinespotter.org">Vaccine Spotter</a> and the data that they provide via their API!
                        Head over to their site for the most up to date vaccine appointment availability.
                    </div>
                    <br/>
                    <div>
                        If you're an engineer and would like to help out, the project is open sourced
                        on <a href="https://github.com/nplutt/vaccine-availability-notifications">Github</a>.
                    </div>
                </Jumbotron>
                <Jumbotron style={{
                    marginRight: 'auto',
                    marginLeft: 'auto',
                    maxWidth: 1000,
                    backgroundColor: 'white',
                    textAlign: 'left',
                    paddingTop: 0,
                }}>
                    <h2>Common Questions</h2>
                    <p>
                        <div><b>Q:</b> Not receiving emails?</div>
                        <div>
                            <b>A:</b> Check your spam folder, if there aren't any emails in there then try widening your search radius.
                        </div>
                    </p>
                    <p>
                        <div><b>Q:</b> Why aren't the appointments that I see in the email available?</div>
                        <div>
                            <b>A:</b> There is a 2 to 5 minute delay between when appointments become available and when we can
                            get the emails sent to you. For the most up to date vaccine availability information, go
                            to <a href="https://vaccinespotter.org">Vaccine Spotter</a>.
                        </div>
                    </p>
                </Jumbotron>
            </div>
        );
    }
}

export default SignUp;
