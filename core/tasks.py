import fpdf
import hashlib
from celery import shared_task
from django.conf import settings


@shared_task
def make_pdf(form_dict, offer_dict, pk):
    pdf = fpdf.FPDF()
    pdf.add_page()
    pdf.set_xy(0, 0)
    pdf.set_font('arial', 'B', 13.0)
    pdf_data = f"""
                         Form                     
    name     phone_number        passport_number     rating
    {form_dict['name']}         {form_dict['phone_number']}        {form_dict['passport_number']}           {form_dict['rating']}
                         Offer                 
    description          loan_type                min_rating             max_rating
    {offer_dict['description']}                    {offer_dict['loan_type']}             {offer_dict['min_rating']}        {offer_dict['max_rating']}
    """

    datas = pdf_data.splitlines()
    for i, data in enumerate(datas):
        pdf.cell(ln=i, h=5.0, align='L', w=i, txt=data, border=0)

    pdf_name_with_salt = f"proposal{pk}{settings.SECRET_KEY}".encode()
    hashed_pdf_file = hashlib.sha512(pdf_name_with_salt).hexdigest()

    pdf.output(f"{settings.BASE_DIR}/proposals/{hashed_pdf_file}.pdf", 'F')
