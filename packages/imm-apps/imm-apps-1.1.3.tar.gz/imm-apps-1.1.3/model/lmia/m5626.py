from model.lmia.common import *
from model.common.commonmodel import CommonModel
from webform.lmiaportal.webformmodel import WebformModel


class Emp5626(BaseModel):
    named: bool
    is_in_seasonal_industry: bool
    start_month: Optional[str]
    end_month: Optional[str]
    last_canadian_number: Optional[int]
    last_tfw_number: Optional[int]
    current_canadian_number: Optional[int]
    current_tfw_number: Optional[int]
    tp_waivable: bool
    waive_creteria: Optional[str]
    has_finished_tp: Optional[bool]
    finished_tp_result: Optional[str]
    activity1_title: Optional[str]
    activity1_description: Optional[str]
    activity1_outcome: Optional[str]
    activity1_comment: Optional[str]
    activity2_title: Optional[str]
    activity2_description: Optional[str]
    activity2_outcome: Optional[str]
    activity2_comment: Optional[str]
    activity3_title: Optional[str]
    activity3_description: Optional[str]
    activity3_outcome: Optional[str]
    activity3_comment: Optional[str]
    activity4_title: Optional[str]
    activity4_description: Optional[str]
    activity4_outcome: Optional[str]
    activity4_comment: Optional[str]
    activity5_title: Optional[str]
    activity5_description: Optional[str]
    activity5_outcome: Optional[str]
    activity5_comment: Optional[str]

    @root_validator
    def checkAnswers(cls, values):
        questions = [
            "tp_waivable",
            "has_finished_tp",
        ]
        explanations = [
            "waive_creteria",
            "finished_tp_result",
        ]
        qas = dict(zip(questions, explanations))
        for k, v in qas.items():
            if values.get(k) and not values.get(v):
                raise ValueError(
                    f"Since {k} is true, but you did not answer the question {v} in info-position sheet"
                )
        is_in_seasonal_industry = values.get("is_in_seasonal_industry", None)
        is_seasonal_vars = [
            values.get(var, None)
            for var in [
                "start_month",
                "end_month",
                "last_canadian_number",
                "last_tfw_number",
                "current_canadian_number",
                "current_tfw_number",
            ]
        ]
        if is_in_seasonal_industry and not all(v is not None for v in is_seasonal_vars):
            raise ValueError(
                "The position is in seasonal industry, but you didn't input all the information required"
            )

        return values


class Personal(BaseModel):
    last_name: Optional[str]
    first_name: Optional[str]
    sex: Optional[str]
    dob: Optional[date]
    citizen: Optional[str]


class M5626Model(CommonModel):
    lmiacase: LmiaCase
    general: General
    lmi: Lmi
    emp5626: Emp5626
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
        # check if TFW is named, details must be included in personal sheet
        self.checkTFW()

    def webform(self, output_json, upload_dir, rcic):
        args = {
            "model_variable": "5626",
            "app": self,
            "output_json": output_json,
            "upload_dir": upload_dir,
            "rcic": rcic,
        }

        wf = WebformModel(**args)
        wf.save()

    def checkTFW(self):
        if self.emp5626.named and not all(
            [
                self.personal.first_name,
                self.personal.last_name,
                self.personal.sex,
                self.personal.citizen,
                self.personal.dob,
            ]
        ):
            raise ValueError(
                "Since TFW is name required, you haven't input all information required in info-personal sheet."
            )
