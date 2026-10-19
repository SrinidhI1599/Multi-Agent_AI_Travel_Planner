from tools.travel_tool import MODES, search_travel


class TravelAgent:
    """
    One agent for every way of getting there: train, flight and bus.
    Replaces the old TrainAgent.
    """

    def run(
        self,
        origin,
        destination,
        travel_date,
        mode="all",
        travel_class="3A",
        travellers=1
    ):
        """
        mode: "train" | "flight" | "bus" | "car" | "all"

        Returns:
            {
                "options": {"train": [...], "flight": [...], "bus": [...], "car": [...]},
                "best": the option with the lowest round-trip total (or None),
                "cost": round-trip cost for all travellers (0 if unknown)
            }
        """

        modes = list(MODES) if mode == "all" else [mode]

        options = {}

        for m in modes:
            options[m] = search_travel(
                origin,
                destination,
                travel_date,
                m,
                travel_class
            )

        # Round-trip total for the whole group, per option:
        #   train / flight / bus -> fare is per person
        #   car                  -> fare is per vehicle (4 seats)
        for found in options.values():
            for o in found:
                o["total_cost"] = self._total_cost(o, travellers)

        priced = [
            o
            for found in options.values()
            for o in found
            if o["total_cost"]
        ]

        best = min(priced, key=lambda o: o["total_cost"]) if priced else None

        cost = best["total_cost"] if best else 0

        return {
            "options": options,
            "best": best,
            "cost": cost
        }

    @staticmethod
    def _total_cost(option, travellers):
        if not option["fare"]:
            return 0

        if option["per_vehicle"]:
            vehicles = -(-travellers // option["seats"])  # ceil division
            return option["fare"] * 2 * vehicles

        return option["fare"] * 2 * travellers