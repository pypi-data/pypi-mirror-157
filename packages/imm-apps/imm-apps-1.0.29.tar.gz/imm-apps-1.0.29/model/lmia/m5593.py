from datetime import date
from typing import Optional, List
from pydantic import BaseModel, root_validator, EmailStr
from model.common.commonmodel import CommonModel
from model.common.person import Person, PersonalAssess
from model.common.address import Address
from model.common.contact import ContactBase
from model.common.advertisement import Advertisement, InterviewRecord
from model.common.jobofferbase import JobofferBase
from model.common.jobposition import PositionBase
from model.lmia.finance import Finance
from termcolor import colored
import os


class LmiaCase(BaseModel):
    area_index: int
    province_index: int
    unemploy_rate: float
    area_median_wage: float
    noc_outlook: int
    reason_failed_hire_canadian: Optional[str]
    provincial_median_wage: float
    is_in_10_days_priority: bool
    top10_wages: float
    is_waived_from_advertisement: bool
    reason_for_waived: Optional[str]
    purpose_of_lmia: str
    stream_of_lmia: str
    has_another_employer: Optional[bool]
    another_employer_name: Optional[str]
    number_of_tfw: int
    duration_number: float
    duration_unit: str
    duration_reason: str
    has_attestation: bool
    use_jobbank: bool
    reason_not_use_jobbank: Optional[str]
    reason_not_recruit: Optional[str]
    provide_details_even_waived: Optional[str]

    @root_validator
    def checkAdditional(cls, values):
        has_another_employer = values.get("has_another_employer", None)
        another_employer_name = values.get("another_employer_name", None)
        if has_another_employer and not another_employer_name:
            raise ValueError(
                "Since has another employer,but did not input the details about it."
            )
        noc_outlook = values.get("noc_outlook", None)
        reason_failed_hire_canadian = values.get("reason_failed_hire_canadian", None)
        if noc_outlook <= 2 and not reason_failed_hire_canadian:
            print(
                colored(
                    "Warning: sinece the outlook is <= 2, but it seems you didn't consider that you may be challanged by processing officer for why there is lack of labours",
                    "yellow",
                )
            )

        return values


class General(BaseModel):
    legal_name: str
    operating_name: Optional[str]
    website: Optional[str]
    establish_date: date
    business_intro: str
    cra_number: str
    ft_employee_number: int
    pt_employee_number: int


class Lmi(BaseModel):
    laid_off_in_12: bool
    laid_off_canadians: Optional[int]
    laid_off_tfw: Optional[int]
    laid_off_reason: Optional[str]
    is_work_sharing: bool
    work_sharing_info: Optional[str]
    labour_dispute: bool
    labour_dispute_info: Optional[str]
    brief_benefit: str
    job_creation_benefit: Optional[str]
    skill_transfer_benefit: Optional[str]
    fill_shortage_benefit: Optional[str]
    other_benefit: Optional[str]
    canadian_lost_job: bool
    canadian_lost_job_info: Optional[str]
    safety_concerns: str

    @root_validator
    def checkLabourDisput(cls, values):
        canadian_lost_job = values.get("canadian_lost_job", None)
        canadian_lost_job_info = values.get("canadian_lost_job_info", None)
        if canadian_lost_job and not canadian_lost_job_info:
            raise ValueError(
                "Since Canadian will lost job because of hiring TFW,but did not input the details about it."
            )
        return values

    @root_validator
    def checkLayoff(cls, values):
        laid_off_in_12 = values.get("laid_off_in_12", None)
        laid_off_canadians = values.get("laid_off_canadians", None)
        laid_off_tfw = values.get("laid_off_tfw", None)
        laid_off_reason = values.get("laid_off_reason", None)
        if laid_off_in_12 and (
            not laid_off_canadians or not laid_off_tfw or not laid_off_reason
        ):
            raise ValueError(
                "Since there is laid of in past 12 months in info lmi sheet,but did not input how many Canadians and/or foreign workers, and/or reason of lay off."
            )
        return values

    @root_validator
    def checkWorkSharing(cls, values):
        is_work_sharing = values.get("is_work_sharing", None)
        work_sharing_info = values.get("work_sharing_info", None)
        if is_work_sharing and not work_sharing_info:
            raise ValueError(
                "Since there is work sharing in info lmi sheet,but did not input the details about it."
            )
        return values


class ErAddress(Address):
    phone: Optional[str]

    @root_validator
    def checkRowCompletion(cls, values):
        all_fields = [
            "po_box",
            "unit",
            "street_number",
            "street_name",
            "city",
            "district",
            "province",
            "country",
            "post_code",
            "phone",
        ]
        all_fields_values = [values[field] for field in all_fields]

        required_fields = [
            "street_number",
            "street_name",
            "city",
            "country",
            "post_code",
            "phone",
        ]
        variable_type = values.get("variable_type")
        display_type = values.get("display_type")

        required_values = [values[field] for field in required_fields]

        has_values = [value for value in required_values if value]

        if (
            any(all_fields_values)
            and not all(required_values)
            and variable_type != "working_address"
        ):
            raise ValueError(
                f"Please check the row with values ({','.join(has_values)}), some required fileds are missed."
            )

        if (
            any(all_fields_values)
            and not all(required_values)
            and variable_type == "working_address"
            and display_type == "工作地点1"
        ):
            raise ValueError(
                f"Please check the row with values ({','.join(has_values)}), some required fileds are missed."
            )

        return values


class Contact(ContactBase):
    middle_name: Optional[str]
    position: str
    po_box: Optional[str]
    unit: Optional[str]
    street_number: str
    street_name: str
    city: str
    province: str
    post_code: str

    @root_validator
    def checkCanadaProvince(cls, values):
        province = values.get("province")
        if province and province not in [
            "AB",
            "BC",
            "MB",
            "NB",
            "NL",
            "NS",
            "NT",
            "NU",
            "ON",
            "PE",
            "QC",
            "SK",
            "YT",
        ]:
            raise ValueError(
                f'Since country is Canada is, the province must be one of  "AB","BC","MB","NB","NL","NS","NT","NU","ON","PE","QC","SK","YT"'
            )
        return values


class Joboffer(JobofferBase):
    phone_country_code: str
    phone: str
    license_request: bool
    license_description: Optional[str]
    union: bool
    atypical_schedule: bool
    atypical_schedule_explain: Optional[str]
    part_time_explain: Optional[str]
    payment_way: str
    ot_after_hours_unit: Optional[str]
    ot_after_hours: Optional[float]
    is_working: bool
    has_probation: bool
    probation_duration: Optional[str]
    disability_insurance: bool
    dental_insurance: bool
    empolyer_provided_persion: bool
    extended_medical_insurance: bool
    extra_benefits: Optional[str]
    offer_date: date
    supervisor_name: str
    supervisor_title: str
    employer_rep: str
    employer_rep_title: str
    vacation_pay_weeks: int
    vacation_pay_percentage: float
    duties_brief: str
    duties: str
    english_french: bool
    oral: Optional[str]
    writing: Optional[str]
    reason_for_no: Optional[str]
    other_language_required: bool
    reason_for_other: Optional[str]
    education_level: str
    is_trade: Optional[bool]
    trade_type: Optional[str]
    specific_edu_requirement: Optional[str]
    skill_experience_requirement: Optional[str]
    other_requirements: Optional[str]

    @root_validator
    def checkProbation(cls, values):
        has_probation = values.get("has_probation", None)
        probation_duration = values["probation_duration"]
        if has_probation and not probation_duration:
            raise ValueError(
                "Since has probation is true, but did not input probation duration"
            )
        return values

    @root_validator
    def checkLanguage(cls, values):
        english_french = values.get("english_french", None)
        oral = values.get("oral", None)
        writing = values.get("writing", None)
        reason_for_no = values.get("reason_for_no", None)
        if english_french and not oral or not writing:
            raise ValueError(
                "Since English or French is true, but did not input oral or/and writting language requirement"
            )
        if not english_french and not reason_for_no:
            raise ValueError(
                "Since there is no English or French requirement, but did not input the reason"
            )
        return values

    @root_validator
    def checkOtherLanguageReason(cls, values):
        other_language_required = values.get("other_language_required", None)
        reason_for_other = values.get("reason_for_other", None)
        if other_language_required and not reason_for_other:
            raise ValueError(
                "Since required other language in job offer sheet,but did not input the reason"
            )
        return values


class Personal(Person):
    pass


class Position(PositionBase):
    pass


# RCIC
class Rcic(BaseModel):
    first_name: str
    last_name: str
    rcic_number: str
    email: EmailStr
    company: str

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name


class M5593Model(CommonModel):
    lmiacase: LmiaCase
    general: General
    lmi: Lmi
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
