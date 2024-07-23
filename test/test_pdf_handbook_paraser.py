from handbook.handbook_pdf_parser import handbook_parser


def test_handbook_parser():
    test_pdf = "D:\\LLM\\project\\uDocParser\\examples\\doc_dataset\\CECS132_2002给水排水多功能水泵控制阀应用技术规程.pdf"
    pdf_dir = "D:\\LLM\\project\\uDocParser\\examples\\doc_dataset"
    handbook_parser(test_pdf)