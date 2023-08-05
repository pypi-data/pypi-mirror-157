__all__ = ('IdentificationProcessPoint', 'AutoIdentificationTaskPoint')

from expressmoney.api import *

SERVICE = 'profiles'


class IdentificationProcessReadContract(Contract):
    EMPTY = 'EMPTY'
    SUCCESS = 'SCS'
    FAILURE = 'FAIL'
    RESULT_CHOICES = (
        (EMPTY, EMPTY),
        (FAILURE, FAILURE),
        (SUCCESS, SUCCESS),
    )
    id = serializers.IntegerField(min_value=1)
    updated = serializers.DateTimeField()
    user_id = serializers.IntegerField(min_value=1)
    result = serializers.ChoiceField(choices=RESULT_CHOICES)
    comment = serializers.CharField(max_length=1024, allow_blank=True)
    status = serializers.CharField(max_length=50)


class AutoIdentificationTaskReadContract(Contract):
    EMPTY = 'EMPTY'
    SUCCESS = 'SCS'
    FAILURE = 'FAIL'
    RESULT_CHOICES = (
        (EMPTY, EMPTY),
        (FAILURE, FAILURE),
        (SUCCESS, SUCCESS),
    )
    id = serializers.IntegerField(min_value=1)
    created = serializers.DateTimeField()
    result = serializers.ChoiceField(choices=RESULT_CHOICES)
    comment = serializers.CharField(max_length=1024, allow_blank=True)


class IdentificationProcessID(ID):
    _service = SERVICE
    _app = 'identification'
    _view_set = 'identification_process'


class AutoIdentificationTaskID(ID):
    _service = SERVICE
    _app = 'identification'
    _view_set = 'auto_identification_task'


class IdentificationProcessPoint(ListPointMixin, ContractPoint):
    _point_id = IdentificationProcessID()
    _read_contract = IdentificationProcessReadContract


class AutoIdentificationTaskPoint(ListPointMixin, ContractPoint):
    _point_id = AutoIdentificationTaskID()
    _read_contract = AutoIdentificationTaskReadContract
