import requests
from nemoguardrails import LLMRails,RailsConfig
from nemoguardrails.actions import action
from nemoguardrails.actions.actions import ActionResult
from datetime import datetime, timedelta
import re
import os
from openai import OpenAI
from nemoguardrails.llm.taskmanager import LLMTaskManager
from nemoguardrails.llm.params import llm_params
from nemoguardrails.actions.llm.utils import llm_call
from langchain.llms.base import BaseLLM
from typing import Optional
import os
import uuid
from typing import Optional, Union



@action()
async def get_transactions_history():
    api_url = "https://tec-digital-konecta-dev.technisys.net/api/faas/function/tec-digital-konecta-wh-dispatcher-func/test/get-dynamic-options"
    params = {"minAccounts": 5, "maxAccounts": 5}


    our_fake_entry = {
        "m_tx_id": "P-custom",
        "m_tx_description": "Custom description for test",
        "m_tx_type": "Test Account",
        "m_tx_date": "Apr 1, 2024",
        "m_tx_amount": "$123.45"
    }

    try:
        response = requests.post(api_url, json=params)
        response.raise_for_status()
        data = response.json()


        transactions = data.get("m_tx_data", [])
        transactions.append(our_fake_entry)

        return transactions
    except requests.RequestException as e:
        print(f"Error fetching transactions: {e}")
        return []


@action()
async def get_transaction_by_date(date: str):
    api_url = "https://tec-digital-konecta-dev.technisys.net/api/faas/function/tec-digital-konecta-wh-dispatcher-func/test/get-dynamic-options"
    params = {"minAccounts": 5, "maxAccounts": 5}

    try:
        response = requests.post(api_url, json=params)
        response.raise_for_status()
        data = response.json()
        transactions = data.get("m_tx_data", [])
        our_fake_entry = {
            "m_tx_id": "123",
            "m_tx_description": "Custom description for test",
            "m_tx_type": "Test Account",
            "m_tx_date": "Apr 1, 2024",
            "m_tx_amount": "$123.45"
        }
        transactions.append(our_fake_entry)

    except requests.RequestException as e:
        print(f"Error fetching transactions: {e}")
        transactions = [our_fake_entry]


    try:
        input_date = datetime.strptime(date, "%m-%d-%Y")
    except ValueError:
        return "Invalid date format. Please enter the date in mm-dd-yyyy format."

    for transaction in transactions:

        transaction_date = datetime.strptime(transaction["m_tx_date"], "%b %d, %Y")
        if input_date == transaction_date:
            return transaction

    return None


@action()
async def get_date_transaction(user_input: str, llm_task_manager: LLMTaskManager,llm: Optional[BaseLLM] = None):

    prompt = llm_task_manager.render_task_prompt(
        task="extract_date",
        context={"user_input": user_input}
    )

    with llm_params(llm, temperature=1.0,max_tokens=200):
        extracted_date = await llm_call(llm, prompt )

    print(f"Extracted date: {extracted_date}")

    return extracted_date


@action()
async def create_dispute_transaction(user_input: str, llm_task_manager: LLMTaskManager,llm: Optional[BaseLLM] = None):


    transaction_details = await lookup_transaction_by_date(user_input)
    if transaction_details:
        return f"Transaction details: {transaction_details}"
    else:
        return "No transaction found for the provided date."


@action()
async def get_origin_account(user_input, llm_task_manager: LLMTaskManager,llm: Optional[BaseLLM] = None):

    prompt = llm_task_manager.render_task_prompt(
        task="extract_origin_account",
        context={"user_input": user_input}
    )

    with llm_params(llm, temperature=0.7,max_tokens=200):
        extract_origin_account = await llm_call(llm, prompt )

    print(f"Extracted origin account: --{extract_origin_account.lower().strip()}--")

    return extract_origin_account.lower().strip()


@action()
async def get_destination_account(user_input, llm_task_manager: LLMTaskManager,llm: Optional[BaseLLM] = None):

    prompt = llm_task_manager.render_task_prompt(
        task="extract_destination_account",
        context={"user_input": user_input}
    )

    with llm_params(llm, temperature=0.7,max_tokens=200):
        extract_destination_account = await llm_call(llm, prompt )

    print(f"Extracted Destination account: --{extract_destination_account.lower().strip()}--")

    return extract_destination_account.lower().strip()

@action()
async def get_account(user_input, llm_task_manager: LLMTaskManager,llm: Optional[BaseLLM] = None):

    prompt = llm_task_manager.render_task_prompt(
        task="extract_account",
        context={"user_input": user_input}
    )

    with llm_params(llm, temperature=0.7,max_tokens=200):
        extracted_account = await llm_call(llm, prompt )

    print(f"Extracted account: --{extracted_account}--")

    return extracted_account.lower().strip()


@action()
async def get_amount(user_input: str, llm_task_manager: LLMTaskManager, llm: Optional[BaseLLM] = None):
    prompt = llm_task_manager.render_task_prompt(
        task="extract_amount",
        context={"user_input": user_input}
    )

    with llm_params(llm, temperature=1.0, max_tokens=200):
        extracted_amount = await llm_call(llm, prompt)

    print(f"Extracted amount: --{extracted_amount.lower().strip()}--")

    return extracted_amount.lower().strip()

@action()
async def get_balance(user_input, llm_task_manager: LLMTaskManager,llm: Optional[BaseLLM] = None):

    prompt = llm_task_manager.render_task_prompt(
        task="extract_account",
        context={"user_input": user_input}
    )

    with llm_params(llm, temperature=1.0,max_tokens=200):
        extracted_account = await llm_call(llm, prompt )

    print(f"Extracted account: {extracted_account}")

    validated_account = validate_account(extracted_account.strip())
    if "Invalid account" in validated_account:
        return validated_account


    url = "https://pintserv.perf.aws.gft/intserv/4.0/getBalance"
    headers = {
        "response-content-type": "json"
    }
    data = {
        "apiLogin": "Mwj2Yr-0057",
        "apiTransKey": "galileotest",
        "providerId": "342",               # Hardcoded providerId
        "transactionId": "test-anupama",   # Hardcoded transactionId
        "accountNo": validated_account
    }

    def format_balance_info(balance_info):
        return (
            f"Balance: {balance_info.get('balance')}\n"
            f"Balance without pending: {balance_info.get('balance_without_pending')}\n"
            f"Currency code: {balance_info.get('currency_code')}\n"
            f"Pending adjustments: {balance_info.get('pending_adjustments')}\n"
            f"Pending billpay: {balance_info.get('pending_billpay')}\n"
            f"Pending purchase: {balance_info.get('pending_purchase')}\n"
            f"Balance without auths: {balance_info.get('balance_without_auths')}"
        )

    try:
        response = requests.post(url, headers=headers, data=data, verify=False)
        response.raise_for_status()
        balance_info = response.json()

        # Extraer y devolver el campo response_data
        response_data = balance_info.get('response_data', {})
        return f"Transaction details:\n{format_balance_info(response_data)}"

    except requests.exceptions.RequestException as e:
        print(f"Error when calling API: {e}")
        # Mensaje de error en caso de fallo en la llamada a la API
        hardcoded_balance_info = {
            "balance": 50000.08,
            "balance_without_pending": "50000.08",
            "currency_code": "840",
            "pending_adjustments": 0,
            "pending_billpay": 0,
            "pending_purchase": 0,
            "balance_without_auths": 50000.08
        }
        return f"Account details:\n{format_balance_info(hardcoded_balance_info)}"

    except ValueError:
        # Manejo de error si la respuesta no se puede convertir a JSON
        hardcoded_balance_info = {
            "balance": 50000.08,
            "balance_without_pending": "50000.08",
            "currency_code": "840",
            "pending_adjustments": 0,
            "pending_billpay": 0,
            "pending_purchase": 0,
            "balance_without_auths": 50000.08
        }
        return f"Account details:\n{format_balance_info(hardcoded_balance_info)}"



@action()
async def get_params(user_input, llm_task_manager: LLMTaskManager,llm: Optional[BaseLLM] = None):

    prompt = llm_task_manager.render_task_prompt(
        task="extract_transfer_details",
        context={"user_input": user_input}
    )

    with llm_params(llm, temperature=0.7,max_tokens=200):
        extract_transfer_details = await llm_call(llm, prompt )

    print(f"Extracted extract_transfer_details: {extract_transfer_details}")

    values_list = extract_transfer_details.split('|')

    print(f"Values list: {values_list}")
    return values_list


@action()
async def get_allparams(user_input, llm_task_manager: LLMTaskManager, llm: Optional[BaseLLM] = None):
    # Extract origin account
    prompt_origin = llm_task_manager.render_task_prompt(
        task="extract_origin_account",
        context={"user_input": user_input}
    )
    with llm_params(llm, temperature=0.2, max_tokens=200):
        origin_account = await llm_call(llm, prompt_origin)

    # Extract transfer account
    prompt_transfer = llm_task_manager.render_task_prompt(
        task="extract_transfer_account",
        context={"user_input": user_input}
    )
    with llm_params(llm, temperature=0.2, max_tokens=200):
        transfer_account = await llm_call(llm, prompt_transfer)

    # Extract amount
    prompt_amount = llm_task_manager.render_task_prompt(
        task="extract_amount",
        context={"user_input": user_input}
    )
    with llm_params(llm, temperature=0.2, max_tokens=200):
        amount = await llm_call(llm, prompt_amount)

    # Print the raw extracted details for debugging
    print(f"Extracted origin account: {origin_account}")
    print(f"Extracted transfer account: {transfer_account}")
    print(f"Extracted amount: {amount}")

    values_list = [origin_account.strip(), transfer_account.strip(), amount.strip()]

    # Print the values list for debugging
    print(f"Values list: {values_list}")

    return values_list



@action()
def create_transfer_account(accountNo, amount, transferToAccountNo):
    """
    Mock function to simulate the Create Account Transfer API call.

    Args:
        accountNo (str): The PRN or PAN of the sending account.
        amount (float or str): Currency amount.
        transferToAccountNo (str): The PAN or PRN of the receiving account.

    Returns:
        dict: Mock response simulating the API response.
    """
    print(f"Creating transfer from account {accountNo} to account {transferToAccountNo} for amount {amount}.")

    # Convert amount to float if it is not already
    if isinstance(amount, str):
        try:
            amount = float(amount)
        except ValueError:
            raise ValueError("Invalid amount format. Please ensure the amount is a valid number.")

    # Mock response data
    response = {
        "status_code": 0,
        "status": "Success",
        "processing_time": 0.527,
        "response_data": {
            "old_balance": 1000.00,
            "new_balance": 1000.00 - amount,
            "adjustment_trans_id": 57906,
            "transfer_account_id": 0,
            "sender_fee_amount": 0,
            "payment_trans_id": 4161926,
            "transfer_to_account": {
                "old_balance": 500.00,
                "new_balance": 500.00 + amount
            }
        },
        "echo": {
            "provider_transaction_id": "",
            "provider_timestamp": None,
            "transaction_id": str(uuid.uuid4())
        },
        "rtoken": str(uuid.uuid4()),
        "system_timestamp": "2020-07-13 10:47:17"
    }
    print(f"Response: {response}")

    return response


@action()
async def get_confirm(user_input, llm_task_manager: LLMTaskManager,llm: Optional[BaseLLM] = None):

    prompt = llm_task_manager.render_task_prompt(
        task="extract_confirm",
        context={"user_input": user_input}
    )
    print
    with llm_params(llm, temperature=1.0,max_tokens=200):
        extracted_confirm = await llm_call(llm, prompt )

    print(f"Extracted confirm: {extracted_confirm}")

    return extracted_confirm



def init(app: LLMRails):

    app.register_action(get_transactions_history, "get_transactions_history")
    app.register_action(get_transaction_by_date, "get_transaction_by_date")
    app.register_action(get_date_transaction, "get_date_transaction")
    app.register_action(create_dispute_transaction, "create_dispute_transaction")
    app.register_action(get_balance, "get_balance")
    app.register_action(get_account, "get_account")
    app.register_action(get_origin_account, "get_origin_account")
    app.register_action(get_destination_account, "get_destination_account")
    app.register_action(get_amount, "get_amount")
    app.register_action(create_transfer_account, "create_transfer_account")
    app.register_action(get_confirm, "get_confirm")
    app.register_action(get_params, "get_params")
    app.register_action(get_params, "get_allparams")



