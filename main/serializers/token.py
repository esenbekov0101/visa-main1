
from rest_framework import serializers as srz

from main.choices import Role

from main.serializers.fields import ChoiceField



class TokenObtainPairResponseSerializer(srz.Serializer):
    access = srz.CharField()
    refresh = srz.CharField()
    # role = ChoiceField(Role.choices)
    # branch = srz.CharField()
    # fullname = srz.CharField()



class TokenRefreshResponseSerializer(srz.Serializer):
     access = srz.CharField()
     # role = ChoiceField(Role.choices)
     # branch = srz.CharField()
     # fullname = srz.CharField()




