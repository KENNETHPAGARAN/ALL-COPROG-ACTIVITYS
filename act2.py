import tkinter as tk

def generate_receipt():
    try:
        customer_number = int(customer_number_entry.get())
        customer_name = customer_name_entry.get()
        item = item_entry.get()
        price = int(price_entry.get())
        quantity = int(quantity_entry.get())
        
        total = price * quantity
        
        receipt_text.delete(1.0, tk.END)
        receipt_text.insert(tk.END, "----------------------------\n")
        receipt_text.insert(tk.END, "         RECEIPT            \n")
        receipt_text.insert(tk.END, f" customer number: {customer_number}\n")
        receipt_text.insert(tk.END, f" customer name: {customer_name}\n")
        receipt_text.insert(tk.END, f" item description: {item}\n")
        receipt_text.insert(tk.END, f"YOUR TOTAL PRICE IS: {total}\n")
        receipt_text.insert(tk.END, "----------------------------\n")
    except ValueError:
        receipt_text.delete(1.0, tk.END)
        receipt_text.insert(tk.END, "Invalid input. Please enter numbers for customer number, price, and quantity.")

root = tk.Tk()
root.title("Receipt Generator")

tk.Label(root, text="Customer Number:").grid(row=0, column=0)
customer_number_entry = tk.Entry(root)
customer_number_entry.grid(row=0, column=1)

tk.Label(root, text="Customer Name:").grid(row=1, column=0)
customer_name_entry = tk.Entry(root)
customer_name_entry.grid(row=1, column=1)

tk.Label(root, text="Item:").grid(row=2, column=0)
item_entry = tk.Entry(root)
item_entry.grid(row=2, column=1)

tk.Label(root, text="Price:").grid(row=3, column=0)
price_entry = tk.Entry(root)
price_entry.grid(row=3, column=1)

tk.Label(root, text="Quantity:").grid(row=4, column=0)
quantity_entry = tk.Entry(root)
quantity_entry.grid(row=4, column=1)

tk.Button(root, text="Generate Receipt", command=generate_receipt).grid(row=5, column=0, columnspan=2)

receipt_text = tk.Text(root, height=10, width=40)
receipt_text.grid(row=6, column=0, columnspan=2)

root.mainloop()	


