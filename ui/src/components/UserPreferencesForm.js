import React from 'react';
import {Form, Button, Card} from 'react-bootstrap'

const UserPreferencesForm  = ({
    onFormSubmit,
    formSubmitText,
    currentEmail,
    currentZipcode,
    currentDistance,
    loading,
}) => {
    const [validated, setValidated] = React.useState(false);
    const [email, setEmail] = React.useState(currentEmail || '')
    const [zipcode, setZipcode] = React.useState(currentZipcode || '')
    const [distance, setDistance] = React.useState(currentDistance || 10)
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
                email,
                zipcode,
                distance,
            });
        }
    }

    const validateZipcode = zipcode => {
        const re = /(^\d{5}$)/;
        return re.test(String(zipcode).toLowerCase());
    }

    const validateEmail = email => {
        const re = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }

    const formValid = () => {
        return email.length > 1 && zipcode.length > 1 && errors.email !== true && errors.zipcode !== true
    }

    return (
        <Card className="baseForm">
            <Card.Body>
                <Form validated={validated} onSubmit={handleSubmit}>
                    <Form.Group controlId="formEmail">
                        <Form.Label>Send email notifications to</Form.Label>
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

                    <Form.Group controlId="formDistance">
                        <Form.Label>When there are available appointments within</Form.Label>
                        <Form.Control
                            as="select"
                            required
                            value={distance}
                            onChange={e => setDistance(e.target.value)}
                        >
                            <option value={5}>5 miles</option>
                            <option value={10}>10 miles</option>
                            <option value={25}>25 miles</option>
                            <option value={50}>50 miles</option>
                        </Form.Control>
                    </Form.Group>

                    <Form.Group controlId="formZipcode">
                        <Form.Label>Of</Form.Label>
                        <Form.Control
                            type="text"
                            placeholder="Enter a 5 digit zipcode"
                            required
                            value={zipcode}
                            onChange={e => {
                                setZipcode(e.target.value);
                                setErrors({ ...errors, zipcode: !validateZipcode(e.target.value) });
                            }}
                            isInvalid={!!errors.zipcode}
                        />
                        <Form.Control.Feedback type="invalid">
                            Please provide a valid 5 digit zipcode
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
        </Card>
    );
}

export default UserPreferencesForm;