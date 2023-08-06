__all__ = ('CreditScoringTaskPoint',)

from expressmoney.api import *


SERVICE = 'profiles'
APP = 'credit_scoring'


class CreditScoringTaskReadContract(Contract):
    EMPTY = 'EMPTY'
    SUCCESS = 'SCS'
    FAILURE = 'FAIL'
    RESULT_CHOICES = (
        (EMPTY, EMPTY),
        (FAILURE, FAILURE),
        (SUCCESS, SUCCESS),
    )
    RU = 'RU'
    COUNTRY_CHOICES = (
        (RU, RU),
    )
    id = serializers.IntegerField(min_value=1)
    created = serializers.DateTimeField()
    user_id = serializers.IntegerField(min_value=1)
    country = serializers.ChoiceField(choices=COUNTRY_CHOICES)
    result = serializers.ChoiceField(choices=RESULT_CHOICES)
    score = serializers.DecimalField(max_digits=3, decimal_places=2, allow_null=True)
    comment = serializers.CharField(max_length=1024, allow_blank=True)


class CreditScoringTaskID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'credit_scoring_task'


class CreditScoringTaskPoint(ListPointMixin, ContractPoint):
    _point_id = CreditScoringTaskID()
    _read_contract = CreditScoringTaskReadContract
