import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta

class LibraryGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Library Management System")
        self.root.geometry("900x600")
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")
        
        # Create tabs
        self.checkout_tab = ttk.Frame(self.notebook)
        self.borrower_tab = ttk.Frame(self.notebook)
        self.newbook_tab = ttk.Frame(self.notebook)
        self.copies_tab = ttk.Frame(self.notebook)
        self.late_tab = ttk.Frame(self.notebook)
        self.search_tab = ttk.Frame(self.notebook)
        
        # Add tabs
        self.notebook.add(self.checkout_tab, text="Book Checkout")
        self.notebook.add(self.borrower_tab, text="New Borrower")
        self.notebook.add(self.newbook_tab, text="Add New Book")
        self.notebook.add(self.copies_tab, text="View Copies")
        self.notebook.add(self.late_tab, text="Late Returns")
        self.notebook.add(self.search_tab, text="Search")
        
        # Setup all tabs
        self.init_checkout_tab()
        self.init_borrower_tab()
        self.init_newbook_tab()
        self.init_copies_tab()
        self.init_late_tab()
        self.init_search_tab()

    def init_checkout_tab(self):
        frame = ttk.LabelFrame(self.checkout_tab, text="Checkout Book")
        frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Book ID
        ttk.Label(frame, text="Book ID:").pack()
        self.book_id = ttk.Entry(frame)
        self.book_id.pack()
        
        # Branch ID
        ttk.Label(frame, text="Branch ID:").pack()
        self.branch_id = ttk.Entry(frame)
        self.branch_id.pack()
        
        # Card Number
        ttk.Label(frame, text="Card Number:").pack()
        self.card_no = ttk.Entry(frame)
        self.card_no.pack()
        
        # Checkout Button
        ttk.Button(frame, text="Check Out", command=self.do_checkout).pack(pady=10)

    def do_checkout(self):
        try:
            conn = sqlite3.connect("library.db")
            cur = conn.cursor()
            date_out = datetime.now().strftime("%Y-%m-%d")
            due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            cur.execute("INSERT INTO BOOK_LOANS (Book_Id, Branch_Id, Card_No, Date_Out, Due_Date) VALUES (?, ?, ?, ?, ?)", 
                       (self.book_id.get(), self.branch_id.get(), self.card_no.get(), date_out, due_date))
            conn.commit()
            messagebox.showinfo("Success", "Book checked out successfully!")
        except sqlite3.Error as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def init_borrower_tab(self):
        frame = ttk.LabelFrame(self.borrower_tab, text="Add New Borrower")
        frame.pack(padx=10, pady=10, fill="both", expand=True)
    
        # Name
        ttk.Label(frame, text="Name:").pack()
        self.borrower_name = ttk.Entry(frame)
        self.borrower_name.pack()
    
        # Address
        ttk.Label(frame, text="Address:").pack()
        self.borrower_address = ttk.Entry(frame)
        self.borrower_address.pack()
            
        # Phone
        ttk.Label(frame, text="Phone:").pack()
        self.borrower_phone = ttk.Entry(frame)
        self.borrower_phone.pack()
        
        # Add Button
        ttk.Button(frame, text="Add Borrower", command=self.add_borrower).pack(pady=10)

    def add_borrower(self):
        try:
            conn = sqlite3.connect("library.db")
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO BORROWER (Name, Address, Phone)
                VALUES (?, ?, ?)
            """, (self.borrower_name.get(), self.borrower_address.get(), self.borrower_phone.get()))
            
            card_no = cur.lastrowid
            
            conn.commit()
            messagebox.showinfo("Success", f"Borrower added successfully!\nCard Number: {card_no}")
            
            # Clear entries
            self.borrower_name.delete(0, tk.END)
            self.borrower_address.delete(0, tk.END)
            self.borrower_phone.delete(0, tk.END)
            
        except sqlite3.Error as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def init_newbook_tab(self):
        frame = ttk.LabelFrame(self.newbook_tab, text="Add New Book")
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Title
        ttk.Label(frame, text="Book Title:").pack()
        self.book_title = ttk.Entry(frame)
        self.book_title.pack()

        # Author
        ttk.Label(frame, text="Author:").pack()
        self.author_name = ttk.Entry(frame)
        self.author_name.pack()

        # Publisher
        ttk.Label(frame, text="Publisher Name:").pack()
        self.publisher_combo = ttk.Combobox(frame)
        self.publisher_combo.pack()
        self.load_publishers()

        # Add Button
        ttk.Button(frame, text="Add Book", command=self.add_book).pack(pady=10)

    def load_publishers(self):
        try:
            conn = sqlite3.connect("library.db")
            cur = conn.cursor()
            cur.execute("SELECT Publisher_Name FROM PUBLISHER")
            publishers = [row[0] for row in cur.fetchall()]
            self.publisher_combo['values'] = publishers
        except sqlite3.Error as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def add_book(self):
        try:
            conn = sqlite3.connect("library.db")
            cur = conn.cursor()

            # Get the next available Book_Id
            cur.execute("SELECT MAX(Book_Id) FROM BOOK")
            max_id = cur.fetchone()[0]
            new_book_id = 1 if max_id is None else max_id + 1

            # Insert the book
            cur.execute("""
                INSERT INTO BOOK (Book_Id, Title, Publisher_Name)
                VALUES (?, ?, ?)
            """, (new_book_id, self.book_title.get(), self.publisher_combo.get()))

            # Insert the author
            cur.execute("""
                INSERT INTO BOOK_AUTHORS (Book_Id, Author_Name)
                VALUES (?, ?)
            """, (new_book_id, self.author_name.get()))

            # Add 5 copies to each branch
            cur.execute("SELECT Branch_Id FROM LIBRARY_BRANCH")
            branches = cur.fetchall()
            for branch in branches:
                cur.execute("""
                    INSERT INTO BOOK_COPIES (Book_Id, Branch_Id, No_Of_Copies)
                    VALUES (?, ?, 5)
                """, (new_book_id, branch[0]))

            conn.commit()
            messagebox.showinfo("Success", "Book added successfully to all branches!")

            # Clear entries
            self.book_title.delete(0, tk.END)
            self.author_name.delete(0, tk.END)
            self.publisher_combo.set('')

        except sqlite3.Error as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def init_copies_tab(self):
        frame = ttk.LabelFrame(self.copies_tab, text="View Book Copies")
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Book Title Entry
        ttk.Label(frame, text="Enter Book Title:").pack()
        self.title_search = ttk.Entry(frame)
        self.title_search.pack()

        # Search Button
        ttk.Button(frame, text="Search", command=self.find_copies).pack(pady=10)

        # Create Treeview for results
        columns = ('Branch', 'Total Copies', 'Copies Loaned')
        self.copies_tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        # Set column headings
        for col in columns:
            self.copies_tree.heading(col, text=col)
            self.copies_tree.column(col, width=150)
        
        self.copies_tree.pack(pady=10, fill='both', expand=True)

    def find_copies(self):
        try:
            # Clear previous results
            for item in self.copies_tree.get_children():
                self.copies_tree.delete(item)

            conn = sqlite3.connect('library.db')
            cur = conn.cursor()
            
            title = f"%{self.title_search.get()}%"
            
            cur.execute("""
                SELECT 
                    LB.Branch_Name,
                    BC.No_Of_Copies as Total_Copies,
                    COUNT(BL.Book_Id) as Copies_Loaned
                FROM BOOK B
                JOIN BOOK_COPIES BC ON B.Book_Id = BC.Book_Id
                JOIN LIBRARY_BRANCH LB ON BC.Branch_Id = LB.Branch_Id
                LEFT JOIN BOOK_LOANS BL ON B.Book_Id = BL.Book_Id 
                    AND BC.Branch_Id = BL.Branch_Id
                    AND BL.Returned_date IS NULL
                WHERE B.Title LIKE ?
                GROUP BY LB.Branch_Name, BC.No_Of_Copies
                ORDER BY LB.Branch_Name
            """, (title,))

            results = cur.fetchall()
            if not results:
                messagebox.showinfo("No Results", "No copies found for this book title.")
            else:
                for row in results:
                    self.copies_tree.insert('', 'end', values=row)

        except sqlite3.Error as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def init_late_tab(self):
        frame = ttk.LabelFrame(self.late_tab, text="View Late Returns")
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Date Range Entries
        date_frame = ttk.Frame(frame)
        date_frame.pack(pady=10)

        ttk.Label(date_frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5)
        self.start_date = ttk.Entry(date_frame)
        self.start_date.grid(row=0, column=1, padx=5)

        ttk.Label(date_frame, text="End Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5)
        self.end_date = ttk.Entry(date_frame)
        self.end_date.grid(row=1, column=1, padx=5)

        # Search Button
        ttk.Button(frame, text="Find Late Returns", command=self.find_late_returns).pack(pady=10)

        # Create Treeview for results
        columns = ('Title', 'Borrower', 'Due Date', 'Returned Date', 'Days Late')
        self.late_tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        # Set column headings
        for col in columns:
            self.late_tree.heading(col, text=col)
            self.late_tree.column(col, width=120)
        
        self.late_tree.pack(pady=10, fill='both', expand=True)

    def find_late_returns(self):
        try:
            # Clear previous results
            for item in self.late_tree.get_children():
                self.late_tree.delete(item)

            conn = sqlite3.connect('library.db')
            cur = conn.cursor()
            
            cur.execute("""
                SELECT 
                    B.Title,
                    BR.Name,
                    BL.Due_Date,
                    BL.Returned_date,
                    CAST(julianday(BL.Returned_date) - julianday(BL.Due_Date) AS INTEGER) as Days_Late
                FROM BOOK_LOANS BL
                JOIN BOOK B ON BL.Book_Id = B.Book_Id
                JOIN BORROWER BR ON BL.Card_No = BR.Card_No
                WHERE BL.Returned_date > BL.Due_Date
                AND BL.Due_Date BETWEEN ? AND ?
                ORDER BY Days_Late DESC
            """, (self.start_date.get(), self.end_date.get()))

            results = cur.fetchall()
            if not results:
                messagebox.showinfo("No Results", "No late returns found in this date range.")
            else:
                for row in results:
                    self.late_tree.insert('', 'end', values=row)

        except sqlite3.Error as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def init_search_tab(self):
        frame = ttk.LabelFrame(self.search_tab, text="Search Library")
        frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Create notebook for sub-tabs
        search_notebook = ttk.Notebook(frame)
        search_notebook.pack(expand=True, fill="both")

        # Create sub-tabs for borrower and book searches
        borrower_tab = ttk.Frame(search_notebook)
        book_tab = ttk.Frame(search_notebook)
        search_notebook.add(borrower_tab, text="Search Borrowers")
        search_notebook.add(book_tab, text="Search Books")

        # Borrower Search Section
        ttk.Label(borrower_tab, text="Search by (ID, Name, or partial name):").pack(pady=5)
        self.borrower_search = ttk.Entry(borrower_tab)
        self.borrower_search.pack(pady=5)
        ttk.Button(borrower_tab, text="Search Borrowers", command=self.search_borrowers).pack(pady=5)

        # Borrower Results Treeview
        columns = ('ID', 'Name', 'Late Fee Balance')
        self.borrower_tree = ttk.Treeview(borrower_tab, columns=columns, show='headings')
        for col in columns:
            self.borrower_tree.heading(col, text=col)
            self.borrower_tree.column(col, width=150)
        self.borrower_tree.pack(pady=10, fill='both', expand=True)

        # Book Search Section
        ttk.Label(book_tab, text="Search by (Book ID, Title, or partial title):").pack(pady=5)
        self
        self.book_search = ttk.Entry(book_tab)
        self.book_search.pack(pady=5)
        ttk.Label(book_tab, text="Borrower ID (optional):").pack(pady=5)
        self.book_borrower_id = ttk.Entry(book_tab)
        self.book_borrower_id.pack(pady=5)
        ttk.Button(book_tab, text="Search Books", command=self.search_books).pack(pady=5)

        # Book Results Treeview
        columns = ('Title', 'Borrower', 'Due Date', 'Late Fee')
        self.book_tree = ttk.Treeview(book_tab, columns=columns, show='headings')
        for col in columns:
            self.book_tree.heading(col, text=col)
            self.book_tree.column(col, width=150)
        self.book_tree.pack(pady=10, fill='both', expand=True)

    def search_borrowers(self):
        try:
            # Clear previous results
            for item in self.borrower_tree.get_children():
                self.borrower_tree.delete(item)

            conn = sqlite3.connect('library.db')
            cur = conn.cursor()
            search_term = f"%{self.borrower_search.get()}%"
            
            cur.execute("""
                SELECT 
                    BR.Card_No,
                    BR.Name,
                    COALESCE(SUM(
                        CASE 
                            WHEN BL.Returned_date > BL.Due_Date 
                            THEN (julianday(BL.Returned_date) - julianday(BL.Due_Date)) * LB.LateFee
                            ELSE 0 
                        END
                    ), 0) as TotalLateFees
                FROM BORROWER BR
                LEFT JOIN BOOK_LOANS BL ON BR.Card_No = BL.Card_No
                LEFT JOIN LIBRARY_BRANCH LB ON BL.Branch_Id = LB.Branch_Id
                WHERE BR.Card_No LIKE ? OR BR.Name LIKE ?
                GROUP BY BR.Card_No, BR.Name
                ORDER BY TotalLateFees DESC
            """, (search_term, search_term))

            results = cur.fetchall()
            if not results:
                messagebox.showinfo("No Results", "No borrowers found.")
            else:
                for row in results:
                    formatted_fee = f"${row[2]:.2f}"
                    self.borrower_tree.insert('', 'end', values=(row[0], row[1], formatted_fee))

        except sqlite3.Error as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def search_books(self):
        try:
            # Clear previous results
            for item in self.book_tree.get_children():
                self.book_tree.delete(item)

            conn = sqlite3.connect('library.db')
            cur = conn.cursor()
            search_term = f"%{self.book_search.get()}%"
            borrower_id = self.book_borrower_id.get()

            query = """
                SELECT 
                    B.Title,
                    BR.Name,
                    BL.Due_Date,
                    CASE 
                        WHEN BL.Returned_date > BL.Due_Date 
                        THEN (julianday(BL.Returned_date) - julianday(BL.Due_Date)) * LB.LateFee
                        ELSE NULL
                    END as LateFee
                FROM BOOK B
                JOIN BOOK_LOANS BL ON B.Book_Id = BL.Book_Id
                JOIN BORROWER BR ON BL.Card_No = BR.Card_No
                JOIN LIBRARY_BRANCH LB ON BL.Branch_Id = LB.Branch_Id
                WHERE (B.Book_Id LIKE ? OR B.Title LIKE ?)
            """
            
            params = [search_term, search_term]
            if borrower_id:
                query += " AND BR.Card_No = ?"
                params.append(borrower_id)
                
            query += " ORDER BY LateFee DESC NULLS LAST"
            
            cur.execute(query, params)
            results = cur.fetchall()
            
            if not results:
                messagebox.showinfo("No Results", "No books found.")
            else:
                for row in results:
                    late_fee = f"${row[3]:.2f}" if row[3] is not None else "Non-Applicable"
                    self.book_tree.insert('', 'end', values=(row[0], row[1], row[2], late_fee))

        except sqlite3.Error as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.close()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = LibraryGUI()
    app.run()
