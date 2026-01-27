from faker import Faker

fake = Faker()


class Payloads:

    @staticmethod
    def create_user() -> dict:
        return {
            "email": fake.unique.email(),
            "firstName": fake.first_name(),
            "lastName": fake.last_name(),
            "dateOfBirth": fake.date_of_birth().isoformat(),
            "phone": fake.msisdn()[:14],
        }

    @staticmethod
    def update_user() -> dict:
        return {
            "firstName": fake.first_name(),
            "lastName": fake.last_name(),
            "phone": fake.msisdn()[:14],
        }
