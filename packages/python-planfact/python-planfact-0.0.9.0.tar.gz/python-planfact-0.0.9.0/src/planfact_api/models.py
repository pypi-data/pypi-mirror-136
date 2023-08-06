from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator, NonNegativeFloat
from typing import List


class OperationItems(BaseModel):
    calculationDate: datetime
    isCalculationCommitted: bool
    contrAgentId: Optional[int]
    operationCategoryId: Optional[int]
    projectId: Optional[int]
    firstAdditionalOperationAttributeId: Optional[int]
    value: NonNegativeFloat

    @validator('calculationDate')
    def remainder_date(cls, v):
        return v.strftime('%Y-%m-%d')

    @validator('projectId', 'operationCategoryId')
    def check_for_zero_ids(cls, v):
        if v == 0:
            return None
        else:
            return v


class IncomeOutcomeOperation(BaseModel):
    operationDate: datetime
    calculationDate: Optional[datetime]
    isCalculationCommitted: Optional[bool]
    contrAgentId: Optional[int]
    accountId: int
    operationCategoryId: Optional[int]
    comment: Optional[str]
    value: Optional[NonNegativeFloat]
    isCommitted: Optional[bool]
    items: List[OperationItems]
    externalId: Optional[str]
    distributeCalculationDate: Optional[datetime]
    distributeCalculationType: Optional[str]

    @validator('operationDate', 'calculationDate', 'distributeCalculationDate')
    def remainder_date(cls, v):
        return v.strftime('%Y-%m-%d')


class MoveOperation(BaseModel):
    """
    debitingDate: string (date)     Дата списания
    admissionDate: string (date)     Дата зачисления
    debitingAccountId: integer (int32)     Счет списания
    admissionAccountId: integer (int32)     Счет зачисления
    debitingValue: number (double) x ≥ 0     Сумма списания
    admissionValue: number (double) x ≥ 0     Сумма зачисления
    comment: string     Комментарий
    valueByProjects: object     Сумма по проектам
    isCommitted: boolean     Признак того, что операция проведена
    importLogId: integer (int32)     Идентификатор лога импорта
    debitingItems: OperationPartRequest     Части операции списания
    admissionItems: OperationPartRequest     Части операции зачисления
    debitingExternalId: string   Внешний идентификатор для списания
    admissionExternalId: string   Внешний идентификатор для зачисления
    """
    debitingDate: datetime
    admissionDate: datetime
    debitingAccountId: int
    admissionAccountId: int
    debitingValue: Optional[NonNegativeFloat]
    admissionValue: Optional[NonNegativeFloat]
    comment: Optional[str]
    isCommitted: Optional[bool]
    importLogId: Optional[int]
    debitingItems: Optional[List[OperationItems]]
    admissionItems: Optional[List[OperationItems]]
    debitingExternalId: Optional[str]
    admissionExternalId: Optional[str]

    @validator('debitingDate', 'admissionDate')
    def remainder_date(cls, v):
        return v.strftime('%Y-%m-%d')

    def set_to_committed(self):
        self.isCommitted = True
        for item in self.debitingItems or []:
            item.isCalculationCommitted = True
            item.calculationDate = self.debitingDate
        for item in self.admissionItems or []:
            item.isCalculationCommitted = True
            item.calculationDate = self.admissionDate


class Account(BaseModel):
    title: str
    companyId: int
    accountType: str
    currencyCode: str
    longTitle: Optional[str]
    description: Optional[str]
    accountType: Optional[str]
    accountAcct: Optional[str]
    correspondentAcct: Optional[str]
    accountBik: Optional[str]
    accountBank: Optional[str]
    active: Optional[bool]
    remainder: Optional[float]
    remainderDate: datetime
    externalId: Optional[str]
    accountGroupId: Optional[int]

    @validator('remainderDate')
    def remainder_date(cls, v):
        return v.strftime('%Y-%m-%d')
