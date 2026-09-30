# Library Automation Tool

A Python-based library management application created as a practical internship project.

## Features
- Add and search books
- Add library members
- Issue books with due dates
- Return books and detect late returns
- Input validation
- Error handling
- CSV-based data storage
- Dashboard and reports
- Download transaction/book reports
- Basic automated tests

## Technologies
- Python
- Streamlit
- Pandas
- Pytest

## Run on a computer
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run in Google Colab
```python
!pip install -q streamlit pandas
```
Then upload `app.py` and the `data` folder, and run:
```python
!streamlit run app.py &>/content/log.txt &
```
For a public demo link in Colab, use a tunneling service available in your environment.

## Project workflow
1. Add books.
2. Add members.
3. Issue an available book.
4. System creates a transaction and reduces available copies.
5. Return the book.
6. System increases available copies and checks late return.
7. View reports and download CSV files.

## Internship submission description
"Developed a Python-based Library Automation Tool using Streamlit and Pandas. The application automates book inventory, member registration, issue/return transactions, due-date tracking, input validation, error handling, reporting and CSV data processing. The project demonstrates modular Python development, practical data processing and testing."
