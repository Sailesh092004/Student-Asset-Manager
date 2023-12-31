import tkinter as tk
from tkinter import ttk
import sqlite3

class Vehicle:
    def __init__(self, name, available=True):
        self.name = name
        self.available = available
        self.renter = None
        self.rent_duration = 0

    def rent(self, person, duration):
        self.renter = person
        self.rent_duration = duration
        self.available = False

    def return_item(self):
        self.renter = None
        self.rent_duration = 0
        self.available = True

class Person:
    def __init__(self, name):
        self.name = name

class RentalSystem:
    DATABASE_NAME = 'rental.db'

    def __init__(self):
        self.vehicles = [Vehicle("Book"), Vehicle("Bike"), Vehicle("Calculator")]
        self.create_rental_table()
        self.setup_ui()

    def create_rental_table(self):
        conn = sqlite3.connect(self.DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rental (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT,
                person TEXT,
                duration INTEGER,
                cost INTEGER
            )
        ''')
        conn.commit()
        conn.close()

    def rent_item(self):
        item = item_entry.get()
        duration_str = duration_entry.get().strip()
        person_name = person_entry.get()
        rent_price_str = rent_price_entry.get().strip()  # New entry for rent price

        if not duration_str or not rent_price_str:
            result_label.config(text="Please enter valid duration and rent price.")
            return

        try:
            duration = int(duration_str)
            rent_price = int(rent_price_str)
        except ValueError:
            result_label.config(text="Invalid duration or rent price. Please enter valid numbers.")
            return

        for vehicle in self.vehicles:
            if vehicle.name == item and vehicle.available:
                person = Person(person_name)
                vehicle.rent(person, duration)
                rent_cost = duration * rent_price
                result_label.config(text=f"{person_name} rented {item} for {duration} days. Rent cost: {rent_cost} INR")

                conn = sqlite3.connect(self.DATABASE_NAME)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO rental (item, person, duration, cost) VALUES (?, ?, ?, ?)",
                               (item, person_name, duration, rent_cost))
                conn.commit()
                conn.close()

                self.show_rental_data()
                break
        else:
            result_label.config(text=f"{item} is not available for rent.")

    def return_item(self):
        item = item_entry.get()

        for vehicle in self.vehicles:
            if vehicle.name == item and not vehicle.available:
                person_name = vehicle.renter.name
                rent_duration = vehicle.rent_duration
                rent_price = int(rent_price_entry.get().strip())  # Get rent price for cost calculation
                rent_cost = rent_duration * rent_price
                vehicle.return_item()
                result_label.config(text=f"{person_name} returned {item}. Rent cost: {rent_cost} INR")

                conn = sqlite3.connect(self.DATABASE_NAME)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM rental WHERE item = ? AND person = ?",
                               (item, person_name))
                conn.commit()
                conn.close()

                self.show_rental_data()
                break
        else:
            result_label.config(text=f"{item} is not currently rented.")

    def show_rental_data(self):
        conn = sqlite3.connect(self.DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rental")
        data = cursor.fetchall()
        conn.close()

        for row in table.get_children():
            table.delete(row)

        for row in data:
            table.insert('', 'end', values=row)

    def setup_ui(self):
        self.app = tk.Tk()
        self.app.title("University Student Rental System")

        item_label = tk.Label(self.app, text="Item:")
        item_label.pack()
        global item_entry
        item_entry = tk.Entry(self.app)
        item_entry.pack()

        duration_label = tk.Label(self.app, text="Duration (days):")
        duration_label.pack()
        global duration_entry
        duration_entry = tk.Entry(self.app)
        duration_entry.pack()

        rent_price_label = tk.Label(self.app, text="Rent Price (INR per day):")  # New label for rent price
        rent_price_label.pack()
        global rent_price_entry
        rent_price_entry = tk.Entry(self.app)
        rent_price_entry.pack()

        person_label = tk.Label(self.app, text="Renter's Name:")
        person_label.pack()
        global person_entry
        person_entry = tk.Entry(self.app)
        person_entry.pack()

        rent_button = tk.Button(self.app, text="Rent", command=self.rent_item)
        rent_button.pack()

        return_button = tk.Button(self.app, text="Return", command=self.return_item)
        return_button.pack()

        global result_label
        result_label = tk.Label(self.app, text="")
        result_label.pack()

        global table
        table = ttk.Treeview(self.app, columns=('ID', 'Item', 'Person', 'Duration', 'Cost'), show='headings')
        table.heading('ID', text='ID')
        table.heading('Item', text='Item')
        table.heading('Person', text='Person')
        table.heading('Duration', text='Duration (days)')
        table.heading('Cost', text='Cost (INR)')
        table.pack()

        self.show_rental_data()

    def start(self):
        self.app.mainloop()

if __name__ == "__main__":
    rental_system = RentalSystem()
    rental_system.start()
