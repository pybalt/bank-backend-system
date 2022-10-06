# This is a custom command. You use it through manage.py this way:
"py manage.py fill-data"
from types import NoneType
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker
import pycountry
import geonamescache
from address.models import (Country, State, City, Address)
from branch.models import Branch
import random
from django.db.utils import IntegrityError
gc = geonamescache.GeonamesCache()
countries = gc.get_countries()
cities = gc.get_cities()
fake = Faker()


class IGenerated():
    def choose_random(self) -> dict:
        raise NotImplementedError #  I must refactor. Users doesn't get choosed.

    def does_exists(self) -> bool:
        raise NotImplementedError

    def insert(self) -> bool:
        print(self.insert)
        if not self.does_exists():
            self.instance.save()

    def model_object(self) -> object:
        raise NotImplementedError


class ISubdivissions(IGenerated):
    def has_subdivissions() -> bool:
        raise NotImplementedError


class GeneratedCountry(ISubdivissions):

    def choose_random(self) -> str:
        print(self.choose_random)
        return random.choice(list(countries))

    def does_exists(self) -> bool:
        print(self.does_exists)
        return Country.objects.filter(code=self.country_code).exists()

    def has_subdivissions(self) -> bool:
        print(self.has_subdivissions)
        return bool(pycountry.subdivisions.get(country_code=self.country_code))

    @staticmethod
    def model_object(country_code) -> object:
        return Country.objects.get(code=country_code)

    def __init__(self) -> None:
        self.country_code: str = self.choose_random()
        self.country_name: str = countries[f"{self.country_code}"]["name"]
        if not self.has_subdivissions():
            return self.__init__()
        self.instance: object = Country(code=self.country_code,
                                        country_name=self.country_name)


class GeneratedState(ISubdivissions):

    def choose_random(self, country_code: str) -> str:
        print(self.choose_random)
        subdivissions = pycountry.subdivisions.get(country_code=country_code)
        return random.choice(list(subdivissions))

    def does_exists(self) -> bool:
        print(self.does_exists)
        return State.objects.filter(code=self.state_code).exists()

    def has_subdivissions(self) -> bool:
        print(self.has_subdivissions)
        # This is completely random. I must refactor.
        return NotImplementedError

    @staticmethod
    def model_object(state_code) -> object:
        return State.objects.get(code=state_code)

    def __init__(self, country_code) -> None:
        self.__state = self.choose_random(country_code)
        self.state_code = self.__state.code
        self.state_name = self.__state.name
        self.instance = State(code=self.state_code,
                              state_name=self.state_name,
                              country=GeneratedCountry.model_object(
                                  country_code
                                  )
                              )


class GeneratedCity(IGenerated):

    def choose_random(self, countrycode: str) -> str(int):
        print(self.choose_random)

        filtered_list = [
            i for i in
            filter(lambda x:
                   cities[x]["countrycode"] == countrycode,
                   cities)
            ]
        if filtered_list:
            return random.choice(filtered_list)
        else:
            return countries[f"{countrycode}"]["name"]

    def does_exists(self) -> bool:
        print(self.does_exists)
        return City.objects.filter(state_id=self.instance.state,
                                   city_name=self.instance.city_name).exists()

    @staticmethod
    def model_object(city_name, state_code) -> object:
        return City.objects.filter(city_name=city_name,
                                   state=GeneratedState.model_object(
                                       state_code
                                       )
                                   ).first()

    def __init__(self, countrycode, state_code) -> None:
        self.city_id = self.choose_random(countrycode)
        try:
            self.name = cities[self.city_id]["name"]
        except KeyError:
            self.name = self.city_id
        self.instance = City(city_name=self.name,
                             state=GeneratedState.model_object(
                                  state_code
                                  ))


class RandomStreet:

    def __init__(self, *args, **kwargs):

        self.name = fake.street_name()
        self.number = int(fake.building_number())


class GeneratedAddress(IGenerated):

    def choose_random(self, country_code: str) -> str:
        print(self.choose_random)
        subdivissions = pycountry.subdivisions.get(country_code=country_code)
        return random.choice(list(subdivissions))

    def does_exists(self) -> bool:
        print(self.does_exists)
        return Address.objects.filter(address_name=self.address_name,
                                      address_number=self.address_number,
                                      address_city=self.address_city).exists()

    def has_subdivissions(self) -> bool:
        print(self.has_subdivissions)
        # This is completely random. I must refactor.
        return NotImplementedError

    @staticmethod
    def model_object(name, number, city) -> object:
        return Address.objects.get(address_name=name,
                                   address_number=number,
                                   address_city=city)

    def __init__(self, city, state, *args, **kwargs):

        self.__street = RandomStreet()
        self.address_name = self.__street.name
        self.address_number = self.__street.number
        self.address_city: object = GeneratedCity.model_object(city,
                                                               state)
        self.instance = Address(address_name=self.address_name,
                                address_number=self.address_number,
                                address_city=self.address_city)


class Command(BaseCommand):

    help = "This command is to fill the database with dummy data. Just for testing purposes."

    def handle(self, *args, **kwargs):

        number_of_fields = int(
            input("How many fields do you want to generate?  \n  --> "))
        for _ in range(number_of_fields):
            country = GeneratedCountry()
            print(country.country_name, country.country_code)
            country.insert()
            state = GeneratedState(country.country_code)
            print(state.state_code, state.state_name, state.instance)
            state.insert()
            city = GeneratedCity(country.country_code,
                                 state.state_code)
            city.insert()
            address = GeneratedAddress(city.name, state.state_code)
            address.insert()
