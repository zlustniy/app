import random
import string

import factory

from .models import (
    User,
    Instance,
    LiabilitiesType,
    SubjectAccumulation, AccumulationRegister,
)
from .models.liabilities_type import TypeRunningChoices


def generate_sequence(size=10, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class InstanceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Instance

    name = factory.Faker('company')


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    instance = factory.SubFactory(InstanceFactory)
    username = factory.Sequence(lambda n: 'user_%03d' % n)


class LiabilitiesTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LiabilitiesType

    name = factory.LazyFunction(lambda: generate_sequence(10, string.digits))
    instance = factory.SubFactory(InstanceFactory)
    postfix = factory.LazyFunction(lambda: generate_sequence(32, string.digits))
    type_running = factory.Faker('random_element', elements=TypeRunningChoices.choices())


class SubjectAccumulationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SubjectAccumulation

    ogrn = factory.LazyFunction(lambda: generate_sequence(15, string.digits))
    name = factory.Faker('name')


class AccumulationRegisterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AccumulationRegister

    user = factory.SubFactory(UserFactory)
    liabilities_type = factory.SubFactory(LiabilitiesTypeFactory)
    amount_record = factory.Faker('pyfloat', left_digits=4, right_digits=2, positive=True)
    amount_total = factory.Faker('pyfloat', left_digits=4, right_digits=2, positive=True)
    subject = factory.SubFactory(SubjectAccumulationFactory)
