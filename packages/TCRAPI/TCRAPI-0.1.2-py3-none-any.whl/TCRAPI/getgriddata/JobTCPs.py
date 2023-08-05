from TCRAPI.models import ConditionsModel, FilterModel

class jobTCPsClass:
    GRIDID = 75
    GRIDNAME = "JTCPS"
    def __init__(self, JobID):
        self.JobID = JobID
        self.AttachmentURL = "https://apps.tcrsoftware.com/tcr_2/webforms/edit.aspx?id=JTCP&download=1&TCPID="
        self.filterConditions = FilterModel(
            Conditions=[
                ConditionsModel(
                    Attribute="JobID",
                    Values=[
                        str(self.JobID)
                    ],
                    Operator=1
                )
            ]
        )