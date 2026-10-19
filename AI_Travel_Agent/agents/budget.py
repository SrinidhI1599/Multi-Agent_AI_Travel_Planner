from tools.budget_tool import calculate_budget

class BudgetAgent:

    def run(
        self,
        days,
        user_budget,
        train_cost=0
    ):

        hotel_cost = days * 2500

        food_cost = days * 1000

        transport_cost = days * 800

        sightseeing_cost = days * 1000

        miscellaneous_cost = days * 500

        estimated_total = (
            train_cost
            + hotel_cost
            + food_cost
            + transport_cost
            + sightseeing_cost
            + miscellaneous_cost
        )

        budget_remaining = (
            user_budget - estimated_total
        )

        exceeded = estimated_total > user_budget

        return {
            "user_budget": user_budget,
            "estimated_total": estimated_total,
            "remaining": budget_remaining,
            "exceeded": exceeded,
            "train_cost": train_cost,
            "hotel_cost": hotel_cost,
            "food_cost": food_cost,
            "transport_cost": transport_cost,
            "sightseeing_cost": sightseeing_cost,
            "miscellaneous_cost": miscellaneous_cost
        }