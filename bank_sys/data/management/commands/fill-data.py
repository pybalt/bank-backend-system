# This is a custom command. You use it through manage.py this way:
"py manage.py fill-data"
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker
import pycountry
import geonamescache
from address.models import (Country, State, City, Address)
from employee.models import Employee
from customer.models import Customer, CustomerType
from branch.models import Branch
import random
from django.db.utils import IntegrityError
gc = geonamescache.GeonamesCache()
countries = gc.get_countries()
cities = gc.get_cities()
fake = Faker()


class RandomStreet:

    def __init__(self, *args, **kwargs):
        self.street_name = fake.street_name()
        self.street_number = int(fake.building_number())


def list_subdivisions(country_code):
    return list(pycountry.subdivisions.get(country_code=country_code))


class RandomCountry:

    def __init__(self, *args, **kwargs):
        self._number_of_countries = Country.objects.count()
        self.country_code = random.choice(list(countries))
        self.country_name = countries[f"{self.country_code}"]["name"]
        self.country_states: list = list_subdivisions(self.country_code)
        Country(country_name=self.country_name, code=self.country_code).save()


class RandomState:

    def __init__(self, *args, **kwargs):
        self.country: object = RandomCountry()
        self._number_of_states = State.objects.count()
        self.state_info: dict = random.choice(self.country.country_states)
        self.state_name = self.state_info.name
        self.state_code = self.state_info.code
        State(state_name=self.state_name, code=self.state_code).save()


def city_filter(countrycode):

    def countrycode_filter(x, countrycode):
        return cities[x]["countrycode"] == countrycode

    return [i for i in filter(countrycode_filter(countrycode), cities)]


class RandomCity(RandomState):

    def __id_chooser(self) -> str:
        countrycode = self.country.country_code
        return random.choice([i for i in city_filter(countrycode)])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__city_id: str = RandomCity.__id_chooser(self)
        self.city_name: str = cities[self.__city_id]["name"]
        City(city_name=self.city_name).save()


class RandomAddress(RandomCity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__street = RandomStreet()
        self.address_name = self.__street.street_name
        self.address_number = self.__street.street_number
        self.__countries_pks: list = Country.objects.filter(
            code=self.country.country_code
            ).values_list('pk', flat=True)
        print("countries pk:    ", self.__countries_pks)
        self.__random_pk: int = random.choice(self.__countries_pks)
        self.address_country: object = Country.objects.filter(
            pk=self.__random_pk).first()
        self.__states_pks: list = State.objects.filter(
            code=self.state_code).values_list('pk', flat=True)
        print("states pks:  ", self.__states_pks)
        self.__random_pk: int = random.choice(self.__states_pks)
        self.address_state: object = State.objects.filter(
            pk=self.__random_pk).first()
        self.__cities_pks: list = City.objects.filter(
            city_name=self.city_name).values_list('pk', flat=True)
        print("cities pks   ", self.__cities_pks)
        self.__random_pk: int = random.choice(self.__cities_pks)
        self.address_city: object = City.objects.filter(
            pk=self.__random_pk).first()


def choose_type() -> object:
    db_number_of_instances: int = CustomerType.objects.count()
    db_instances: list[str] = ['BLACK', 'GOLD', 'CLASSIC']
    if db_number_of_instances != len(db_instances):
        for i in db_instances:
            instance = CustomerType(customer_type=i)
            try:
                instance.save()
            except IntegrityError:
                continue
    choice = random.choice(['BLACK', 'GOLD', 'CLASSIC'])
    instance: object = CustomerType.objects.filter(customer_type=choice).first
    return instance


class ModelDB:
    "This class has static methods that creates model instances. "
    @staticmethod
    def address() -> object:
        address = RandomAddress()
        return Address(address_name=address.address_name,
                       address_number=address.address_number,
                       address_city=address.address_city,
                       address_country=address.address_country,
                       address_state=address.address_state)

    @staticmethod
    def user() -> object:
        password = fake.password(length=50, special_chars=True, digits=True)
        user = {"username": f"{fake.simple_profile()['username']}",
                "password": f"{password}"}
        return User(username=user["username"],
                    password=user["password"])

    @staticmethod
    def branch(address_instance: object) -> object:
        return Branch(branch_number=random.randint(1, 9999),
                      branch_name=fake.color_name(),
                      branch_address=address_instance)

    @staticmethod
    def employee(branch_instance: object,
                 address_instance: object,
                 user_instance: object) -> object:
        return Employee(user=user_instance,
                        employee_name=fake.first_name(),
                        employee_surname=fake.last_name(),
                        employee_hire_date=fake.date(),
                        employee_dni=fake.random() * 10000000,
                        branch=branch_instance,
                        address=address_instance
                        )

    def customer(branch_instance: object,
                 address_instance: object,
                 user_instance: object) -> object:
        return Customer(user=user_instance,
                        customer_name=fake.first_name(),
                        customer_surname=fake.last_name(),
                        customer_dni=fake.random() * 10000000,
                        customer_type=choose_type(),
                        customer_dob=fake.date(),
                        branch=branch_instance,
                        address=address_instance
                        )


class Command(BaseCommand):

    help = """This command is to fill the database with dummy data.
    Just for testing purposes."""

    def handle(self, *args, **kwargs):

        number_of_fields = int(input(
            "How many fields do you want to generate?\n  --> "))

        _integrity_errors = 0
        new_fields = 0
        while True:
            if new_fields == number_of_fields:
                break
            if _integrity_errors > 6:
                print("You can't add more fields.")
                break
            try:
                ModelDB.address().save()
            except IntegrityError:
                _integrity_errors += 1
                continue
            except IndexError:
                "Just a Country with no subdivissions."
                continue
            except TypeError:
                """A Country with no subdivissions
                can also throw an TypeError: NoneType."""
                continue

            "Branchs"
            desired_proportion = 8  # 1 of 8 instances must be a branch
            number_of_addresses = Address.objects.count()
            number_of_branchs = int("%.0f" % (
                number_of_addresses/desired_proportion
                ))

            if number_of_branchs > 0:
                for _ in range(number_of_branchs):
                    pk_addresses: list = Address.objects.all(
                        ).values_list('id')
                    pk = random.choice(pk_addresses)
                    try:
                        ModelDB.branch(
                            Address.objects.filter(pk=pk[0]).first()).save()
                    except IntegrityError:
                        "It seems this address has already been asigned."
                        continue
            "Each branch has 6 employees and 32 customers"
            branch_number = Branch.objects.count()

            for i in range(0, branch_number):
                id = i+1

                branch = Branch.objects.filter(pk=id).first()
                number_of_employees = Employee.objects.filter(
                    branch=branch).count()
                "employees"
                if number_of_employees < 6:
                    counter = 0
                    while True:
                        try:
                            address = ModelDB.address()
                            address.save()
                            user = ModelDB.user()
                            user.save()
                            ModelDB.employee(branch, address, user).save()
                            counter += 1
                            if counter == (6 - number_of_employees):
                                break
                            else:
                                continue
                        except IntegrityError:
                            continue
                "customers"
                number_of_customers = Customer.objects.filter(branch=branch)
                if number_of_customers < 32:
                    counter = 0
                    while True:
                        try:
                            address = ModelDB.address()
                            address.save()
                            user = ModelDB.user()
                            user.save()
                            ModelDB.customer(branch, address, user).save()
                            counter += 1
                            if counter == (32 - number_of_customers):
                                break
                            else:
                                continue
                        except IntegrityError:
                            continue

            try:
                ModelDB.user().save()
            except IntegrityError:
                "It seems this user already exists."

            new_fields += 1
