import React, { Component } from 'react';
import { Jumbotron, Spinner, Button } from 'react-bootstrap'
import UserPreferencesForm from "../components/UserPreferencesForm";
import SendPreferencesEmailForm from "../components/SendPreferencesEmailForm"
import api from '../lib/api'

class Preferences extends Component {
    constructor(props) {
        super(props);
        this.state = {
            user: null,
            loading: true,
            error: false,
            unsubscribed: false,
            showSuccessAlert: false,
            showErrorAlert: false
        };
    }

    async componentDidMount() {
        let params = (new URL(window.location.href)).searchParams;
        let token = params.get('token');
        this.setState({ token })
        if (token) {
            try {
                const result = await api.user.get(token);
                if (result.status === 200) {
                    this.setState({
                        user: { ...result.data },
                        loading: false,
                    })
                }
            } catch (err) {
                this.setState({ loading: false, error: true })
            }
        } else {
            this.setState({ loading: false })
        }
    }

    updatePreferences = async data => {
        const { token } = this.state;
        await api.user.patch(token, data);
    }

    sendPreferencesEmail = async data => {
        const send_email_result = await api.user.manage_preferences.post(data);
        if (send_email_result.status == 204) {
            this.setState({ showSuccessAlert: true })
        } else {
            this.setState({ showErrorAlert: true })
        }
    }

    unsubscribe = async () => {
        const { token } = this.state;
        await api.user.delete(token);
        this.setState({ unsubscribed: true })
    }

    buildBody = () => {
        const { user, loading, error, unsubscribed, token, showSuccessAlert, showErrorAlert } = this.state;
        if (loading) {
            return (
                <div style={{
                    marginRight: 'auto',
                    marginLeft: 'auto',
                    backgroundColor: 'white',
                    textAlign: 'center',
                }}>
                    <Spinner animation="border" role="status" />
                    <p>Loading your notification preferences...</p>
                </div>
            );
        } else if (!loading && error) {
            return (
                <div style={{
                    marginRight: 'auto',
                    marginLeft: 'auto',
                    backgroundColor: 'white',
                    textAlign: 'center',
                }}>
                    <p>Looks like we were unable to load your notification preferences</p>
                </div>
            );
        } else if (!loading && !token) {
            return (
                <div style={{

                }}>
                    <SendPreferencesEmailForm
                        formSubmitText="SendPreferencesEmail"
                        onFormSubmit={this.sendPreferencesEmail}
                        loading={loading}
                        showSuccessAlert={showSuccessAlert}
                        showErrorAlert={showErrorAlert}
                    ></SendPreferencesEmailForm>
                </div>
            )
        } else if (unsubscribed) {
            return (
                <div style={{
                    marginRight: 'auto',
                    marginLeft: 'auto',
                    backgroundColor: 'white',
                    textAlign: 'center',
                }}>
                    <p>You have been successfully unsubscribed from future emails</p>
                </div>
            );
        } else {
            return (
                <div>
                    <UserPreferencesForm
                        formSubmitText="Update"
                        onFormSubmit={this.updatePreferences}
                        currentEmail={user.email}
                        currentDistance={user.distance}
                        currentZipcode={user.zipcode}
                        loading={loading}
                    />
                    <div style={{
                        maxWidth: 300,
                        margin: 'auto',
                        paddingTop: 40,
                        paddingBottom: 40,
                    }}>
                        <Button
                            variant="danger"
                            size="lg"
                            block
                            onClick={this.unsubscribe}
                        >
                            Unsubscribe
                        </Button>
                    </div>
                </div>
            );
        }
    }

    render() {
        return (
            <div>
                <Jumbotron style={{
                    marginRight: 'auto',
                    marginLeft: 'auto',
                    maxWidth: 1000,
                    backgroundColor: 'white',
                    textAlign: 'center',
                }}>
                    <h2>Update your notification preferences</h2>
                </Jumbotron>
                {this.buildBody()}
            </div>
        );
    }
}

export default Preferences;
