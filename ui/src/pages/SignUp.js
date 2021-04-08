import React, {Component} from 'react';
import {Jumbotron, Spinner} from 'react-bootstrap'
import UserPreferencesForm from "../components/UserPreferencesForm";
import api from '../lib/api'

class SignUp extends Component {
    constructor(props) {
        super(props);
        this.state = {
            userCreated: false
        };
    }

    onFormSubmit = async data => {
        try {
            const result = await api.user.post(data);
            if (result.status === 201) {
                this.setState({ userCreated: true })
            }
        } catch (err) {
            console.log('Failed to signup')
        }
    }

    render() {
        const { userCreated } = this.state;

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
                    </div>
                ): (
                    <UserPreferencesForm
                        formSubmitText="Sign Up"
                        onFormSubmit={this.onFormSubmit}
                    />
                )}
            </div>
        );
    }
}

export default SignUp;
