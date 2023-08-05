from TCRAPI.models import ConditionsModel, FilterModel


class ticketsClass:
    GRIDID = 9
    GRIDNAME = "TICKETS"
    def __init__(self):
        self.filterConditions = FilterModel(
            Conditions=[
                ConditionsModel(
                    Attribute="Status",
                    Values=["A", "E", "F", "I", "V"],
                    Operator=12
                ),
            ]
        )

    def setStatusFilter(self, Status):
        """
        Sets the status filter for the tickets grid.
            - A - Active
            - E - Review
            - F - Final Edit
            - I - Invoices
            - V - Void
        """
        if isinstance(Status, list):
            self.filterConditions.Conditions = [
                ConditionsModel(
                    Attribute="Status",
                    Values=Status,
                    Operator=12
                ),
            ]
        if isinstance(Status, str):
            self.filterConditions.Conditions = [
                ConditionsModel(
                    Attribute="Status",
                    Values=[Status],
                    Operator=12
                ),
            ]
