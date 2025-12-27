import PyPDF2
def merge_pdfs(odd_pdf_path, even_pdf_path, output_pdf_path):
    # 홀수 페이지 파일과 짝수 페이지 파일 열기
    odd_pdf = open(odd_pdf_path, 'rb')
    even_pdf = open(even_pdf_path, 'rb')

    # PyPDF2에서 PdfReader를 사용해 PDF 파일 읽기
    odd_reader = PyPDF2.PdfReader(odd_pdf)
    even_reader = PyPDF2.PdfReader(even_pdf)

    # 결과 PDF를 만들기 위한 PdfWriter 객체 생성
    pdf_writer = PyPDF2.PdfWriter()

    # 두 파일의 페이지 수 확인 (같아야 함)
    total_pages = len(odd_reader.pages)

    if len(even_reader.pages) != total_pages:
        print("PDF 파일의 페이지 수가 다릅니다.")
        return

    # 홀수 페이지와 짝수 페이지를 번갈아가며 추가
    for i in range(total_pages):
        # 홀수 페이지 추가 (odd_pdf에서는 정방향)
        pdf_writer.add_page(odd_reader.pages[i])

        # 짝수 페이지 추가 (even_pdf에서는 역순)
        even_page = even_reader.pages[total_pages - i - 1]
        pdf_writer.add_page(even_page)

    # 결과 PDF 파일 저장
    with open(output_pdf_path, 'wb') as output_pdf:
        pdf_writer.write(output_pdf)

    # 파일 닫기
    odd_pdf.close()
    even_pdf.close()
    print(f"PDF 파일이 성공적으로 병합되었습니다. 저장 경로: {output_pdf_path}")


# PDF 병합 실행 예시
if __name__ == "__main__":
    # 사용 예시 (직접 경로를 입력해서 실행할 경우)
    odd_pdf_path = "odd_pages.pdf"   # 홀수 페이지 파일 (1, 3, 5...)
    even_pdf_path = "even_pages.pdf" # 짝수 페이지 파일 (역순: 6, 4, 2...)
    output_pdf_path = "merged_output.pdf"

    # 파일이 실제로 존재할 때만 실행
    import os
    if os.path.exists(odd_pdf_path) and os.path.exists(even_pdf_path):
        merge_pdfs(odd_pdf_path, even_pdf_path, output_pdf_path)
    else:
        print("예시: 홀수/짝수 PDF 경로를 설정하고 merge_pdfs 함수를 호출하세요.")
