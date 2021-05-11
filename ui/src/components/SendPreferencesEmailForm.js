import React from 'react';
import { Form, Button, Card, Alert } from 'react-bootstrap'

const SendPreferencesEmailForm = ({
    onFormSubmit,
    formSubmitText,
    currentEmail,
    loading,
    showErrorAlert,
    showSuccessAlert
}) => {
    const [validated, setValidated] = React.useState(false);
    const [email, setEmail] = React.useState(currentEmail || '')
    const [errors, setErrors] = React.useState({});

    const handleSubmit = event => {
        const form = event.currentTarget;
        if (form.checkValidity() === false) {
            event.preventDefault();
            event.stopPropagation();
        } else {
            event.preventDefault();
            event.stopPropagation();
            onFormSubmit({
                email
            });
        }
    }


    const validateEmail = email => {
        const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }

    const formValid = () => {
        return email.length > 1 && errors.email !== true
    }

    return (
        <Card className="baseForm">
            <Card.Body>
                <Form validated={validated} onSubmit={handleSubmit}>
                    <Form.Group controlId="formEmail">
                        <Form.Label>Send update notification preferences email to</Form.Label>
                        <Form.Control
                            type="email"
                            placeholder="Enter email"
                            required
                            value={email}
                            readOnly={currentEmail != null}
                            onChange={e => {
                                setEmail(e.target.value);
                                setErrors({ ...errors, email: !validateEmail(e.target.value) });
                            }}
                            isInvalid={!!errors.email}
                        />
                        <Form.Control.Feedback type="invalid">
                            Please provide a valid email
                        </Form.Control.Feedback>
                    </Form.Group>

                    <Button
                        variant="primary"
                        type="submit"
                        disabled={!formValid() || loading}
                    >
                        {formSubmitText}
                    </Button>
                </Form>
            </Card.Body>

            <Card.Body>
                <Alert show={showSuccessAlert} variant="success">
                    <Alert.Heading>
                        Success
                        </Alert.Heading>
                    <p>Email sent!</p>
                </Alert>
                <Alert show={showErrorAlert} variant="danger">
                    <Alert.Heading>
                        Error
                        </Alert.Heading>
                    <p>There was a problem sending the email to the address provided. Have you submitted the sign up form with this address?</p>
                </Alert>
            </Card.Body>
        </Card>
    );
}

export default SendPreferencesEmailForm;