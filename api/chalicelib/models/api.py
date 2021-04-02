from pydantic import BaseModel, EmailStr, validator
import zipcodes


class UserSchema(BaseModel):
    email: EmailStr
    zipcode: str
    distance: int

    @validator('zipcode')
    def valid_zipcode(cls, zipcode: str) -> str:
        """
        Validates that the zipcode is valid
        """
        if not zipcodes.is_real(zipcode):
            raise ValueError('Invalid zipcode')
        return zipcode

    @validator('distance')
    def valid_distance(cls, distance: int) -> int:
        if distance not in (5, 10, 25, 50, 100):
            raise ValueError('Invalid distance')
        return distance
