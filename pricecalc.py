from typing import Literal


def calculate_mongodb_monthly_cost(
    storage_gb: int,
    row_writes: int,
    row_reads: int,
    bytes_per_row: int,
):
    READ_PRICE_PER_M_FIRST_50M = 0.10
    READ_PRICE_PER_M_NEXT_500M = 0.05
    READ_PRICE_PER_M_THEREAFTER = 0.01
    WRITE_PRICE_PER_M = 1.0
    STORAGE_PRICE_PER_GB = 0.25
    BACKUP_PRICE_PER_GB = 0.2
    TRANSFER_PRICE_PER_GB = 0.01

    write_price = (
        row_writes / 1e6 * WRITE_PRICE_PER_M
        + row_writes * bytes_per_row / 1e9 * TRANSFER_PRICE_PER_GB
    )

    read_price = (
        READ_PRICE_PER_M_FIRST_50M * min(row_reads / 1e6, 50)
        + (row_reads / 1e6 > 50)
        * READ_PRICE_PER_M_NEXT_500M
        * min(row_reads / 1e6 - 50, 500)
        + (row_reads / 1e6 > 550)
        * READ_PRICE_PER_M_THEREAFTER
        * (row_reads / 1e6 - 550)
        + row_reads * bytes_per_row / 1e9 * TRANSFER_PRICE_PER_GB
    )

    storage_price = storage_gb * (STORAGE_PRICE_PER_GB + BACKUP_PRICE_PER_GB)

    return write_price + read_price + storage_price


def calculate_firebase_ciam_monthly_cost(
    user_amount: int,
    percentage_of_tier2_auth_users: float,
):
    SIGN_IN_PRICE_PER_TIER1_AFTER_50K = 0.0055
    SIGN_IN_PRICE_PER_TIER2_AFTER_50 = 0.015

    tier1_users = user_amount * (1 - percentage_of_tier2_auth_users)
    tier2_users = user_amount * percentage_of_tier2_auth_users
    return (tier1_users > 50_000) * SIGN_IN_PRICE_PER_TIER1_AFTER_50K + (
        tier2_users > 50
    ) * SIGN_IN_PRICE_PER_TIER2_AFTER_50


def calculate_cost(
    initial_user_amount: int,
    user_growth_rate: int,
    user_growth_type: Literal["Absoluto", "Percentual"],
    initial_companies_per_user: int,
    monthly_new_companies_per_user: int,
    targets_per_company: int,
    actions_per_target: int,
    daily_analysis_per_user: int,
    companies_analyzed_per_user: int,
    bytes_per_row: int,
    percentage_of_tier2_auth_users: float,
    app_price: int,
    months: int,
):
    monthly_costs = [0] * months

    def calculate_row_writes(user_amount, company_amount):
        return user_amount * company_amount * targets_per_company

    def calculate_row_reads(user_amount):
        return (
            user_amount
            * daily_analysis_per_user
            * companies_analyzed_per_user
            * (1 + targets_per_company * (1 + actions_per_target))
            * 30
        )

    # Initial cost
    initial_row_writes = calculate_row_writes(
        initial_user_amount, initial_companies_per_user
    )
    initial_mongodb_cost = calculate_mongodb_monthly_cost(
        0, initial_row_writes, 0, bytes_per_row
    )

    current_storage_gb = initial_row_writes * bytes_per_row / 1e9
    current_user_amount = initial_user_amount

    for month in range(months):

        if user_growth_type == "Absoluto":
            new_user_amount = user_growth_rate
        elif user_growth_type == "Percentual":
            new_user_amount = current_user_amount * user_growth_rate

        new_user_initial_row_writes = calculate_row_writes(
            new_user_amount, initial_companies_per_user
        )

        current_user_amount += new_user_amount
        row_writes = new_user_initial_row_writes + calculate_row_writes(
            current_user_amount, monthly_new_companies_per_user
        )

        current_storage_gb += row_writes * bytes_per_row / 1e9

        row_reads = calculate_row_reads(current_user_amount)

        mongodb_cost = calculate_mongodb_monthly_cost(
            current_storage_gb, row_writes, row_reads, bytes_per_row
        )

        firebase_ciam_cost = calculate_firebase_ciam_monthly_cost(
            current_user_amount, percentage_of_tier2_auth_users
        )

        yield initial_mongodb_cost + mongodb_cost + firebase_ciam_cost, current_user_amount, current_storage_gb, current_user_amount * app_price
        initial_mongodb_cost = 0

    return monthly_costs
