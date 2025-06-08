import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, timedelta
from fpdf import FPDF
import os
import shutil
import webbrowser

class GoldShopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Management System ❤️ Created by Enzoha6ks ❤️")
        self.root.geometry("1100x750")
        
        # Setup database
        self.db_path = "gold.db"
        self.setup_database()
        
        # Style configuration
        self.setup_styles()
        
        # Create GUI
        self.create_main_frame()
        self.create_menu()
        self.create_tabs()
        
        # Load initial data
        self.load_orders()
        self.load_inventory()
        self.load_clients()
        
        # Center the window
        self.center_window()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", background="#ccc")
        style.configure("Title.TLabel", font=('Helvetica', 12, 'bold'))
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
        style.configure("Accent.TButton", background="#4CAF50", foreground="white")
    
    def setup_database(self):
        """Initialize database and create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Orders table
        c.execute('''CREATE TABLE IF NOT EXISTS orders
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER,
                    description TEXT,
                    estimated_weight REAL,
                    actual_weight REAL,
                    purity REAL,
                    order_date TEXT,
                    delivery_date TEXT,
                    status TEXT,
                    price_per_gm REAL,
                    making_charges REAL,
                    FOREIGN KEY(client_id) REFERENCES clients(id))''')
        
        # Clients table
        c.execute('''CREATE TABLE IF NOT EXISTS clients
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    phone TEXT,
                    address TEXT,
                    created_date TEXT)''')
        
        # Inventory table
        c.execute('''CREATE TABLE IF NOT EXISTS inventory
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    transaction_type TEXT,
                    weight REAL,
                    purity REAL,
                    date TEXT,
                    notes TEXT,
                    price_per_gm REAL,
                    client_id INTEGER REFERENCES clients(id))''')
        
        # Daily rates table
        c.execute('''CREATE TABLE IF NOT EXISTS rates
                    (date TEXT PRIMARY KEY,
                    gold_rate REAL,
                    silver_rate REAL)''')
        
        # Order items table
        c.execute('''CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            description TEXT,
            weight REAL,
            purity REAL,
            rate REAL,
            amount REAL,
            FOREIGN KEY(order_id) REFERENCES orders(id)
        )''')
        
        # Insert default rates if none exist
        c.execute("SELECT COUNT(*) FROM rates")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO rates (date, gold_rate, silver_rate) VALUES (?, ?, ?)",
                     (datetime.now().strftime("%Y-%m-%d"), 5000, 60))
        
        conn.commit()
        conn.close()
    
    def create_main_frame(self):
        """Create the main container frame"""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_menu(self):
        """Create the menu bar"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Backup Database", command=self.backup_database)
        file_menu.add_command(label="Restore Database", command=self.restore_database)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Set Today's Rates", command=self.set_rates)
        tools_menu.add_command(label="Calculate Gold Value", command=self.calculate_gold_value)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # Reports menu
        reports_menu = tk.Menu(menubar, tearoff=0)
        reports_menu.add_command(label="Daily Summary", command=self.generate_daily_summary)
        reports_menu.add_command(label="Inventory Report", command=self.generate_inventory_report)
        reports_menu.add_command(label="Client Orders", command=self.generate_client_orders_report)
        menubar.add_cascade(label="Reports", menu=reports_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def backup_database(self):
        """Create a backup of the database file"""
        backup_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")],
            initialfile=f"gold_shop_backup_{datetime.now().strftime('%Y%m%d')}.db"
        )
        if backup_path:
            try:
                shutil.copy2(self.db_path, backup_path)
                messagebox.showinfo("Success", f"Database backed up to:\n{backup_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Backup failed:\n{str(e)}")
    
    def restore_database(self):
        """Restore database from backup"""
        backup_path = filedialog.askopenfilename(
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        if backup_path:
            try:
                # Close any existing connections
                if hasattr(self, 'conn'):
                    self.conn.close()
                
                shutil.copy2(backup_path, self.db_path)
                messagebox.showinfo("Success", "Database restored successfully!\nPlease restart the application.")
                self.root.quit()
            except Exception as e:
                messagebox.showerror("Error", f"Restore failed:\n{str(e)}")
    
    def set_rates(self):
        """Set gold/silver rates"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Today's Rates")
        dialog.grab_set()
        
        # Get current rates
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT gold_rate, silver_rate FROM rates ORDER BY date DESC LIMIT 1")
        current_rates = c.fetchone() or (5000, 60)
        conn.close()
        
        ttk.Label(dialog, text="Gold Rate (per gram):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        gold_rate_entry = ttk.Entry(dialog)
        gold_rate_entry.grid(row=0, column=1, padx=5, pady=5)
        gold_rate_entry.insert(0, current_rates[0])
        
        ttk.Label(dialog, text="Silver Rate (per gram):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        silver_rate_entry = ttk.Entry(dialog)
        silver_rate_entry.grid(row=1, column=1, padx=5, pady=5)
        silver_rate_entry.insert(0, current_rates[1])
        
        def save_rates():
            try:
                gold_rate = float(gold_rate_entry.get())
                silver_rate = float(silver_rate_entry.get())
                today = datetime.now().strftime("%Y-%m-%d")  # <-- Add this line

                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                c.execute("SELECT 1 FROM rates WHERE date = ?", (today,))
                if c.fetchone():
                    c.execute("UPDATE rates SET gold_rate = ?, silver_rate = ? WHERE date = ?", (gold_rate, silver_rate, today))
                else:
                    c.execute("INSERT INTO rates (date, gold_rate, silver_rate) VALUES (?, ?, ?)", (today, gold_rate, silver_rate))
                conn.commit()
                conn.close()

                messagebox.showinfo("Success", "Rates updated successfully!")
                dialog.destroy()
                self.load_dashboard_data()
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for rates")
        
        ttk.Button(dialog, text="Save", command=save_rates).grid(row=2, column=0, columnspan=2, pady=10)
    
    def calculate_gold_value(self):
        """Calculate gold value based on weight and purity"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Calculate Gold Value")
        dialog.grab_set()
        
        # Get current gold rate
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT gold_rate FROM rates ORDER BY date DESC LIMIT 1")
        row = c.fetchone()
        current_rate = row[0] if row else 5000
        conn.close()
        
        ttk.Label(dialog, text="Weight (grams):").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        weight_entry = ttk.Entry(dialog)
        weight_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="Purity (e.g. 0.999 for 24k):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        purity_entry = ttk.Entry(dialog)
        purity_entry.grid(row=1, column=1, padx=5, pady=5)
        purity_entry.insert(0, "0.999")
        
        ttk.Label(dialog, text=f"Current Gold Rate: KWD{current_rate}/g").grid(row=2, column=0, columnspan=2, pady=5)
        
        result_label = ttk.Label(dialog, text="Value: KWD0.00", font=('Helvetica', 10, 'bold'))
        result_label.grid(row=4, column=0, columnspan=2, pady=5)
        
        def calculate():
            try:
                weight = float(weight_entry.get())
                purity = float(purity_entry.get())
                value = weight * purity * current_rate
                result_label.config(text=f"Value: KWD{value:,.2f}")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numbers for weight and purity")
        
        ttk.Button(dialog, text="Calculate", command=calculate).grid(row=3, column=0, columnspan=2, pady=10)
    
    def generate_daily_summary(self):
        """Generate daily summary report"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get today's date
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Get today's orders
        c.execute('''SELECT COUNT(*), SUM(actual_weight) 
                     FROM orders 
                     WHERE order_date = ? AND status != 'Cancelled' ''', (today,))
        order_count, total_weight = c.fetchone()
        order_count = order_count or 0
        total_weight = total_weight or 0
        
        # Get today's transactions
        c.execute('''SELECT 
                     SUM(CASE WHEN transaction_type = 'received' THEN weight ELSE 0 END),
                     SUM(CASE WHEN transaction_type = 'issued' THEN weight ELSE 0 END)
                     FROM inventory WHERE date = ?''', (today,))
        received, issued = c.fetchone()
        received = received or 0
        issued = issued or 0
        
        # Get current rates
        c.execute("SELECT gold_rate FROM rates ORDER BY date DESC LIMIT 1")
        gold_rate = c.fetchone()[0] if c.fetchone() else 0
        
        conn.close()
        
        # Create PDF report
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Title
        pdf.cell(200, 10, txt=f"Daily Summary Report - {today}", ln=1, align='C')
        pdf.ln(10)
        
        # Orders summary
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Orders Summary", ln=1)
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt=f"Total Orders: {order_count}", ln=1)
        pdf.cell(200, 10, txt=f"Total Gold Weight: {total_weight:.2f}g", ln=1)
        pdf.cell(200, 10, txt=f"Estimated Value: KWD{total_weight * gold_rate:,.2f}", ln=1)
        pdf.ln(5)
        
        # Inventory summary
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Inventory Summary", ln=1)
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt=f"Gold Received: {received:.2f}g", ln=1)
        pdf.cell(200, 10, txt=f"Gold Issued: {issued:.2f}g", ln=1)
        pdf.cell(200, 10, txt=f"Net Change: {received - issued:.2f}g", ln=1)
        pdf.ln(10)
        
        # Save the PDF
        report_path = f"daily_summary_{today}.pdf"
        pdf.output(report_path)
        
        # Show success message
        messagebox.showinfo("Success", f"Daily summary report generated:\n{os.path.abspath(report_path)}")
        webbrowser.open(report_path)
    
    def generate_inventory_report(self):
        """Generate inventory report"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get inventory data
        c.execute('''SELECT date, transaction_type, weight, purity, price_per_gm, notes 
                     FROM inventory ORDER BY date DESC''')
        inventory_data = c.fetchall()
        
        # Get current stock
        c.execute('''SELECT 
                     SUM(CASE WHEN transaction_type = 'received' THEN weight ELSE 0 END),
                     SUM(CASE WHEN transaction_type = 'issued' THEN weight ELSE 0 END)
                     FROM inventory''')
        received, issued = c.fetchone()
        current_stock = (received or 0) - (issued or 0)
        
        conn.close()
        
        # Create PDF report
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Title
        pdf.cell(200, 10, txt="Gold Inventory Report", ln=1, align='C')
        pdf.ln(10)
        
        # Current stock
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=f"Current Gold Stock: {current_stock:.2f}g", ln=1)
        pdf.ln(10)
        
        # Transactions table
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(30, 10, "Date", 1)
        pdf.cell(25, 10, "Type", 1)
        pdf.cell(25, 10, "Weight (g)", 1)
        pdf.cell(25, 10, "Purity", 1)
        pdf.cell(30, 10, "Rate (KWD/g)", 1)
        pdf.cell(60, 10, "Notes", 1, ln=1)
        
        pdf.set_font("Arial", size=8)
        for row in inventory_data:
            pdf.cell(30, 10, row[0], 1)
            pdf.cell(25, 10, row[1].capitalize(), 1)
            pdf.cell(25, 10, f"{row[2]:.2f}", 1)
            pdf.cell(25, 10, f"{row[3]:.3f}", 1)
            pdf.cell(30, 10, f"{row[4]:.2f}" if row[4] else "N/A", 1)
            pdf.cell(60, 10, row[5] or "", 1, ln=1)
        
        # Save the PDF
        report_path = "inventory_report.pdf"
        pdf.output(report_path)
        
        # Show success message
        messagebox.showinfo("Success", f"Inventory report generated:\n{os.path.abspath(report_path)}")
        webbrowser.open(report_path)
    
    def generate_client_orders_report(self):
        """Generate client orders report"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get client orders data
        c.execute('''SELECT clients.name, clients.phone, 
                     COUNT(orders.id), SUM(orders.actual_weight)
                     FROM clients LEFT JOIN orders ON clients.id = orders.client_id
                     GROUP BY clients.id ORDER BY clients.name''')
        client_data = c.fetchall()
        
        conn.close()
        
        # Create PDF report
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Title
        pdf.cell(200, 10, txt="Client Orders Report", ln=1, align='C')
        pdf.ln(10)
        
        # Clients table
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(80, 10, "Client Name", 1)
        pdf.cell(40, 10, "Phone", 1)
        pdf.cell(30, 10, "Total Orders", 1)
        pdf.cell(40, 10, "Total Gold (g)", 1, ln=1)
        
        pdf.set_font("Arial", size=8)
        for row in client_data:
            pdf.cell(80, 10, row[0], 1)
            pdf.cell(40, 10, row[1] or "", 1)
            pdf.cell(30, 10, str(row[2]), 1)
            pdf.cell(40, 10, f"{row[3]:.2f}" if row[3] else "0.00", 1, ln=1)
        
        # Save the PDF
        report_path = "client_orders_report.pdf"
        pdf.output(report_path)
        
        # Show success message
        messagebox.showinfo("Success", f"Client orders report generated:\n{os.path.abspath(report_path)}")
        webbrowser.open(report_path)
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo("About", 
                          "❤️ Created by  ❤️ \n\n"
                          "Version 1.0\n"
                          "© 2025 \n\n"
                          "Manage orders, inventory, and clients for gold shop business.")
    
    def create_tabs(self):
        """Create the notebook with tabs"""
        self.notebook = ttk.Notebook(self.main_frame)
        
        # Create tabs
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.orders_tab = ttk.Frame(self.notebook)
        self.inventory_tab = ttk.Frame(self.notebook)
        self.clients_tab = ttk.Frame(self.notebook)
        self.invoices_tab = ttk.Frame(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.orders_tab, text="Orders")
        self.notebook.add(self.inventory_tab, text="Inventory")
        self.notebook.add(self.clients_tab, text="Clients")
        self.notebook.add(self.invoices_tab, text="Invoices")
        
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Build each tab
        self.build_dashboard_tab()
        self.build_orders_tab()
        self.build_inventory_tab()
        self.build_clients_tab()
        self.build_invoices_tab()
    
    def build_dashboard_tab(self):
        """Build the dashboard tab"""
        # Current rates frame
        rates_frame = ttk.LabelFrame(self.dashboard_tab, text="Today's Rates", padding=10)
        rates_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(rates_frame, text="Gold Rate (per gram):").grid(row=0, column=0, sticky=tk.E, padx=5, pady=2)
        self.gold_rate_label = ttk.Label(rates_frame, text="Loading...", font=('Helvetica', 10, 'bold'))
        self.gold_rate_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Label(rates_frame, text="Silver Rate (per gram):").grid(row=1, column=0, sticky=tk.E, padx=5, pady=2)
        self.silver_rate_label = ttk.Label(rates_frame, text="Loading...", font=('Helvetica', 10, 'bold'))
        self.silver_rate_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        ttk.Button(rates_frame, text="Update Rates", command=self.set_rates, 
                  style="Accent.TButton").grid(row=0, column=2, rowspan=2, padx=10)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(self.dashboard_tab, text="Quick Stats", padding=10)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        stats = [
            ("Total Orders", "orders_count"),
            ("Pending Orders", "pending_orders"),
            ("Gold in Stock (grams)", "gold_stock"),
            ("Active Clients", "clients_count")
        ]
        
        for i, (label, var) in enumerate(stats):
            ttk.Label(stats_frame, text=label+":").grid(row=i//2, column=(i%2)*2, sticky=tk.E, padx=5, pady=2)
            label = ttk.Label(stats_frame, text="0", font=('Helvetica', 10, 'bold'))
            label.grid(row=i//2, column=(i%2)*2+1, sticky=tk.W, padx=5, pady=2)
            setattr(self, f"dashboard_{var}_label", label)
        
        # Recent orders frame
        recent_orders_frame = ttk.LabelFrame(self.dashboard_tab, text="Recent Orders", padding=10)
        recent_orders_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("id", "client", "description", "status", "order_date")
        self.recent_orders_tree = ttk.Treeview(recent_orders_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.recent_orders_tree.heading(col, text=col.capitalize())
            self.recent_orders_tree.column(col, width=100 if col != "description" else 200)
        
        scrollbar = ttk.Scrollbar(recent_orders_frame, orient=tk.VERTICAL, command=self.recent_orders_tree.yview)
        self.recent_orders_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.recent_orders_tree.pack(fill=tk.BOTH, expand=True)
        
        # Load dashboard data
        self.load_dashboard_data()
    
    def load_dashboard_data(self):
        """Load data for dashboard"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Load current rates
        c.execute("SELECT gold_rate, silver_rate FROM rates ORDER BY date DESC LIMIT 1")
        rates = c.fetchone()
        if rates:
            self.gold_rate_label.config(text=f"KWD{rates[0]:.2f}")
            self.silver_rate_label.config(text=f"KWD{rates[1]:.2f}")
        
        # Load stats
        c.execute("SELECT COUNT(*) FROM orders")
        self.dashboard_orders_count_label.config(text=c.fetchone()[0])
        
        c.execute("SELECT COUNT(*) FROM orders WHERE status='Pending'")
        self.dashboard_pending_orders_label.config(text=c.fetchone()[0])
        
        c.execute("SELECT SUM(weight) FROM inventory WHERE transaction_type='received'")
        received = c.fetchone()[0] or 0
        c.execute("SELECT SUM(weight) FROM inventory WHERE transaction_type='issued'")
        issued = c.fetchone()[0] or 0
        self.dashboard_gold_stock_label.config(text=f"{received - issued:.2f}")
        
        c.execute("SELECT COUNT(*) FROM clients")
        self.dashboard_clients_count_label.config(text=c.fetchone()[0])
        
        # Load recent orders
        self.recent_orders_tree.delete(*self.recent_orders_tree.get_children())
        c.execute('''SELECT orders.id, clients.name, orders.description, orders.status, orders.order_date
                     FROM orders LEFT JOIN clients ON orders.client_id = clients.id
                     ORDER BY orders.order_date DESC LIMIT 10''')
        for row in c.fetchall():
            self.recent_orders_tree.insert("", tk.END, values=row)
        
        conn.close()
    
    def build_orders_tab(self):
        """Build the orders management tab"""
        # Frame for controls
        controls_frame = ttk.Frame(self.orders_tab)
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Buttons
        ttk.Button(controls_frame, text="Add New Order", command=self.add_order, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Edit Order", command=self.edit_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Delete Order", command=self.delete_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Generate Invoice", command=self.generate_invoice_from_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Refresh", command=self.load_orders).pack(side=tk.LEFT, padx=5)
        
        # Search frame
        search_frame = ttk.Frame(self.orders_tab)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.order_search_entry = ttk.Entry(search_frame, width=30)
        self.order_search_entry.pack(side=tk.LEFT, padx=5)
        self.order_search_entry.bind("<KeyRelease>", lambda e: self.search_orders())
        
        ttk.Button(search_frame, text="Clear", command=self.clear_order_search).pack(side=tk.LEFT, padx=5)
        
        # Treeview for orders
        columns = ("id", "client", "description", "estimated", "actual", "purity", "order_date", "delivery", "status")
        self.orders_tree = ttk.Treeview(self.orders_tab, columns=columns, show="headings", selectmode="browse")
        
        # Configure columns
        self.orders_tree.heading("id", text="ID")
        self.orders_tree.heading("client", text="Client")
        self.orders_tree.heading("description", text="Description")
        self.orders_tree.heading("estimated", text="Est. Weight (g)")
        self.orders_tree.heading("actual", text="Act. Weight (g)")
        self.orders_tree.heading("purity", text="Purity")
        self.orders_tree.heading("order_date", text="Order Date")
        self.orders_tree.heading("delivery", text="Delivery Date")
        self.orders_tree.heading("status", text="Status")
        
        self.orders_tree.column("id", width=50, anchor=tk.CENTER)
        self.orders_tree.column("client", width=150)
        self.orders_tree.column("description", width=200)
        self.orders_tree.column("estimated", width=80, anchor=tk.E)
        self.orders_tree.column("actual", width=80, anchor=tk.E)
        self.orders_tree.column("purity", width=80, anchor=tk.E)
        self.orders_tree.column("order_date", width=100)
        self.orders_tree.column("delivery", width=100)
        self.orders_tree.column("status", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.orders_tab, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.orders_tree.pack(fill=tk.BOTH, expand=True)
    
    def search_orders(self):
        """Search orders based on search term"""
        search_term = self.order_search_entry.get().strip()
        if not search_term:
            self.load_orders()
            return
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        query = '''SELECT orders.id, clients.name, orders.description, 
                  orders.estimated_weight, orders.actual_weight, orders.purity,
                  orders.order_date, orders.delivery_date, orders.status
                  FROM orders
                  LEFT JOIN clients ON orders.client_id = clients.id
                  WHERE clients.name LIKE ? OR orders.description LIKE ? OR orders.status LIKE ?
                  ORDER BY orders.order_date DESC'''
        
        search_param = f"%{search_term}%"
        c.execute(query, (search_param, search_param, search_param))
        
        self.orders_tree.delete(*self.orders_tree.get_children())
        for row in c.fetchall():
            self.orders_tree.insert("", tk.END, values=row)
        
        conn.close()
    
    def clear_order_search(self):
        """Clear order search and reload all orders"""
        self.order_search_entry.delete(0, tk.END)
        self.load_orders()
    
    def load_orders(self):
        """Load orders from database into the treeview"""
        self.orders_tree.delete(*self.orders_tree.get_children())
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''SELECT orders.id, clients.name, orders.description, 
                    orders.estimated_weight, orders.actual_weight, orders.purity,
                    orders.order_date, orders.delivery_date, orders.status
                    FROM orders
                    LEFT JOIN clients ON orders.client_id = clients.id
                    ORDER BY orders.order_date DESC''')
        
        for row in c.fetchall():
            self.orders_tree.insert("", tk.END, values=row)
        
        conn.close()
    
    def add_order(self):
        """Open dialog to add a new order"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Order")
        dialog.grab_set()
        
        # Client selection
        ttk.Label(dialog, text="Client:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        client_var = tk.StringVar()
        client_combobox = ttk.Combobox(dialog, textvariable=client_var)
        client_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Get client names for combobox
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, name FROM clients ORDER BY name")
        clients = c.fetchall()
        client_combobox['values'] = [f"{name} (ID:{id})" for id, name in clients]
        conn.close()
        
        # Order details
        ttk.Label(dialog, text="Description:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        desc_entry = ttk.Entry(dialog, width=40)
        desc_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Estimated Weight (g):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        est_weight_entry = ttk.Entry(dialog)
        est_weight_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Purity:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        purity_entry = ttk.Entry(dialog)
        purity_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        purity_entry.insert(0, "0.999")  # Default 24k purity
        
        ttk.Label(dialog, text="Delivery Date:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.E)
        delivery_entry = ttk.Entry(dialog)
        delivery_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        delivery_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Label(dialog, text="Status:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.E)
        status_combobox = ttk.Combobox(dialog, values=["Pending", "In Progress", "Completed", "Delivered", "Cancelled"])
        status_combobox.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
        status_combobox.set("Pending")
        
        # Price and making charges
        ttk.Label(dialog, text="Price per gram (KWD):").grid(row=6, column=0, padx=5, pady=5, sticky=tk.E)
        price_entry = ttk.Entry(dialog)
        price_entry.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Making charges (KWD):").grid(row=7, column=0, padx=5, pady=5, sticky=tk.E)
        making_charges_entry = ttk.Entry(dialog)
        making_charges_entry.grid(row=7, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Items section
        items = []

        def add_item():
            desc = item_desc_entry.get()
            weight = item_weight_entry.get()
            purity = item_purity_entry.get()
            rate = item_rate_entry.get()
            amount = float(weight) * float(rate) if weight and rate else 0
            items.append((desc, weight, purity, rate, amount))
            items_listbox.insert(tk.END, f"{desc} | {weight}g | {purity} | {rate} | {amount}")
            item_desc_entry.delete(0, tk.END)
            item_weight_entry.delete(0, tk.END)
            item_purity_entry.delete(0, tk.END)
            item_rate_entry.delete(0, tk.END)

        ttk.Label(dialog, text="Item Description:").grid(row=9, column=0)
        item_desc_entry = ttk.Entry(dialog)
        item_desc_entry.grid(row=9, column=1)
        ttk.Label(dialog, text="Weight:").grid(row=10, column=0)
        item_weight_entry = ttk.Entry(dialog)
        item_weight_entry.grid(row=10, column=1)
        ttk.Label(dialog, text="Purity:").grid(row=11, column=0)
        item_purity_entry = ttk.Entry(dialog)
        item_purity_entry.grid(row=11, column=1)
        ttk.Label(dialog, text="Rate:").grid(row=12, column=0)
        item_rate_entry = ttk.Entry(dialog)
        item_rate_entry.grid(row=12, column=1)
        ttk.Button(dialog, text="Add Item", command=add_item).grid(row=13, column=0, columnspan=2)

        items_listbox = tk.Listbox(dialog, width=60)
        items_listbox.grid(row=14, column=0, columnspan=2)
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=8, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Save", command=lambda: self.save_order(
            client_var.get(),
            desc_entry.get(),
            est_weight_entry.get(),
            purity_entry.get(),
            delivery_entry.get(),
            status_combobox.get(),
            price_entry.get(),
            making_charges_entry.get(),
            items,
            dialog
        )).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_order(self, client, description, est_weight, purity, delivery_date, status, price_per_gm, making_charges, items, dialog):
        """Save new order to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            c.execute("SELECT gold_rate, silver_rate FROM rates ORDER BY date DESC LIMIT 1")
            row = c.fetchone()
            current_rates = row if row else (5000, 60)

            if "(ID:" not in client:
                messagebox.showerror("Error", "Please select a client.")
                return

            # Extract client ID from combobox text
            client_id = int(client.split("(ID:")[1].rstrip(")"))

            c.execute('''INSERT INTO orders 
                        (client_id, description, estimated_weight, actual_weight, purity, order_date, delivery_date, status, price_per_gm, making_charges)
                        VALUES (?, ?, ?, NULL, ?, ?, ?, ?, ?, ?)''',
                    (client_id, description, float(est_weight), float(purity), 
                     datetime.now().strftime("%Y-%m-%d"), delivery_date, status, 
                     float(price_per_gm) if price_per_gm else None,
                     float(making_charges) if making_charges else None))

            # Get the last inserted order ID
            order_id = c.lastrowid
            for desc, weight, purity, rate, amount in items:
                c.execute('''INSERT INTO order_items (order_id, description, weight, purity, rate, amount)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (order_id, desc, weight, purity, rate, amount))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Order added successfully!")
            dialog.destroy()
            self.load_orders()
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save order: {str(e)}")
    
    def edit_order(self):
        """Edit selected order"""
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an order to edit")
            return
        
        order_id = self.orders_tree.item(selected[0], "values")[0]
        
        # Fetch order details
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''SELECT orders.*, clients.name 
                     FROM orders 
                     LEFT JOIN clients ON orders.client_id = clients.id
                     WHERE orders.id = ?''', (order_id,))
        order = c.fetchone()
        conn.close()
        
        if not order:
            messagebox.showerror("Error", "Order not found")
            return
        
        # Open edit dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Order")
        dialog.grab_set()
        
        # Client selection
        ttk.Label(dialog, text="Client:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        client_var = tk.StringVar(value=f"{order[11]} (ID:{order[1]})")
        client_combobox = ttk.Combobox(dialog, textvariable=client_var, state="readonly")
        client_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Get client names for combobox
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, name FROM clients ORDER BY name")
        clients = c.fetchall()
        client_combobox['values'] = [f"{name} (ID:{id})" for id, name in clients]
        conn.close()
        
        # Order details
        ttk.Label(dialog, text="Description:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        desc_entry = ttk.Entry(dialog, width=40)
        desc_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        desc_entry.insert(0, order[2])
        
        ttk.Label(dialog, text="Estimated Weight (g):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        est_weight_entry = ttk.Entry(dialog)
        est_weight_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        est_weight_entry.insert(0, order[3])
        
        ttk.Label(dialog, text="Actual Weight (g):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        actual_weight_entry = ttk.Entry(dialog)
        actual_weight_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        if order[4]:  # If actual weight exists
            actual_weight_entry.insert(0, order[4])
        
        ttk.Label(dialog, text="Purity:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.E)
        purity_entry = ttk.Entry(dialog)
        purity_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        purity_entry.insert(0, order[5])
        
        ttk.Label(dialog, text="Delivery Date:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.E)
        delivery_entry = ttk.Entry(dialog)
        delivery_entry.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
        delivery_entry.insert(0, order[7])
        
        ttk.Label(dialog, text="Status:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.E)
        status_combobox = ttk.Combobox(dialog, values=["Pending", "In Progress", "Completed", "Delivered", "Cancelled"])
        status_combobox.grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)
        status_combobox.set(order[8])
        
        ttk.Label(dialog, text="Price per gram (KWD):").grid(row=7, column=0, padx=5, pady=5, sticky=tk.E)
        price_entry = ttk.Entry(dialog)
        price_entry.grid(row=7, column=1, padx=5, pady=5, sticky=tk.W)
        if order[9]:  # If price exists
            price_entry.insert(0, order[9])
        
        ttk.Label(dialog, text="Making charges (KWD):").grid(row=8, column=0, padx=5, pady=5, sticky=tk.E)
        making_charges_entry = ttk.Entry(dialog)
        making_charges_entry.grid(row=8, column=1, padx=5, pady=5, sticky=tk.W)
        if order[10]:  # If making charges exist
            making_charges_entry.insert(0, order[10])
        
        # Items section
        items = []

        def add_item():
            desc = item_desc_entry.get()
            weight = item_weight_entry.get()
            purity = item_purity_entry.get()
            rate = item_rate_entry.get()
            amount = float(weight) * float(rate) if weight and rate else 0
            items.append((desc, weight, purity, rate, amount))
            items_listbox.insert(tk.END, f"{desc} | {weight}g | {purity} | {rate} | {amount}")
            item_desc_entry.delete(0, tk.END)
            item_weight_entry.delete(0, tk.END)
            item_purity_entry.delete(0, tk.END)
            item_rate_entry.delete(0, tk.END)

        ttk.Label(dialog, text="Item Description:").grid(row=9, column=0)
        item_desc_entry = ttk.Entry(dialog)
        item_desc_entry.grid(row=9, column=1)
        ttk.Label(dialog, text="Weight:").grid(row=10, column=0)
        item_weight_entry = ttk.Entry(dialog)
        item_weight_entry.grid(row=10, column=1)
        ttk.Label(dialog, text="Purity:").grid(row=11, column=0)
        item_purity_entry = ttk.Entry(dialog)
        item_purity_entry.grid(row=11, column=1)
        ttk.Label(dialog, text="Rate:").grid(row=12, column=0)
        item_rate_entry = ttk.Entry(dialog)
        item_rate_entry.grid(row=12, column=1)
        ttk.Button(dialog, text="Add Item", command=add_item).grid(row=13, column=0, columnspan=2)

        items_listbox = tk.Listbox(dialog, width=60)
        items_listbox.grid(row=14, column=0, columnspan=2)
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=9, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Update", command=lambda: self.update_order(
            order_id,
            client_var.get(),
            desc_entry.get(),
            est_weight_entry.get(),
            actual_weight_entry.get(),
            purity_entry.get(),
            delivery_entry.get(),
            status_combobox.get(),
            price_entry.get(),
            making_charges_entry.get(),
            items,
            dialog
        )).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def update_order(self, order_id, client, description, est_weight, actual_weight, purity, delivery_date, status, price_per_gm, making_charges, items, dialog):
        """Update order in database"""
        try:
            # Extract client ID from combobox text
            client_id = int(client.split("(ID:")[1].rstrip(")"))
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Convert empty actual weight to NULL
            actual_weight = float(actual_weight) if actual_weight else None
            price_per_gm = float(price_per_gm) if price_per_gm else None
            making_charges = float(making_charges) if making_charges else None
            
            c.execute('''UPDATE orders SET
                        client_id = ?,
                        description = ?,
                        estimated_weight = ?,
                        actual_weight = ?,
                        purity = ?,
                        delivery_date = ?,
                        status = ?,
                        price_per_gm = ?,
                        making_charges = ?
                        WHERE id = ?''',
                    (client_id, description, float(est_weight), actual_weight, 
                     float(purity), delivery_date, status, 
                     price_per_gm, making_charges, order_id))
            
            # Delete existing order items
            c.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
            
            # Insert new order items
            for item in items:
                c.execute('''INSERT INTO order_items (order_id, description, weight, purity, rate, amount)
                            VALUES (?, ?, ?, ?, ?, ?)''',
                          (order_id, item[0], float(item[1]), float(item[2]), float(item[3]), float(item[4])))

            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Order updated successfully!")
            dialog.destroy()
            self.load_orders()
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update order: {str(e)}")
    
    def delete_order(self):
        """Delete selected order"""
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an order to delete")
            return
        
        order_id = self.orders_tree.item(selected[0], "values")[0]
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this order?"):
            try:
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                c.execute("DELETE FROM orders WHERE id = ?", (order_id,))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Order deleted successfully!")
                self.load_orders()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete order: {str(e)}")
    
    def generate_invoice_from_order(self):
        """Generate invoice for selected order"""
        selected = self.orders_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an order to generate invoice")
            return
        
        order_id = self.orders_tree.item(selected[0], "values")[0]
        self.generate_invoice(order_id)
    
    def generate_invoice(self, order_id):
        """Generate PDF invoice for an order"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Get order details
        c.execute('''SELECT orders.*, clients.name, clients.phone, clients.address
                     FROM orders
                     LEFT JOIN clients ON orders.client_id = clients.id
                     WHERE orders.id = ?''', (order_id,))
        order = c.fetchone()
        
        if not order:
            messagebox.showerror("Error", "Order not found")
            return
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Header
        pdf.cell(200, 10,  txt="BARKAT AL KHAIR", ln=1, align='C')
        pdf.ln(10)
        
        # Invoice info
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(50, 10, txt="Invoice #:", ln=0)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt=f"ORD-{order[0]:04d}", ln=1)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(50, 10, txt="Date:", ln=0)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, txt=datetime.now().strftime("%Y-%m-%d"), ln=1)
        pdf.ln(5)
        
        # Client info
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Information", ln=1)
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt=f"Name: {order[11]}", ln=1)
        pdf.cell(200, 10, txt=f"Phone: {order[12]}", ln=1)
        pdf.cell(200, 10, txt=f"Address: {order[13]}", ln=1)
        pdf.ln(10)
        
        # Order details
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt="Order Details", ln=1)
        pdf.set_font("Arial", size=10)
        
        pdf.cell(50, 10, txt="Description:", ln=0)
        pdf.cell(0, 10, txt=order[2], ln=1)
        
        pdf.cell(50, 10, txt="Delivery Date:", ln=0)
        pdf.cell(0, 10, txt=order[7], ln=1)
        
        pdf.cell(50, 10, txt="Status:", ln=0)
        pdf.cell(0, 10, txt=order[8], ln=1)
        pdf.ln(10)
    
        # Items table
        # pdf.set_font("Arial", 'B', 12)
        # pdf.cell(200, 10, "Items", ln=1)
    
        # pdf.set_font("Arial", 'B', 10)
        # pdf.cell(70, 10, "Description", 1, 0, 'C')
        # pdf.cell(30, 10, "Weight (g)", 1, 0, 'C')
        # pdf.cell(30, 10, "Purity", 1, 0, 'C')
        # pdf.cell(30, 10, "Rate (KWD/g)", 1, 0, 'C')
        # pdf.cell(30, 10, "Amount (KWD)", 1, 1, 'C')
        
        pdf.set_font("Arial", size=10)
        # Fetch all items for this order
        c.execute('''SELECT description, weight, purity, rate, amount FROM order_items WHERE order_id = ?''', (order_id,))
        items = c.fetchall()

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, "Items", ln=1)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(70, 10, "Description", 1, 0, 'C')
        pdf.cell(30, 10, "Weight (g)", 1, 0, 'C')
        pdf.cell(30, 10, "Purity", 1, 0, 'C')
        pdf.cell(30, 10, "Rate (KWD/g)", 1, 0, 'C')
        pdf.cell(30, 10, "Amount (KWD)", 1, 1, 'C')
        pdf.set_font("Arial", size=10)
        for desc, weight, purity, rate, amount in items:
            pdf.cell(70, 10, str(desc), 1, 0)
            pdf.cell(30, 10, f"{weight:.2f}", 1, 0, 'R')
            pdf.cell(30, 10, f"{purity:.3f}", 1, 0, 'R')
            pdf.cell(30, 10, f"{rate:.2f}", 1, 0, 'R')
            pdf.cell(30, 10, f"{amount:,.2f}", 1, 1, 'R')
        
        # Calculate total amount from all items
        items_total = sum(item[4] for item in items)  # item[4] is amount

        # Making charges
        if order[10]:  # If making charges exist
            pdf.cell(160, 10, "Making Charges:", 1, 0, 'R')
            pdf.cell(30, 10, f"{order[10]:,.2f}", 1, 1, 'R')
        
        # Total
        total = items_total + (order[10] if order[10] else 0)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(160, 10, "TOTAL:", 1, 0, 'R')
        pdf.cell(30, 10, f"{total:,.2f}", 1, 1, 'R')
        
        
        
        # Save the PDF
        invoice_path = f"invoice_ORD-{order[0]:04d}.pdf"
        pdf.output(invoice_path)
        
        # Show success message
        messagebox.showinfo("Success", f"Invoice generated:\n{os.path.abspath(invoice_path)}")
        webbrowser.open(invoice_path)
    
    def build_inventory_tab(self):
        """Build the inventory management tab"""
        # Frame for controls
        controls_frame = ttk.Frame(self.inventory_tab)
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Buttons
        ttk.Button(controls_frame, text="Add Received Gold", command=lambda: self.add_inventory("received"),
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Add Issued Gold", command=lambda: self.add_inventory("issued")).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Delete Transaction", command=self.delete_inventory).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Refresh", command=self.load_inventory).pack(side=tk.LEFT, padx=5)
        
        # Treeview for inventory
        columns = ("id", "type", "weight", "purity", "price", "date", "notes", "client")
        self.inventory_tree = ttk.Treeview(self.inventory_tab, columns=columns, show="headings", selectmode="browse")
        
        # Configure columns
        self.inventory_tree.heading("id", text="ID")
        self.inventory_tree.heading("type", text="Type")
        self.inventory_tree.heading("weight", text="Weight (g)")
        self.inventory_tree.heading("purity", text="Purity")
        self.inventory_tree.heading("price", text="Rate (KWD/g)")
        self.inventory_tree.heading("date", text="Date")
        self.inventory_tree.heading("notes", text="Notes")
        self.inventory_tree.heading("client", text="Client")
        
        self.inventory_tree.column("id", width=50, anchor=tk.CENTER)
        self.inventory_tree.column("type", width=100)
        self.inventory_tree.column("weight", width=80, anchor=tk.E)
        self.inventory_tree.column("purity", width=80, anchor=tk.E)
        self.inventory_tree.column("price", width=80, anchor=tk.E)
        self.inventory_tree.column("date", width=100)
        self.inventory_tree.column("notes", width=300)
        self.inventory_tree.column("client", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.inventory_tab, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.inventory_tree.pack(fill=tk.BOTH, expand=True)
    
    def load_inventory(self):
        """Load inventory transactions from database"""
        self.inventory_tree.delete(*self.inventory_tree.get_children())
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''SELECT inventory.id, inventory.transaction_type, inventory.weight, inventory.purity, 
                        inventory.price_per_gm, inventory.date, inventory.notes, clients.name
                 FROM inventory
                 LEFT JOIN clients ON inventory.client_id = clients.id
                 ORDER BY inventory.date DESC''')
        for row in c.fetchall():
            self.inventory_tree.insert("", tk.END, values=row)
        conn.close()
    
    def add_inventory(self, transaction_type):
        """Add inventory transaction (received/issued gold)"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Add {transaction_type.capitalize()} Gold")
        dialog.grab_set()

        # Client selection
        ttk.Label(dialog, text="Client:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        client_var = tk.StringVar()
        client_combobox = ttk.Combobox(dialog, textvariable=client_var)
        client_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Get client names for combobox
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, name FROM clients ORDER BY name")
        clients = c.fetchall()
        client_combobox['values'] = [f"{name} (ID:{id})" for id, name in clients]
        conn.close()

        ttk.Label(dialog, text="Weight (grams):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        weight_entry = ttk.Entry(dialog)
        weight_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Purity:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        purity_entry = ttk.Entry(dialog)
        purity_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        purity_entry.insert(0, "0.999")  # Default 24k purity
        
        ttk.Label(dialog, text="Price per gram (KWD):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        price_entry = ttk.Entry(dialog)
        price_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Date:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.E)
        date_entry = ttk.Entry(dialog)
        date_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Label(dialog, text="Notes:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.E)
        notes_entry = ttk.Entry(dialog, width=40)
        notes_entry.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="Save", command=lambda: self.save_inventory(
            transaction_type,
            client_var.get(),
            weight_entry.get(),
            purity_entry.get(),
            price_entry.get(),
            date_entry.get(),
            notes_entry.get(),
            dialog
        )).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_inventory(self, transaction_type, client, weight, purity, price, date, notes, dialog):
        """Save inventory transaction to database"""
        try:
            # Extract client ID from combobox text
            client_id = None
            if client and "(ID:" in client:
                client_id = int(client.split("(ID:")[1].rstrip(")"))
            # For issued gold, client is required
            if transaction_type == "issued" and not client_id:
                messagebox.showerror("Error", "Please select a client for issued gold.")
                return

            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            c.execute('''INSERT INTO inventory 
                        (transaction_type, weight, purity, price_per_gm, date, notes, client_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (transaction_type, float(weight), float(purity), 
                     float(price) if price else None, date, notes, client_id))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Inventory transaction added successfully!")
            dialog.destroy()
            self.load_inventory()
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save transaction: {str(e)}")
    
    def delete_inventory(self):
        """Delete selected inventory transaction"""
        selected = self.inventory_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a transaction to delete")
            return
        
        transaction_id = self.inventory_tree.item(selected[0], "values")[0]
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this transaction?"):
            try:
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                c.execute("DELETE FROM inventory WHERE id = ?", (transaction_id,))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Transaction deleted successfully!")
                self.load_inventory()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete transaction: {str(e)}")
    
    def build_clients_tab(self):
        """Build the clients management tab"""
        # Frame for controls
        controls_frame = ttk.Frame(self.clients_tab)
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Buttons
        ttk.Button(controls_frame, text="Add Client", command=self.add_client,
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Edit Client", command=self.edit_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Delete Client", command=self.delete_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Refresh", command=self.load_clients).pack(side=tk.LEFT, padx=5)
        
        # Search frame
        search_frame = ttk.Frame(self.clients_tab)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.client_search_entry = ttk.Entry(search_frame, width=30)
        self.client_search_entry.pack(side=tk.LEFT, padx=5)
        self.client_search_entry.bind("<KeyRelease>", lambda e: self.search_clients())
        
        ttk.Button(search_frame, text="Clear", command=self.clear_client_search).pack(side=tk.LEFT, padx=5)
        
        # Treeview for clients
        columns = ("id", "name", "phone", "address", "created_date")
        self.clients_tree = ttk.Treeview(self.clients_tab, columns=columns, show="headings", selectmode="browse")
        
        # Configure columns
        self.clients_tree.heading("id", text="ID")
        self.clients_tree.heading("name", text="Name")
        self.clients_tree.heading("phone", text="Phone")
        self.clients_tree.heading("address", text="Address")
        self.clients_tree.heading("created_date", text="Created Date")
        
        self.clients_tree.column("id", width=50, anchor=tk.CENTER)
        self.clients_tree.column("name", width=150)
        self.clients_tree.column("phone", width=120)
        self.clients_tree.column("address", width=250)
        self.clients_tree.column("created_date", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.clients_tab, orient=tk.VERTICAL, command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.clients_tree.pack(fill=tk.BOTH, expand=True)
    
    def search_clients(self):
        """Search clients based on search term"""
        search_term = self.client_search_entry.get().strip()
        if not search_term:
            self.load_clients()
            return
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        query = '''SELECT * FROM clients 
                  WHERE name LIKE ? OR phone LIKE ? OR address LIKE ?
                  ORDER BY name'''
        
        search_param = f"%{search_term}%"
        c.execute(query, (search_param, search_param, search_param))
        
        self.clients_tree.delete(*self.clients_tree.get_children())
        for row in c.fetchall():
            self.clients_tree.insert("", tk.END, values=row)
        
        conn.close()
    
    def clear_client_search(self):
        """Clear client search and reload all clients"""
        self.client_search_entry.delete(0, tk.END)
        self.load_clients()
    
    def load_clients(self):
        """Load clients from database"""
        self.clients_tree.delete(*self.clients_tree.get_children())
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("SELECT * FROM clients ORDER BY name")
        
        for row in c.fetchall():
            self.clients_tree.insert("", tk.END, values=row)
        
        conn.close()
    
    def add_client(self):
        """Add new client"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Client")
        dialog.grab_set()
        
        ttk.Label(dialog, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Phone:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        phone_entry = ttk.Entry(dialog)
        phone_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Label(dialog, text="Address:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        address_entry = ttk.Entry(dialog, width=40)
        address_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Save", command=lambda: self.save_client(
            name_entry.get(),
            phone_entry.get(),
            address_entry.get(),
            dialog
        )).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_client(self, name, phone, address, dialog):
        """Save new client to database"""
        if not name:
            messagebox.showerror("Error", "Name is required")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''INSERT INTO clients 
                        (name, phone, address, created_date)
                        VALUES (?, ?, ?, ?)''',
                    (name, phone, address, datetime.now().strftime("%Y-%m-%d")))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Client added successfully!")
            dialog.destroy()
            self.load_clients()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save client: {str(e)}")
    
    def edit_client(self):
        """Edit selected client"""
        selected = self.clients_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a client to edit")
            return
        
        client_id = self.clients_tree.item(selected[0], "values")[0]
        
        # Fetch client details
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        client = c.fetchone()
        conn.close()
        
        if not client:
            messagebox.showerror("Error", "Client not found")
            return
        
        # Open edit dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Client")
        dialog.grab_set()
        
        ttk.Label(dialog, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        name_entry.insert(0, client[1])
        
        ttk.Label(dialog, text="Phone:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        phone_entry = ttk.Entry(dialog)
        phone_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        phone_entry.insert(0, client[2])
        
        ttk.Label(dialog, text="Address:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        address_entry = ttk.Entry(dialog, width=40)
        address_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        address_entry.insert(0, client[3])
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Update", command=lambda: self.update_client(
            client_id,
            name_entry.get(),
            phone_entry.get(),
            address_entry.get(),
            dialog
        )).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def update_client(self, client_id, name, phone, address, dialog):
        """Update client in database"""
        if not name:
            messagebox.showerror("Error", "Name is required")
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''UPDATE clients SET
                        name = ?,
                        phone = ?,
                        address = ?
                        WHERE id = ?''',
                    (name, phone, address, client_id))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Client updated successfully!")
            dialog.destroy()
            self.load_clients()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update client: {str(e)}")
    
    def delete_client(self):
        """Delete selected client"""
        selected = self.clients_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a client to delete")
            return
        
        client_id = self.clients_tree.item(selected[0], "values")[0]
        
        # Check if client has orders
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM orders WHERE client_id = ?", (client_id,))
        order_count = c.fetchone()[0]
        conn.close()
        
        if order_count > 0:
            messagebox.showerror("Error", "Cannot delete client with existing orders")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this client?"):
            try:
                conn = sqlite3.connect(self.db_path)
                c = conn.cursor()
                c.execute("DELETE FROM clients WHERE id = ?", (client_id,))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", "Client deleted successfully!")
                self.load_clients()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete client: {str(e)}")
    
    def build_invoices_tab(self):
        """Build the invoices tab"""
        # Frame for controls
        controls_frame = ttk.Frame(self.invoices_tab)
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Buttons
        ttk.Button(controls_frame, text="Generate Invoice", command=self.generate_invoice_dialog,
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Print Invoice", command=self.print_invoice).pack(side=tk.LEFT, padx=5)
        
        # Invoice preview area
        self.invoice_text = tk.Text(self.invoices_tab, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(self.invoices_tab, orient=tk.VERTICAL, command=self.invoice_text.yview)
        self.invoice_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.invoice_text.pack(fill=tk.BOTH, expand=True)
    
    def generate_invoice_dialog(self):
        """Show dialog to select order for invoice generation"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Generate Invoice")
        dialog.grab_set()
        
        ttk.Label(dialog, text="Select Order:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        
        # Treeview for orders
        columns = ("id", "client", "description", "date")
        order_tree = ttk.Treeview(dialog, columns=columns, show="headings", height=10)
        
        order_tree.heading("id", text="ID")
        order_tree.heading("client", text="Client")
        order_tree.heading("description", text="Description")
        order_tree.heading("date", text="Date")
        
        order_tree.column("id", width=50, anchor=tk.CENTER)
        order_tree.column("client", width=150)
        order_tree.column("description", width=200)
        order_tree.column("date", width=100)
        
        
        scrollbar = ttk.Scrollbar(dialog, orient=tk.VERTICAL, command=order_tree.yview)
        order_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky=tk.NS)
        order_tree.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NSEW)
        
        # Load orders
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''SELECT orders.id, clients.name, orders.description, orders.order_date
                     FROM orders LEFT JOIN clients ON orders.client_id = clients.id
                     ORDER BY orders.order_date DESC''')
        for row in c.fetchall():
            order_tree.insert("", tk.END, values=row)
        conn.close()
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Generate", 
                  command=lambda: self.generate_invoice_from_dialog(order_tree, dialog)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def generate_invoice_from_dialog(self, order_tree, dialog):
        """Generate invoice from dialog selection"""
        selected = order_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an order to generate invoice")
            return
        
        order_id = order_tree.item(selected[0], "values")[0]
        self.generate_invoice(order_id)
        dialog.destroy()
    
    def print_invoice(self):
        """Print current invoice"""
        if not self.invoice_text.get("1.0", tk.END).strip():
            messagebox.showwarning("Warning", "No invoice to print")
            return
        
        # This is a placeholder - actual printing would require more complex setup
        messagebox.showinfo("Print", "Invoice would be sent to printer")
    
    def generate_sample_data(self):
        """Generate sample data for testing"""
        if not messagebox.askyesno("Confirm", "This will overwrite your database with sample data. Continue?"):
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Clear existing data
            c.execute("DELETE FROM orders")
            c.execute("DELETE FROM clients")
            c.execute("DELETE FROM inventory")
            c.execute("DELETE FROM rates")
            
            # Add sample rates
            c.execute("INSERT INTO rates (date, gold_rate, silver_rate) VALUES (?, ?, ?)",
                     (datetime.now().strftime("%Y-%m-%d"), 5000, 60))
            
            # Add sample clients
            sample_clients = [
                ("John Smith", "555-0101", "123 Main St"),
                ("Emma Johnson", "555-0102", "456 Oak Ave"),
                ("Michael Brown", "555-0103", "789 Pine Rd")
            ]
            
            for name, phone, address in sample_clients:
                c.execute('''INSERT INTO clients 
                            (name, phone, address, created_date)
                            VALUES (?, ?, ?, ?)''',
                        (name, phone, address, datetime.now().strftime("%Y-%m-%d")))
            
            # Add sample inventory
            sample_inventory = [
                ("received", 100.5, 0.999, datetime.now().strftime("%Y-%m-%d"), "Initial stock", 4800),
                ("issued", 25.2, 0.999, datetime.now().strftime("%Y-%m-%d"), "For order #1", 5000),
                ("received", 50.0, 0.999, datetime.now().strftime("%Y-%m-%d"), "New purchase", 4900)
            ]
            
            for trans_type, weight, purity, date, notes, price in sample_inventory:
                c.execute('''INSERT INTO inventory 
                            (transaction_type, weight, purity, date, notes, price_per_gm)
                            VALUES (?, ?, ?, ?, ?, ?)''',
                        (trans_type, weight, purity, date, notes, price))
            
            # Add sample orders
            c.execute("SELECT id FROM clients ORDER BY id")
            client_ids = [row[0] for row in c.fetchall()]
            
            sample_orders = [
                (client_ids[0], "Gold chain", 15.5, 15.3, 0.999, 
                 datetime.now().strftime("%Y-%m-%d"), 
                 (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"), 
                 "Completed", 5000, 1500),
                (client_ids[1], "Gold ring", 8.2, 8.1, 0.999, 
                 datetime.now().strftime("%Y-%m-%d"), 
                 (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"), 
                 "In Progress", 5000, 800),
                (client_ids[2], "Gold bracelet", 22.0, None, 0.999, 
                 datetime.now().strftime("%Y-%m-%d"), 
                 (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"), 
                 "Pending", 5000,   1200)

            ]
            
            for client_id, desc, est, act, purity, order_date, delivery, status, price, charges in sample_orders:
                c.execute('''INSERT INTO orders 
                            (client_id, description, estimated_weight, actual_weight, purity, 
                             order_date, delivery_date, status, price_per_gm, making_charges)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (client_id, desc, est, act, purity, order_date, delivery, status, price, charges))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Success", "Sample data generated successfully!")
            self.load_orders()
            self.load_inventory()
            self.load_clients()
            self.load_dashboard_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate sample data: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = GoldShopApp(root)
    
    
    app.generate_sample_data()
    
    root.mainloop()
