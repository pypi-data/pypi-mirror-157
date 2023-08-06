from model.lmia.common import *
from model.common.commonmodel import CommonModel
from webform.lmiaportal.webformmodel import WebformModel


class Emp5627(BaseModel):
    named: bool
    provide_accommodation: bool
    description: Optional[str]
    rent_unit: str
    rent_amount: float
    accommodation_type: str
    explain: Optional[str]
    bedrooms: str
    people: str
    bathrooms: str
    other: Optional[str]
    cap_exempted: bool
    which_exemption: Optional[str]
    exemption_rationale: Optional[str]
    is_in_seasonal_industry: Optional[bool]
    four_week_start_date: Optional[date]
    four_week_end_date: Optional[date]
    q_a: Optional[int]
    q_b: Optional[int]
    q_c: Optional[int]
    q_d: Optional[int]
    q_e: Optional[int]
    q_f: Optional[int]
    q_g: Optional[int]
    q_h: Optional[int]


class M5627Model(CommonModel):
    lmiacase: LmiaCase
    general: General
    lmi: Lmi
    emp5627: Emp5627
    eraddress: List[ErAddress]
    contact: List[Contact]
    finance: List[Finance]
    joboffer: Joboffer
    personal: Personal
    personalassess: PersonalAssess
    position: Position
    advertisement: List[Advertisement]
    interviewrecord: List[InterviewRecord]
    rcic: Rcic

    # initialize the model with a list of excels, which includes all nececcery information the model required. if outpuot_excel_file is not None, it will make an excel file.
    def __init__(self, excels=None, output_excel_file=None):
        if output_excel_file:
            path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), os.path.pardir)
            )
            excels = self.getExcels(
                [
                    "excel/recruitment.xlsx",
                    "excel/pa.xlsx",
                    "excel/er.xlsx",
                    "excel/rep.xlsx",
                    "excel/lmia.xlsx",
                ]
            )
        else:
            if excels is None and len(excels) == 0:
                raise ValueError(
                    "You must input excel file list as source data for validation"
                )
        # call parent class for validating
        super().__init__(excels, output_excel_file, globals())

    def webform(self, output_json, upload_dir, rcic):
        args = {
            "model_variable": "5627",
            "app": self,
            "output_json": output_json,
            "upload_dir": upload_dir,
            "rcic": rcic,
        }
        wf = WebformModel(**args)
        wf.save()
