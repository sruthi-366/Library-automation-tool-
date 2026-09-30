import streamlit as st
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

DATA_DIR = Path("data")
BOOKS_FILE = DATA_DIR / "books.csv"
MEMBERS_FILE = DATA_DIR / "members.csv"
ISSUES_FILE = DATA_DIR / "issues.csv"

DATA_DIR.mkdir(exist_ok=True)

def init_files():
    if not BOOKS_FILE.exists():
        pd.DataFrame(columns=["book_id","title","author","category","total","available"]).to_csv(BOOKS_FILE, index=False)
    if not MEMBERS_FILE.exists():
        pd.DataFrame(columns=["member_id","name","email","phone"]).to_csv(MEMBERS_FILE, index=False)
    if not ISSUES_FILE.exists():
        pd.DataFrame(columns=["issue_id","book_id","member_id","issue_date","due_date","return_date","status"]).to_csv(ISSUES_FILE, index=False)

def load_data():
    books = pd.read_csv(BOOKS_FILE, dtype=str)
    members = pd.read_csv(MEMBERS_FILE, dtype=str)
    issues = pd.read_csv(ISSUES_FILE, dtype=str)
    for col in ["total","available"]:
        books[col] = pd.to_numeric(books[col], errors="coerce").fillna(0).astype(int)
    return books, members, issues

def save_data(books, members, issues):
    books.to_csv(BOOKS_FILE, index=False)
    members.to_csv(MEMBERS_FILE, index=False)
    issues.to_csv(ISSUES_FILE, index=False)

def valid_text(value, field):
    value = str(value).strip()
    if not value:
        raise ValueError(f"{field} cannot be empty.")
    return value

def next_id(series, prefix):
    nums = []
    for x in series.astype(str):
        try:
            nums.append(int(x.replace(prefix, "")))
        except Exception:
            pass
    return f"{prefix}{max(nums, default=0)+1:03d}"

init_files()
books, members, issues = load_data()

st.set_page_config(page_title="Library Automation Tool", page_icon="📚", layout="wide")
st.title("📚 Library Automation Tool")
st.caption("Python-based practical internship project | Book, member, issue and return management")

menu = st.sidebar.radio("Menu", ["Dashboard", "Books", "Members", "Issue Book", "Return Book", "Reports"])

if menu == "Dashboard":
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("📚 Titles", len(books))
    c2.metric("📖 Available Copies", int(books["available"].sum()) if len(books) else 0)
    c3.metric("👥 Members", len(members))
    c4.metric("📌 Active Issues", int((issues["status"] == "Issued").sum()) if len(issues) else 0)
    st.subheader("Recent Transactions")
    if len(issues):
        st.dataframe(issues.tail(10), use_container_width=True)
    else:
        st.info("No transactions yet. Add books and members first.")

elif menu == "Books":
    st.header("📚 Book Management")
    with st.form("add_book"):
        a,b,c = st.columns(3)
        book_id = a.text_input("Book ID (optional)", placeholder="B001")
        title = b.text_input("Title")
        author = c.text_input("Author")
        d,e = st.columns(2)
        category = d.text_input("Category", "General")
        total = e.number_input("Total Copies", min_value=1, value=1, step=1)
        if st.form_submit_button("Add Book"):
            try:
                title = valid_text(title, "Title")
                author = valid_text(author, "Author")
                category = valid_text(category, "Category")
                book_id = book_id.strip() or next_id(books["book_id"], "B")
                if book_id in books["book_id"].values:
                    raise ValueError("Book ID already exists.")
                row = pd.DataFrame([{"book_id":book_id,"title":title,"author":author,
                                     "category":category,"total":int(total),"available":int(total)}])
                books = pd.concat([books,row], ignore_index=True)
                save_data(books,members,issues)
                st.success(f"Book {book_id} added successfully.")
                st.rerun()
            except ValueError as e:
                st.error(str(e))

    st.subheader("Search Books")
    q = st.text_input("Search by ID, title, author or category")
    view = books.copy()
    if q:
        mask = view.astype(str).apply(lambda col: col.str.contains(q, case=False, na=False))
        view = view[mask.any(axis=1)]
    st.dataframe(view, use_container_width=True)

elif menu == "Members":
    st.header("👥 Member Management")
    with st.form("add_member"):
        a,b = st.columns(2)
        member_id = a.text_input("Member ID (optional)", placeholder="M001")
        name = b.text_input("Name")
        c,d = st.columns(2)
        email = c.text_input("Email")
        phone = d.text_input("Phone")
        if st.form_submit_button("Add Member"):
            try:
                name = valid_text(name, "Name")
                email = valid_text(email, "Email")
                phone = valid_text(phone, "Phone")
                if "@" not in email:
                    raise ValueError("Enter a valid email address.")
                member_id = member_id.strip() or next_id(members["member_id"], "M")
                if member_id in members["member_id"].values:
                    raise ValueError("Member ID already exists.")
                row = pd.DataFrame([{"member_id":member_id,"name":name,"email":email,"phone":phone}])
                members = pd.concat([members,row], ignore_index=True)
                save_data(books,members,issues)
                st.success(f"Member {member_id} added successfully.")
                st.rerun()
            except ValueError as e:
                st.error(str(e))
    st.dataframe(members, use_container_width=True)

elif menu == "Issue Book":
    st.header("📤 Issue a Book")
    available_books = books[books["available"] > 0]
    if available_books.empty:
        st.warning("No books are currently available.")
    elif members.empty:
        st.warning("Add at least one member before issuing a book.")
    else:
        with st.form("issue_form"):
            book_options = available_books["book_id"].tolist()
            member_options = members["member_id"].tolist()
            book_id = st.selectbox("Book", book_options,
                                   format_func=lambda x: f"{x} - {books.loc[books.book_id==x,'title'].iloc[0]}")
            member_id = st.selectbox("Member", member_options,
                                     format_func=lambda x: f"{x} - {members.loc[members.member_id==x,'name'].iloc[0]}")
            issue_date = st.date_input("Issue Date", date.today())
            days = st.number_input("Loan Period (days)", min_value=1, max_value=60, value=14)
            if st.form_submit_button("Issue Book"):
                try:
                    if (issues["status"] == "Issued").any():
                        active = issues[(issues.status=="Issued") & (issues.member_id==member_id)]
                        if len(active) >= 5:
                            raise ValueError("Member already has 5 active books.")
                    issue_id = next_id(issues["issue_id"], "I")
                    due = issue_date + timedelta(days=int(days))
                    row = pd.DataFrame([{"issue_id":issue_id,"book_id":book_id,"member_id":member_id,
                                         "issue_date":issue_date.isoformat(),"due_date":due.isoformat(),
                                         "return_date":"","status":"Issued"}])
                    issues = pd.concat([issues,row], ignore_index=True)
                    books.loc[books["book_id"]==book_id, "available"] -= 1
                    save_data(books,members,issues)
                    st.success(f"Book issued successfully. Due date: {due.isoformat()}")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

elif menu == "Return Book":
    st.header("📥 Return a Book")
    active = issues[issues["status"] == "Issued"]
    if active.empty:
        st.info("No active issued books.")
    else:
        labels = active["issue_id"].tolist()
        with st.form("return_form"):
            issue_id = st.selectbox("Transaction", labels)
            return_date = st.date_input("Return Date", date.today())
            if st.form_submit_button("Return Book"):
                idx = issues.index[issues["issue_id"] == issue_id][0]
                book_id = issues.loc[idx, "book_id"]
                due = date.fromisoformat(issues.loc[idx, "due_date"])
                late_days = max(0, (return_date - due).days)
                issues.loc[idx, "return_date"] = return_date.isoformat()
                issues.loc[idx, "status"] = "Returned"
                books.loc[books["book_id"] == book_id, "available"] += 1
                save_data(books,members,issues)
                if late_days:
                    st.warning(f"Returned successfully. Late by {late_days} day(s).")
                else:
                    st.success("Returned successfully and on time.")
                st.rerun()

elif menu == "Reports":
    st.header("📊 Reports & Data Processing")
    tab1,tab2,tab3 = st.tabs(["All Transactions","Overdue","Inventory"])
    with tab1:
        st.dataframe(issues, use_container_width=True)
        if not issues.empty:
            st.download_button("Download Transactions CSV", issues.to_csv(index=False), "transactions.csv", "text/csv")
    with tab2:
        today = date.today()
        overdue = issues[(issues["status"]=="Issued") & (pd.to_datetime(issues["due_date"], errors="coerce").dt.date < today)]
        st.dataframe(overdue, use_container_width=True)
    with tab3:
        st.dataframe(books, use_container_width=True)
        if not books.empty:
            st.download_button("Download Books CSV", books.to_csv(index=False), "books.csv", "text/csv")

st.sidebar.markdown("---")
st.sidebar.caption("Data is stored locally in the data/ folder.")
