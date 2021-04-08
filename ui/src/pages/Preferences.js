import React, {Component} from 'react';
import {Jumbotron, Spinner, Button} from 'react-bootstrap'
import UserPreferencesForm from "../components/UserPreferencesForm";
import api from '../lib/api'

class Preferences extends Component {
    constructor(props) {
        super(props);
        this.state = {
            user: null,
            loaded: false,
            error: false,
            unsubscribed: false,
        };
    }

    async componentDidMount() {
        let params = (new URL(window.location.href)).searchParams;
        let token = params.get('token');
        this.setState({ token })

        try {
            const result = await api.user.get(token);
            if (result.status === 200) {
                this.setState({
                    user: {...result.data },
                    loaded: true,
                })
            }
        } catch (err) {
           this.setState({ loaded: true, error: true })
        }
    }

    updatePreferences = async data => {
        const { token } = this.state;
        await api.user.patch(token, data);
    }

    unsubscribe = async () => {
        const { token } = this.state;
        await api.user.delete(token);
        this.setState({unsubscribed: true})
    }

    buildBody = () => {
        const { user, loaded, error, unsubscribed } = this.state;
        if (!loaded) {
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
        } else if (loaded && error) {
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
                    />
                    <div style={{
                        maxWidth: 300,
                        margin: 'auto',
                        paddingTop: 40,
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
