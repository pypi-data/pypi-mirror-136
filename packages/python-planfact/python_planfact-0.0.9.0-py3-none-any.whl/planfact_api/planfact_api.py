import logging

from .models import *
from .pf_interaction import pf_interaction

logger = logging.getLogger(__name__)

PAGE_LIMIT = 500


def get_currencies():
    path = f'/api/v1/currencies'
    params = {'paging.limit': PAGE_LIMIT,
              'paging.offset': 0}
    items = pf_interaction.request_list('get', path, params=params)
    return items


def get_operations(account_id=None):
    path = f'/api/v1/operations'
    params = {'paging.limit': PAGE_LIMIT,
              'paging.offset': 0}
    if account_id is not None:
        params['filter.accountId'] = account_id
    items = pf_interaction.request_list('get', path, params=params)
    return items


def get_account_by_id(account_id: int):
    path = f"/api/v1/accounts/{account_id}"
    resp, _ = pf_interaction.request('get', path)
    return resp.json()['data']


def get_accounts(changes_from_date=None, add_params=None):
    path = f'/api/v1/accounts'
    params = {'paging.limit': PAGE_LIMIT}
    if add_params is not None:
        params.update(add_params)
    items = pf_interaction.request_list('get', path, changes_from_date, params=params)
    return items


def get_operationcategories(return_tree=False, tree_parent_ids=None):
    # GET / api / v1 / operationcategories
    path = f'/api/v1/operationcategories'
    params = {'paging.limit': PAGE_LIMIT}
    items = pf_interaction.request_list('get', path, params=params)
    # only Income and Outcome categories
    items = [item for item in items if item['operationCategoryType'] in ['Income', 'Outcome']]
    items = sorted(items, key=lambda cat_type: cat_type['operationCategoryType'])
    # check if item got children:
    parent_ids = [item['parentOperationCategoryId'] for item in items if item['parentOperationCategoryId'] is not None]
    for item in items:
        if item['operationCategoryId'] in parent_ids:
            item['is_parent'] = True
        else:
            item['is_parent'] = False
    if not return_tree:
        # return only non parent categories
        return [item for item in items if item['is_parent'] is False]
    else:
        # build tree
        if tree_parent_ids is None:
            parents = [item for item in items if item['parentOperationCategoryId'] is None]
        else:
            parents = [item for item in items if item['operationCategoryId'] in tree_parent_ids]
        level = 0
        tree_items = list()
        while True:
            children = list()
            tree_items += parents
            for parent in parents:
                parent['level'] = level
                tmp_children = [item for item in items
                                if item['parentOperationCategoryId'] == parent['operationCategoryId']]
                parent['childsOperationCategoryIds'] = [item['operationCategoryId'] for item in tmp_children]
                children += tmp_children
            parents = children
            level += 1
            if not parents:
                break
        return tree_items


def get_projects_groups(changes_from_date=None):
    path = f'/api/v1/projects/groups'
    params = {'paging.limit': PAGE_LIMIT}
    items = pf_interaction.request_list('get', path, changes_from_date, params=params)
    return items


def get_projects(changes_from_date=None):
    path = f'/api/v1/projects'
    params = {'paging.limit': PAGE_LIMIT}
    items = pf_interaction.request_list('get', path, changes_from_date, params=params)
    return items


def create_income(operation: IncomeOutcomeOperation):
    path = f'/api/v1/operations/income'
    data = operation.dict()
    res, _ = pf_interaction.request('post', path, data=data)
    return res.json()['data']


def create_outcome(operation: IncomeOutcomeOperation):
    path = f'/api/v1/operations/outcome'
    data = operation.dict()
    res, _ = pf_interaction.request('post', path, data=data)
    return res.json()['data']


def create_move_operation(operation: MoveOperation):
    path = f'/api/v1/operations/move'
    data = operation.dict()
    res, _ = pf_interaction.request('post', path, data=data)
    return res.json()['data']


def create_account(account: Account):
    path = f'/api/v1/accounts'
    data = account.dict()
    res, _ = pf_interaction.request('post', path, data=data)
    return res.json()['data']


def get_allowed_entities(rule, entities, ident_by):
    allowed_ids = None
    if rule['accessRuleType'] == 'Allowed':
        allowed_ids = rule['ids']
    elif rule['accessRuleType'] == 'Disallowed':
        available_ids = [item[ident_by] for item in entities]
        allowed_ids = list(set(available_ids) - set(rule['ids']))
    allowed_entities = [item for item in entities if item[ident_by] in allowed_ids]
    return allowed_entities


def get_user_permissions(user_id, opcat_parent_ids=None):
    path = f'/api/v1/accesscontexts'
    params = {'filter.kind': 'ByBusiness',
              'paging.limit': PAGE_LIMIT}
    items = pf_interaction.request_list('get', path, params=params)
    user = next((item for item in items if item['user']['id'] == user_id), None)
    # get user permission for accounts, projects and categories
    permissions = {}
    # accounts
    entities = get_accounts()
    allowed_entities = get_allowed_entities(user['accountsRule'], entities, 'accountId')
    permissions['accounts'] = allowed_entities
    # categories
    entities = get_operationcategories(return_tree=True, tree_parent_ids=opcat_parent_ids)
    allowed_entities = get_allowed_entities(user['categoriesRule'], entities, 'operationCategoryId')
    permissions['categories'] = allowed_entities
    # projects
    entities = get_projects()
    allowed_entities = get_allowed_entities(user['projectsRule'], entities, 'projectId')
    permissions['projects'] = allowed_entities
    entities = get_projects_groups()
    allowed_entities = get_allowed_entities(user['projectGroupsRule'], entities, 'projectGroupId')
    permissions['project_groups'] = allowed_entities

    return user['user'], permissions


def get_users():
    path = '/api/v1/accesscontexts'
    params = {'filter.kind': 'ByBusiness',
              'paging.limit': PAGE_LIMIT}
    items = pf_interaction.request_list('get', path, params=params)
    items = [item['user'] for item in items]
    return items


def get_account_history():
    path = '/api/v1/bizinfos/accountshistory'
    resp, _ = pf_interaction.request('get', path)
    return resp.json()["data"]


def get_balance_by_id(account_id: int):
    account = get_account_by_id(account_id)
    all_account_histories = get_account_history()
    account_hist = next((ah for ah in all_account_histories if ah['accountId'] == account['accountId']), None)
    if account_hist is None:
        balance = 0.
    else:
        fact_values = [float(fh["factValue"]) for fh in account_hist["details"]]
        if account["startingRemainderValue"] is None:
            account["startingRemainderValue"] = 0
        balance = sum(fact_values) + account["startingRemainderValue"]
    return balance


def get_balances():
    accounts = get_accounts()
    all_account_histories = get_account_history()
    balances = list()
    for account in accounts:
        account_hist = next((ah for ah in all_account_histories if ah['accountId'] == account['accountId']), None)
        if account_hist is None:
            balance = 0.
        else:
            fact_values = [float(fh["factValue"]) for fh in account_hist["details"]]
            if account["startingRemainderValue"] is None:
                account["startingRemainderValue"] = 0
            balance = sum(fact_values) + account["startingRemainderValue"]
        balances.append({'accountId': account['accountId'],
                         'title': account['title'],
                         'balance': balance})
    return balances
