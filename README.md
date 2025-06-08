# Gold Shop Management System

A desktop application built using Python and Tkinter to manage day-to-day operations of a gold shop. 
This application includes modules for managing client orders, tracking gold inventory, generating invoices, and maintaining historical transaction reports — all stored securely in a local SQLite database.

---

## ✨ Key Features

### 🧾 Order Management
- Create and manage orders with detailed gold item entries.
- Support for estimated and actual weight, purity, rate, and delivery dates.
- Status tracking for orders (Pending, In Progress, Completed, Delivered, Cancelled).
- Assign orders to registered clients.

### 👥 Client Management
- Add, edit, and delete client records with name, phone, and address.
- Automatically link clients to their respective orders and inventory movements.

### 🪙 Inventory Tracking
- Log and differentiate between gold **received** and **issued**.
- Maintain purity, weight, and rate records for each transaction.
- Calculate net gold in stock in real-time.

### 📄 Invoice & Report Generation
- Auto-generate professional PDF invoices for client orders.
- Generate daily summaries and inventory reports in PDF.
- Client-wise order reports with total gold transaction summaries.

### 📊 Dashboard
- Real-time overview with:
  - Today's gold & silver rates
  - Total orders and pending orders
  - Total gold stock available
  - Total active clients
- View recent orders and statistics in a tabbed interface.

### 🧮 Tools
- Gold value calculator (based on weight and purity).
- Set and update daily gold/silver rates.

### 💾 Data Management
- One-click database backup and restore functionality.
- All data securely stored in a local SQLite database (`gold.db`).

---

## 🖥️ Technologies Used

- **Language:** Python 3.x
- **GUI:** Tkinter (ttk-themed)
- **Database:** SQLite (local, file-based)
- **PDF Reports:** [FPDF](https://pyfpdf.readthedocs.io/en/latest/)

---

## 📦 Installation

### Requirements

```bash
pip install fpdf
