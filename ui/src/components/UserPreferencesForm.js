import React, {Component} from 'react';
import {Form, Button, Card} from 'react-bootstrap'

const UserPreferencesForm  = ({
    onFormSubmit,
    formSubmitText,
    currentEmail,
    currentZipcode,
    currentDistance,
}) => {
    const [validated, setValidated] = React.useState(false);
    const [email, setEmail] = React.useState(currentEmail || '')
    const [zipcode, setZipcode] = React.useState(currentZipcode || '')
    const [distance, setDistance] = React.useState(currentDistance || 5)

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

    return (
        <Card className="baseForm">
            <Card.Body>
                <Form validated={validated} onSubmit={handleSubmit}>
                    <Form.Group controlId="formEmail">
                        <Form.Label>Email address</Form.Label>
                        <Form.Control
                            type="email"
                            placeholder="Enter email"
                            required
                            value={email}
                            readOnly={currentEmail != null}
                            onChange={e => setEmail(e.target.value)}
                        />
                        <Form.Control.Feedback type="invalid">
                            Please provide a valid email
                        </Form.Control.Feedback>
                    </Form.Group>

                    <Form.Group controlId="formDistance">
                        <Form.Label>Get notified of open appointments within</Form.Label>
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
                            onChange={e => setZipcode(e.target.value)}
                        />
                        <Form.Control.Feedback type="invalid">
                            Please provide a valid zipcode
                        </Form.Control.Feedback>
                    </Form.Group>

                    <Button
                        variant="primary"
                        type="submit"
                    >
                        {formSubmitText}
                    </Button>
                </Form>
            </Card.Body>
        </Card>
    );
}

export default UserPreferencesForm;