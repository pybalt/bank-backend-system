# This is a custom command. You use it through manage.py this way:
"py manage.py fill-data"
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker
import pycountry
import geonamescache
from address.models import (Country, State, City, Address)
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
    
class RandomCountry:
    
    def __init__(self, *args, **kwargs):
        self._number_of_countries = Country.objects.count() 
        self.country_code = random.choice(list(countries))
        self.country_name = countries[f"{self.country_code}"]["name"]
        self.country_states:list = list(pycountry.subdivisions.get(country_code = self.country_code))
        print(f"{[self.country_code, self.country_name]}, number of states: {len(self.country_states)}")
        Country(country_name = self.country_name, code = self.country_code).save()

    
class RandomState:
    
    def __init__(self, *args, **kwargs):
        self.country:object = RandomCountry()
        self._number_of_states = State.objects.count()
        self.state_info:dict = random.choice(self.country.country_states)
        print(self.state_info)
        self.state_name = self.state_info.name
        self.state_code = self.state_info.code
        State(state_name = self.state_name, code = self.state_code).save()
        print(self.state_name, self.state_code)

def city_filter(countrycode):
    return [ i for i in filter(lambda x: cities[x]["countrycode"] == countrycode, cities) ]

class RandomCity(RandomState):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._number_of_cities = City.objects.count()
        self._city___id:str = random.choice([i for i in city_filter(self.country.country_code)])
        self.city_name:str = cities[self._city___id]["name"]
        print(self.city_name)
        City(city_name = self.city_name).save()



class RandomAddress(RandomCity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._street = RandomStreet()
        self.address_name = self._street.street_name 
        self.address_number = self._street.street_number
        
        self._countries_pks : list = Country.objects.filter(code = self.country.country_code).values_list('pk', flat=True)
        print("countries pk:    ", self._countries_pks)
        self._random_pk : int = random.choice(self._countries_pks)
        self.address_country : object = Country.objects.filter(pk = self._random_pk).first()
        
        self._states_pks : list = State.objects.filter(code = self.state_code).values_list('pk', flat=True)
        print("states pks:  ", self._states_pks)
        self._random_pk : int = random.choice(self._states_pks)
        self.address_state : object = State.objects.filter(pk = self._random_pk).first()
        
        self._cities_pks : list = City.objects.filter(city_name = self.city_name).values_list('pk', flat=True)
        print("cities pks   ", self._cities_pks)
        self._random_pk : int = random.choice(self._cities_pks)
        self.address_city : object = City.objects.filter(pk = self._random_pk).first()
        


class ModelDB:
    "This class has a method that creates model objects. "
    @staticmethod
    def address() -> object:
        address = RandomAddress()
        return Address(address_name = address.address_name,
                       address_number = address.address_number,
                       address_city = address.address_city,
                       address_country = address.address_country,
                       address_state = address.address_state )
    @staticmethod
    def user() -> object:
        return User(username = f"{fake.simple_profile()['username']}", 
                    password = f"{fake.password(length = 50, special_chars = True, digits = True)}")


class Command(BaseCommand):
    
    help = "This command is to fill the database with dummy data. Just for testing purposes."

    
    def handle(self, *args, **kwargs):
        
        number_of_fields = int(input("How many fields do you want to generate?  \n  --> "))
        
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
            except IndexError:
                "Just a Country with no subdivissions."
                continue
            try:
                ModelDB.user().save()
            except IntegrityError:
                "It seems this user already exists."
            new_fields += 1