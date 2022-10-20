# This is a custom command. You use it through manage.py this way:
"py manage.py fill-data"
import heartrate
from uuid import uuid4
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker
import pycountry
import geonamescache
from address.models import (Country, State, City, Address)
from account.models import Account, TypeAccount
from card.models import CardProvider, TypeCard, Card
from branch.models import Branch
from customer.models import Customer, CustomerType
from employee.models import Employee
from movement.models import Movement
from loan.models import Loan
import random
gc = geonamescache.GeonamesCache()
countries = gc.get_countries()
cities = gc.get_cities()
fake = Faker()


class IGenerated():

    def does_exists(self) -> bool:
        raise NotImplementedError

    def insert(self) -> None:
        print(self.insert)
        if not self.does_exists():
            self.instance.save()
    @staticmethod
    def model_object() -> object:
        raise NotImplementedError


class IGeneratedFromList(IGenerated):

    def choose_random(self):
        raise NotImplementedError


class ISubdivissions():
    def has_subdivissions() -> bool:
        raise NotImplementedError


class GeneratedCountry(ISubdivissions, IGeneratedFromList):

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


class GeneratedState(IGeneratedFromList, ISubdivissions):

    def has_subdivissions(self, country_code) -> bool:
        print(self.has_subdivissions)
        return bool(pycountry.subdivisions.get(country_code=country_code))

    def choose_random(self, country_code: str) -> str:
        print(self.choose_random)
        if self.has_subdivissions(country_code):
            subdivissions = pycountry.subdivisions.get(
                country_code=country_code
                )
            return random.choice(list(subdivissions))

    def does_exists(self) -> bool:
        print(self.does_exists)
        return State.objects.filter(code=self.state_code).exists()

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


class GeneratedCity(IGeneratedFromList):

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

    def does_exists(self) -> bool:
        print(self.does_exists)
        return Address.objects.filter(address_name=self.address_name,
                                      address_number=self.address_number,
                                      address_city=self.address_city).exists()

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


class GeneratedBranch(IGenerated):

    def does_exists(self) -> bool:
        print(self.does_exists)
        return Branch.objects.filter(branch_number=self.branch_number,
                                     branch_name=self.branch_name,
                                     branch_address=self.address).exists()

    @staticmethod
    def model_object(number, name, address) -> object:
        print(GeneratedBranch.model_object)
        return Branch.objects.get(branch_number=number,
                                  branch_name=name,
                                  branch_address=address)

    def check_integrity(self) -> bool:
        print(self.model_object)
        number = Branch.objects.filter(
            branch_number=self.branch_number
            ).exists()
        name = Branch.objects.filter(branch_name=self.branch_name).exists()
        if not (number or name):
            return True

        return False

    def __init__(self) -> None:
        print(self.__init__)
        self.__address = give_me_an_address()
        self.branch_number = random.randint(1, 9999)
        self.branch_name = fake.color_name()
        self.address = GeneratedAddress.model_object(self.__address.address_name,
                                                     self.__address.address_number,
                                                     self.__address.address_city)
        if not self.check_integrity():
            self.branch_number = random.randint(1, 20000)
            self.branch_name = fake.street_name()
        self.instance = Branch(branch_number=self.branch_number,
                               branch_name=self.branch_name,
                               branch_address=self.address)


class GeneratedUser(IGenerated):
    def does_exists(self) -> bool:
        print(self.does_exists)
        return User.objects.filter(username=self.username).exists()

    @staticmethod
    def model_object(username) -> object:
        print(GeneratedUser.model_object)
        return User.objects.get(username=username)

    def __init__(self) -> None:
        self.username = fake.simple_profile()['username']
        self.password = fake.password(length=50,
                                      special_chars=True,
                                      digits=True)
        self.instance = User(username=self.username, password=self.password)


class GeneratedCustomer(IGenerated):
    class GeneratedType(IGeneratedFromList):
        def does_exists(self) -> bool:
            return CustomerType.objects.filter(
                customer_type=self.customer_type
                ).exists()

        @staticmethod
        def model_object(customer_type) -> object:
            return CustomerType.objects.get(customer_type=customer_type)

        def choose_random(self):
            __types = ['BLACK', 'GOLD', 'CLASSIC']
            return random.choice(__types)

        def __init__(self) -> None:
            self.customer_type = self.choose_random()
            self.instance = CustomerType(customer_type=self.customer_type)
            self.instance = self.insert()
            self.instance = GeneratedCustomer.GeneratedType.model_object(
                self.customer_type
                )

    def does_exists(self) -> bool:
        return Customer.objects.filter(user=self.user)

    @staticmethod
    def model_object(user) -> object:
        return Customer.objects.get(user=user)

    def __init__(self, branch) -> None:
        self.user = give_me_an_user()
        self.name = fake.first_name()
        self.surname = fake.last_name()
        self.dni = random.random() * 10000000
        self.type = GeneratedCustomer.GeneratedType().instance
        self.dob = fake.date()
        self.branch = branch
        self.__address = give_me_an_address()
        self.address = GeneratedAddress.model_object(self.__address.address_name,
                                                     self.__address.address_number,
                                                     self.__address.address_city)
        self.instance = Customer(
            user=self.user,
            customer_name=self.name,
            customer_surname=self.surname,
            customer_dni=self.dni,
            customer_type=self.type,
            customer_dob=self.dob,
            branch=self.branch,
            address=self.address
        )


class GeneratedEmployee(IGenerated):
    def does_exists(self) -> bool:
        print(self.does_exists)
        return Employee.objects.filter(employee_dni=self.dni).exists()

    @staticmethod
    def model_object(user) -> object:
        print(GeneratedEmployee.model_object)
        return Employee.objects.get(user=user)

    def __init__(self, branch) -> None:
        print(GeneratedEmployee.__init__)
        self.__address = give_me_an_address()
        self.user = give_me_an_user()
        self.name = fake.first_name()
        self.surname = fake.last_name()
        self.hire_date = fake.date()
        self.dni = random.random() * 10000000
        if self.does_exists():
            self.__init__(branch, self.__address)
        self.branch = branch
        self.address = GeneratedAddress.model_object(self.__address.address_name,
                                                     self.__address.address_number,
                                                     self.__address.address_city)
        self.instance = Employee(user=self.user,
                                 employee_name=self.name,
                                 employee_surname=self.surname,
                                 employee_hire_date=self.hire_date,
                                 employee_dni=self.dni,
                                 branch=self.branch,
                                 address=self.address)


class GeneratedAccount(IGenerated):

    class GeneratedTypeAccount(IGeneratedFromList):
        def does_exists(self) -> bool:
            return TypeAccount.objects.filter(
                code=self.account_type["Code"]
            ).exists()

        def choose_random(self):
            __types = [{
                "Type": "Savings account",
                "Code": "SvnACC"
                        },
                       {
                "Type": "Current account",
                "Code": "CntACC"
                        },
                       {
                "Type": "Salary account",
                "Code": "SryACC"
                        },
                       {
                "Type": "Checking account",
                "Code": "CkgACC"
                       }]
            return random.choice(__types)

        @staticmethod
        def model_object(code) -> object:
            return TypeAccount.objects.filter(
                code=code
            ).first()

        def __init__(self) -> None:
            self.account_type = self.choose_random()
            self.instance = TypeAccount(
                type=self.account_type["Type"],
                code=self.account_type["Code"])
            self.instance = self.insert()
            self.instance = GeneratedAccount.GeneratedTypeAccount.model_object(
                self.account_type["Code"]
            )

    def does_exists(self) -> bool:
        return Account.objects.filter(
            customer=self.customer,
            type=self.type,
            balance=self.balance
        ).exists()

    @staticmethod
    def model_object(iban) -> object:
        return Account.objects.filter(iban=iban).first()

    def __init__(self, user) -> None:
        self.iban = str(uuid4()).replace("-", "")[:12]
        self.customer = GeneratedCustomer.model_object(user=user)
        self.balance = random.random() * random.randint(500, 9000)
        self.type = GeneratedAccount.GeneratedTypeAccount().instance
        self.instance = Account(
            customer=self.customer,
            balance=self.balance,
            type=self.type,
            iban=self.iban
        )


class GeneratedCard(IGenerated):
    class GeneratedCardProvider(IGenerated):
        def does_exists(self) -> bool:
            return CardProvider.objects.filter(provider=self.provider).exists()
        @staticmethod
        def model_object(provider) -> object:
            return CardProvider.objects.filter(provider=provider).first()
        def __init__(self) -> None:
            self.provider = fake.credit_card_provider()
            self.instance = CardProvider(provider=self.provider)
            self.insert()
            __model_object = GeneratedCard.GeneratedCardProvider.model_object
            self.instance = __model_object(self.provider)
    class GeneratedTypeCard(IGeneratedFromList):
        def choose_random(self):
            __types = ('CREDIT', 'DEBIT')
            return random.choice(__types)
        def does_exists(self) -> bool:
            return TypeCard.objects.filter(type=self.type).exists()
        @staticmethod
        def model_object(type):
            return TypeCard.objects.filter(type=type).first()
        def __init__(self) -> None:
            self.type = self.choose_random()
            self.instance = TypeCard(type=self.type)
            self.insert()
            __model_object = GeneratedCard.GeneratedTypeCard.model_object
            self.instance = __model_object(self.type)
    def does_exists(self) -> bool:
        return Card.objects.filter(account=self.account,
                                   provider=self.provider,
                                   number=self.number).exists()
    @staticmethod
    def model_object(account, provider, number):
        Card.objects.filter(account=account,
                            provider=provider,
                            number=number).first()
    def __init__(self, account) -> None:
        self.account = account
        self.number = fake.credit_card_number()
        self.cvv = fake.credit_card_security_code()
        self.expiry_date = fake.date()
        self.type = self.GeneratedTypeCard().instance
        self.provider = self.GeneratedCardProvider().instance
        self.instance = Card(
            account=self.account,
            number=self.number,
            cvv=self.cvv,
            expiry_date=self.expiry_date,
            type_card=self.type,
            provider=self.provider
        )

class GeneratedMovement(IGenerated):
    def does_exists(self) -> bool:
        return Movement.objects.filter(description=self.description,
                                       recipient=self.recipient,
                                       sender=self.sender,
                                       amount=self.amount).exists()
    
    @staticmethod
    def model_object(description, recipient, sender) -> object:
        return Movement.objects.filter(description=description,
                                       recipient=recipient,
                                       sender=sender).filter()
    
    def __init__(self, recipient, sender) -> None:
        self.amount = random.random() * random.choice((1_000, 10_000))
        self.description = fake.text(30)
        self.date = fake.date()
        self.recipient = recipient
        self.sender = sender
        self.instance = Movement(amount=self.amount,
                                 description=self.description,
                                 date=self.date,
                                 recipient=self.recipient,
                                 sender=self.sender)


class GeneratedLoan(IGenerated):
    def does_exists(self) -> bool:
        return Loan.objects.filter(granter=self.granter,
                                   amount=self.amount,
                                   date=self.date,
                                   account=self.account).exists()
    @staticmethod
    def model_object(obj) -> object:
        return Loan.objects.filter(granter=obj.granter,
                            amount=obj.amount,
                            type=obj.type,
                            date=obj.date,
                            account=obj.account).first()
    def __init__(self, account, granter) -> None:
        self.granter = granter
        self.amount = random.randint(1_000, 15_000)
        "Type undefined because is PERSONAL by default"
        self.date = fake.date()
        self.account = account
        self.instance = Loan(
            granter=self.granter,
            amount=self.amount,
            date=self.date,
            account=self.account
        )

def give_me_an_address() -> object:
    print(give_me_an_address)
    country = GeneratedCountry()
    country.insert()
    state = GeneratedState(country.country_code)
    state.insert()
    city = GeneratedCity(country.country_code,
                         state.state_code)
    city.insert()
    address = GeneratedAddress(city.name, state.state_code)
    address.insert()
    return address

def give_me_an_user() -> object:
    user = GeneratedUser()
    user.insert()
    user = GeneratedUser.model_object(user.username)
    return user

def movement_accounts() -> list:
    print(movement_accounts)
    __range = Account.objects.count()
    __pks_choices = range(1, __range)
    print(__pks_choices,": ", __range)
    accounts = random.choices(__pks_choices, k=2)
    accounts = list(map(
        lambda pk: Account.objects.filter(pk=pk).first(),
        accounts
        ))
    print([i for i in accounts])
    if accounts[0].id == accounts[1].id:
        return movement_accounts()
    return accounts

def bulk_create(cls:object, arr):
    cls.objects.bulk_create(arr, ignore_conflicts=True)


class Command(BaseCommand):

    help = "This command is to fill the database with dummy data. Just for testing purposes."

    def handle(self, *args, **kwargs):
        heartrate.trace(browser=True)
        number_of_fields = int(
            input("How many fields do you want to generate?  \n  --> "))
        bulk_branchs = []
        bulk_employees = []
        bulk_accounts = []
        bulk_customers = []
        bulk_cards = []
        bulk_movements = []
        bulk_loans = []
        for _ in range(number_of_fields):
            "Branch"
            branch = GeneratedBranch()
            bulk_branchs.append(branch.instance)
        
        bulk_create(Branch, bulk_branchs)
        
        bulk_branchs = list(map(lambda x: GeneratedBranch.model_object(
            x.branch_number,
            x.branch_name,
            x.branch_address_id), bulk_branchs))
            
        print(bulk_branchs)

        "employees"
        for _ in range(number_of_fields):
            employee = GeneratedEmployee(random.choice(bulk_branchs))
            bulk_employees.append(employee.instance)

        bulk_create(Employee, bulk_employees)
        bulk_employees = list(map(lambda x: GeneratedEmployee.model_object(x.user), bulk_employees))

        "Customers"
        for _ in range(number_of_fields):
            customer = GeneratedCustomer(random.choice(bulk_branchs))
            bulk_customers.append(customer.instance)

        bulk_create(Customer, bulk_customers)
        bulk_customers = list(map(lambda x: GeneratedCustomer.model_object(x.user), bulk_customers))

        "Accounts"
        for i in bulk_customers:
            account = GeneratedAccount(i.user)
            bulk_accounts.append(account.instance)

        bulk_create(Account, bulk_accounts)
        bulk_accounts = list(map(lambda x: GeneratedAccount.model_object(x.iban), bulk_accounts))

        "Cards"
        for i in bulk_accounts:
            card = GeneratedCard(i)
            bulk_cards.append(card.instance)
        bulk_create(Card, bulk_cards)
        bulk_cards = list(map(lambda x: GeneratedCard.model_object(x.account,
                                                                   x.provider,
                                                                   x.number), bulk_cards))
        "Loans"
        for _ in range(number_of_fields):
            employee = random.choice(bulk_employees)
            account = random.choice(bulk_accounts)
            loan = GeneratedLoan(account, employee)
            bulk_loans.append(loan.instance)
        bulk_create(Loan, bulk_loans)

        for _ in range(number_of_fields):
            "Customer movements"
            accounts = movement_accounts()
            movement = GeneratedMovement(accounts[0], accounts[1])
            bulk_movements.append(movement.instance)
        bulk_create(Movement, bulk_movements)

            # It would be nice if each time we save a loan, a new movement is created with it.
            # Account.objects.bulk_create