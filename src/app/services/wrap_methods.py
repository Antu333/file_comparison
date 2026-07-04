from src.app.services.read_file import files
from src.app.services.methods import sub

class wrapper:
    def call_docx_report(args):
        sub.docx_report(sub.docx1_content, sub.docx2_contennt)

    def call_pdf_report(args):
        sub.pdf_report(sub.pdf1_content, sub.pdf2_content)

    def call_csv_sym(args):
        sub.csv_report_for_symmetric(sub.csv1,sub.csv2)

    def call_csv_asym(args):
        sub.csv_report_for_asymmetric(args.name1,args.name2,args.key_column)

    def call_excel_report(args):
        sub.excell_report(sub.xl_file1,sub.xl_file2)

    def call_summary_doc(args):
        content1 = files.get_text(args.name1)
        content2 = files.get_text(args.name2)
        sub.summary_generate_for_docx_and_pdfs(content1, content2)

    def call_summary_pdf(args):
        content1 = files.extract_text_from_pdf(args.name1)
        content2 = files.extract_text_from_pdf(args.name2)
        sub.summary_generate_for_docx_and_pdfs(content1, content2)

    def call_summary_csv(args):
        content1 = files.read_csv(args.name1)
        content2 = files.read_csv(args.name2)
        sub.summary_generate_for_csv_and_excel(content1, content2)

    def call_summary_excel(args):
        content1 = files.read_excel(args.name1)
        content2 = files.read_excel(args.name2)
        sub.summary_generate_for_csv_and_excel(content1, content2)

    def call_csv_to_dict(args):
        csv1 = files.read_csv(args.name1)
        csv2 = files.read_csv(args.name2)
        sub.csv_string_to_dict(csv1, csv2)