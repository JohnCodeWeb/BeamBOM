import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
import subprocess
import csv
import os
from PIL import Image, ImageDraw, ImageTk
import re
import math
from pcb_utils import calculate_scale_factor, scale_component_position, get_pcb_dimensions

class FootprintDialog(tk.Toplevel):
    def __init__(self, parent, footprint, is_new=True):
        super().__init__(parent)
        self.title("Add Footprint" if is_new else "Modify Footprint")
        self.footprint = footprint
        self.result = None

        tk.Label(self, text="Shape:").grid(row=0, column=0, sticky="w")
        self.shape_var = tk.StringVar(value="rectangle")
        tk.Radiobutton(self, text="Rectangle", variable=self.shape_var, value="rectangle", command=self.update_preview).grid(row=0, column=1, sticky="w")
        tk.Radiobutton(self, text="Circle", variable=self.shape_var, value="circle", command=self.update_preview).grid(row=0, column=2, sticky="w")

        tk.Label(self, text="Width/Diameter:").grid(row=1, column=0, sticky="w")
        self.width_var = tk.StringVar(value="1.0")
        tk.Entry(self, textvariable=self.width_var).grid(row=1, column=1, columnspan=2, sticky="we")

        tk.Label(self, text="Height:").grid(row=2, column=0, sticky="w")
        self.height_var = tk.StringVar(value="1.0")
        self.height_entry = tk.Entry(self, textvariable=self.height_var)
        self.height_entry.grid(row=2, column=1, columnspan=2, sticky="we")

        tk.Label(self, text="Center X:").grid(row=3, column=0, sticky="w")
        self.center_x_var = tk.StringVar(value="0.0")
        tk.Entry(self, textvariable=self.center_x_var).grid(row=3, column=1, columnspan=2, sticky="we")

        tk.Label(self, text="Center Y:").grid(row=4, column=0, sticky="w")
        self.center_y_var = tk.StringVar(value="0.0")
        tk.Entry(self, textvariable=self.center_y_var).grid(row=4, column=1, columnspan=2, sticky="we")

        self.preview_canvas = tk.Canvas(self, width=200, height=200, bg="white")
        self.preview_canvas.grid(row=5, column=0, columnspan=3, pady=10)

        tk.Button(self, text="Save", command=self.save).grid(row=6, column=0, columnspan=3)

        self.shape_var.trace("w", lambda *args: self.update_preview())
        self.width_var.trace("w", lambda *args: self.update_preview())
        self.height_var.trace("w", lambda *args: self.update_preview())
        self.center_x_var.trace("w", lambda *args: self.update_preview())
        self.center_y_var.trace("w", lambda *args: self.update_preview())

        self.update_preview()

    def update_preview(self):
        self.preview_canvas.delete("all")
        shape = self.shape_var.get()
        try:
            width = float(self.width_var.get()) * 10
            height = float(self.height_var.get()) * 10
            center_x = float(self.center_x_var.get()) * 10 + 100
            center_y = float(self.center_y_var.get()) * 10 + 100
        except ValueError:
            # If any of the values are empty or invalid, just return without updating
            return

        if shape == "rectangle":
            self.preview_canvas.create_rectangle(center_x - width/2, center_y - height/2,
                                                 center_x + width/2, center_y + height/2,
                                                 outline="black")
            self.height_entry.config(state="normal")
        else:
            self.preview_canvas.create_oval(center_x - width/2, center_y - width/2,
                                            center_x + width/2, center_y + width/2,
                                            outline="black")
            self.height_entry.config(state="disabled")

    def save(self):
        try:
            self.result = {
                "name": self.footprint,
                "shape": self.shape_var.get(),
                "width": float(self.width_var.get()),
                "height": float(self.height_var.get()) if self.shape_var.get() == "rectangle" else float(self.width_var.get()),
                "center_x": float(self.center_x_var.get()),
                "center_y": float(self.center_y_var.get())
            }
            self.destroy()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for all dimensions.")

class PCBOutlineDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Set PCB Outline")
        self.result = None

        tk.Label(self, text="Width (mm):").grid(row=0, column=0, padx=5, pady=5)
        self.width_entry = tk.Entry(self)
        self.width_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self, text="Length (mm):").grid(row=1, column=0, padx=5, pady=5)
        self.length_entry = tk.Entry(self)
        self.length_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(self, text="OK", command=self.ok).grid(row=2, column=0, padx=5, pady=5)
        tk.Button(self, text="Cancel", command=self.cancel).grid(row=2, column=1, padx=5, pady=5)

    def ok(self):
        try:
            width = round(float(self.width_entry.get()), 4)
            length = round(float(self.length_entry.get()), 4)
            self.result = (width, length)
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for width and length.")

    def cancel(self):
        self.destroy()

class ProjectionGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Projection GUI")
        self.geometry("800x600")
        self.configure(bg="black")
        
        # Set file paths first
        self.set_file_paths()
        
        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Initialize variables
        self.fill_var = tk.BooleanVar(value=False)
        self.names_var = tk.BooleanVar(value=True)
        self.shapes_var = tk.BooleanVar(value=True)
        
        # Initialize other attributes
        self.pcb_rect = None
        self.pcb_anchors = []
        self.pcb_outline = None
        self.pcb_width = None
        self.pcb_length = None
        self.original_pcb_width = None
        self.original_pcb_length = None
        
        # Initialize BOM-related variables
        self.current_page = 0
        self.total_pages = 0
        self.bom_data = []
        self.all_components = {}  # Dictionary to store all components

        # Create toolbars first
        self.create_main_toolbar()
        self.create_secondary_toolbar()

        # Now load BOM data
        self.load_bom_data()
        
        # Bind events
        self.canvas.bind("<Motion>", self.update_coordinates)
        self.bind("<Configure>", self.on_window_resize)
        
        # Create coordinate labels
        self.create_coordinate_labels()
        
    def create_coordinate_labels(self):
        self.coord_frame = tk.Frame(self.canvas, bg="black")
        self.coord_frame.place(relx=1, rely=1, anchor="se", x=-10, y=-10)
        
        self.x_coord_label = tk.Label(self.coord_frame, text="X: 0.00 mm", fg="white", bg="black")
        self.x_coord_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.y_coord_label = tk.Label(self.coord_frame, text="Y: 0.00 mm", fg="white", bg="black")
        self.y_coord_label.pack(side=tk.LEFT)

    def set_file_paths(self):
        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Set default paths
        self.pcbdata_path = os.path.join(current_dir, "pcbdata.csv")
        self.footprints_path = os.path.join(current_dir, "footprints.csv")
        
        # Check if files exist, if not, prompt user to select them
        if not os.path.exists(self.pcbdata_path):
            messagebox.showwarning("File Not Found", "pcbdata.csv not found in the script directory.")
            self.pcbdata_path = filedialog.askopenfilename(title="Select pcbdata.csv", filetypes=[("CSV files", "*.csv")])
        
        if not os.path.exists(self.footprints_path):
            messagebox.showwarning("File Not Found", "footprints.csv not found in the script directory.")
            self.footprints_path = filedialog.askopenfilename(title="Select footprints.csv", filetypes=[("CSV files", "*.csv")])


    def create_main_toolbar(self):
        self.toolbar = tk.Frame(self.canvas, bg="grey")
        self.toolbar.place(x=10, y=10)

        buttons = [
            ("Load PCB", self.load_pcb),
            ("Footprints", self.show_footprints),
            ("PCB Outline", self.set_pcb_outline),
            ("Place PCB", self.place_pcb),
            ("Place Components", self.place_components),
            ("Rotate PCB", self.rotate_pcb),
            ("Toggle Fill", self.toggle_pcb_fill)
        ]

        for text, command in buttons:
            button = tk.Button(self.toolbar, text=text, command=command)
            button.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X)

        self.toolbar.bind("<ButtonPress-1>", self.start_drag_toolbar)
        self.toolbar.bind("<B1-Motion>", self.drag_toolbar)
    
    def toggle_pcb_fill(self):
        if self.pcb_rect:
            current_fill = self.canvas.itemcget(self.pcb_rect, "fill")
            new_fill = "" if current_fill else "lightgrey"
            self.canvas.itemconfig(self.pcb_rect, fill=new_fill)
    
    def start_drag_toolbar(self, event):
        self._drag_data_toolbar = {'x': event.x, 'y': event.y}
    
    def drag_toolbar(self, event):
        dx = event.x - self._drag_data_toolbar['x']
        dy = event.y - self._drag_data_toolbar['y']
        new_x = self.toolbar.winfo_x() + dx
        new_y = self.toolbar.winfo_y() + dy
        self.toolbar.place(x=new_x, y=new_y)

    def create_secondary_toolbar(self):
        self.secondary_toolbar = tk.Frame(self.canvas, bg="grey")
        self.secondary_toolbar.place(x=150, y=50)

        # Create a sub-frame for the buttons
        button_frame = tk.Frame(self.secondary_toolbar, bg="grey")
        button_frame.pack(padx=5, pady=5)

        self.fill_button = tk.Checkbutton(button_frame, text="Fill Footprints", 
                                           variable=self.fill_var, command=self.toggle_footprint_fill)
        self.fill_button.pack(side=tk.LEFT, padx=5)

        self.names_button = tk.Checkbutton(button_frame, text="Show Names", 
                                           variable=self.names_var, command=self.toggle_component_names)
        self.names_button.pack(side=tk.LEFT, padx=5)

        self.shapes_button = tk.Checkbutton(button_frame, text="Show Shapes", 
                                            variable=self.shapes_var, command=self.toggle_component_shapes)
        self.shapes_button.pack(side=tk.LEFT, padx=5)

        # Add page navigation buttons and label
        self.prev_button = tk.Button(button_frame, text="Previous", command=self.previous_page)
        self.prev_button.pack(side=tk.LEFT, padx=5)

        self.page_label = tk.Label(button_frame, text="Page 0 of 0", bg="grey")
        self.page_label.pack(side=tk.LEFT, padx=5)

        self.next_button = tk.Button(button_frame, text="Next", command=self.next_page)
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        self.secondary_toolbar.bind("<ButtonPress-1>", self.start_drag_secondary_toolbar)
        self.secondary_toolbar.bind("<B1-Motion>", self.drag_secondary_toolbar)

    def toggle_footprint_fill(self):
        for item in self.canvas.find_withtag("component_shape"):
            fill = "white" if self.fill_var.get() else ""
            self.canvas.itemconfig(item, fill=fill)

    def toggle_component_names(self):
        state = "normal" if self.names_var.get() else "hidden"
        for item in self.canvas.find_withtag("component_text"):
            self.canvas.itemconfig(item, state=state)

    def toggle_component_shapes(self):
        state = "normal" if self.shapes_var.get() else "hidden"
        for item in self.canvas.find_withtag("component_shape"):
            self.canvas.itemconfig(item, state=state)

    def start_drag_secondary_toolbar(self, event):
        self._drag_data_secondary_toolbar = {'x': event.x, 'y': event.y}

    def drag_secondary_toolbar(self, event):
        dx = event.x - self._drag_data_secondary_toolbar['x']
        dy = event.y - self._drag_data_secondary_toolbar['y']
        new_x = self.secondary_toolbar.winfo_x() + dx
        new_y = self.secondary_toolbar.winfo_y() + dy
        self.secondary_toolbar.place(x=new_x, y=new_y)

    def load_pcb(self):
        script_path = r"readpickandplace.py"
        try:
            result = subprocess.run(["python", script_path], capture_output=True, text=True, check=True)
            messagebox.showinfo("Success", "PCB data loaded successfully.\n" + result.stdout)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to load PCB data.\nError: {e.stderr}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def show_footprints(self):
        footprint_window = tk.Toplevel(self)
        footprint_window.title("Footprints")
        footprint_window.geometry("400x300")

        tree = ttk.Treeview(footprint_window, columns=("Footprint", "Action"), show="headings")
        tree.heading("Footprint", text="Footprint")
        tree.heading("Action", text="Action")
        tree.pack(fill=tk.BOTH, expand=True)

        existing_footprints = self.get_existing_footprints()

        # Create a style
        style = ttk.Style()
        style.configure("Add.Treeview", background="light coral")
        style.configure("Modify.Treeview", background="light green")

        pcb_data = self.read_pcb_data()
        if pcb_data:
            unique_footprints = set(component['Footprint'] for component in pcb_data if 'Footprint' in component)
            for footprint in unique_footprints:
                action = "Modify" if footprint in existing_footprints else "Add"
                item = tree.insert("", "end", values=(footprint, action))
                
                # Set the tag for the item based on the action
                tree.item(item, tags=(action,))

        # Apply the styles
        tree.tag_configure("Add", background="light coral")
        tree.tag_configure("Modify", background="light green")

        tree.bind("<Double-1>", lambda event: self.handle_footprint_action(tree))

    def get_footprints(self):
        footprints = set()
        try:
            with open(self.pcbdata_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    footprints.add(row["Footprint"])
        except FileNotFoundError:
            messagebox.showerror("Error", f"pcbdata.csv not found at {self.pcbdata_path}. Please load PCB data first.")
        return sorted(footprints)

    def get_existing_footprints(self):
        existing_footprints = set()
        try:
            with open(self.footprints_path, "r") as f:
                reader = csv.reader(f)
                # Check if the file is not empty before trying to skip the header
                first_row = next(reader, None)
                if first_row is not None:
                    # If it's not the header, add it to existing_footprints
                    if first_row != ["Name", "Shape", "Width", "Height", "CenterX", "CenterY"]:
                        existing_footprints.add(first_row[0])
                    # Read the rest of the rows
                    for row in reader:
                        existing_footprints.add(row[0])
        except FileNotFoundError:
            pass  # It's okay if the file doesn't exist yet
        return existing_footprints

    def handle_footprint_action(self, tree):
        selected_item = tree.selection()[0]
        footprint, action = tree.item(selected_item)["values"]
        
        dialog = FootprintDialog(self, footprint, action == "Add")
        self.wait_window(dialog)
        
        if dialog.result:
            self.save_footprint(dialog.result)
            messagebox.showinfo("Success", f"Footprint '{footprint}' has been {action.lower()}ed.")
            tree.item(selected_item, values=(footprint, "Modify"), tags=("Modify",))
            tree.tag_configure("Modify", background="light green")

    def save_footprint(self, data):
        if data is None:
            print("No data to save")
            return
        
        file_exists = os.path.isfile(self.footprints_path)
        mode = "a" if file_exists else "w"
        with open(self.footprints_path, mode, newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Name", "Shape", "Width", "Height", "CenterX", "CenterY"])
            writer.writerow([data["name"], data["shape"], data["width"], data["height"], data["center_x"], data["center_y"]])
        print(f"Footprint saved to {self.footprints_path}")

    def set_pcb_outline(self):
        dialog = PCBOutlineDialog(self)
        self.wait_window(dialog)
        if dialog.result:
            self.original_pcb_width, self.original_pcb_length = dialog.result
            self.pcb_width, self.pcb_length = self.original_pcb_width, self.original_pcb_length
            messagebox.showinfo("PCB Outline", f"PCB outline set to {self.pcb_width}mm x {self.pcb_length}mm")

    def place_pcb(self):
        if self.pcb_width is None or self.pcb_length is None:
            messagebox.showerror("Error", "Please set PCB outline first.")
            return

        # Remove existing PCB rectangle and anchors
        if self.pcb_rect:
            self.canvas.delete(self.pcb_rect)
        for anchor in self.pcb_anchors:
            self.canvas.delete(anchor)

        # Use the default position
        x1, y1 = 250, 100
        x2 = x1 + self.pcb_width
        y2 = y1 + self.pcb_length

        self.pcb_rect = self.canvas.create_rectangle(x1, y1, x2, y2, outline="green", width=2, fill="", tags="pcb")
        self.pcb_outline = [x1, y1, x2, y2]

        # Create anchor points
        self.pcb_anchors = [
            self.canvas.create_oval(x1-5, y2-5, x1+5, y2+5, fill="red", outline="red", tags="pcb_anchor_origin"),
            self.canvas.create_oval(x2-5, y2-5, x2+5, y2+5, fill="blue", outline="blue", tags="pcb_anchor"),
            self.canvas.create_oval(x2-5, y1-5, x2+5, y1+5, fill="blue", outline="blue", tags="pcb_anchor"),
            self.canvas.create_oval(x1-5, y1-5, x1+5, y1+5, fill="blue", outline="blue", tags="pcb_anchor")
        ]
        self.canvas.tag_bind("pcb_anchor_origin", "<ButtonPress-1>", self.start_move_pcb)
        self.canvas.tag_bind("pcb_anchor_origin", "<B1-Motion>", self.moving_pcb)
        self.canvas.tag_bind("pcb_anchor", "<ButtonPress-1>", self.start_resize_pcb)
        self.canvas.tag_bind("pcb_anchor", "<B1-Motion>", self.resizing_pcb)

        print(f"PCB placed: {self.pcb_width}mm x {self.pcb_length}mm")
        print(f"PCB outline (pixels): {self.pcb_outline}")

    def start_move_pcb(self, event):
        self._drag_data = {'x': event.x, 'y': event.y, 'item': event.widget.find_withtag("current")[0]}

    def moving_pcb(self, event):
        delta_x = event.x - self._drag_data['x']
        delta_y = event.y - self._drag_data['y']
        
        # Move the PCB rectangle and all anchors
        self.canvas.move("pcb", delta_x, delta_y)
        self.canvas.move("pcb_anchor", delta_x, delta_y)
        self.canvas.move("pcb_anchor_origin", delta_x, delta_y)
        self.canvas.move("component", delta_x, delta_y)  # Move components with PCB
        
        # Update PCB outline coordinates
        self.pcb_outline = [coord + (delta_x if i % 2 == 0 else delta_y) for i, coord in enumerate(self.pcb_outline)]
        
        self._drag_data['x'] = event.x
        self._drag_data['y'] = event.y

        # Update coordinates display
        self.update_coordinates(event)

    def start_resize_pcb(self, event):
        self._resize_data = {'x': event.x, 'y': event.y, 'item': event.widget.find_withtag("current")[0]}

    def resizing_pcb(self, event):
        delta_x = event.x - self._resize_data['x']
        delta_y = event.y - self._resize_data['y']
        
        anchor = self._resize_data['item']
        anchor_index = self.pcb_anchors.index(anchor)
        
        x1, y1, x2, y2 = self.pcb_outline
        
        if anchor_index == 1:  # Bottom-right
            x2 += delta_x
            y2 += delta_y
        elif anchor_index == 2:  # Top-right
            x2 += delta_x
            y1 += delta_y
        elif anchor_index == 3:  # Top-left
            x1 += delta_x
            y1 += delta_y
        
        # Ensure minimum size
        if x2 - x1 < 10 or y2 - y1 < 10:
            return
        
        self.canvas.coords(self.pcb_rect, x1, y1, x2, y2)
        self.pcb_outline = [x1, y1, x2, y2]
        
        # Update anchor positions
        self.canvas.coords(self.pcb_anchors[0], x1-5, y2-5, x1+5, y2+5)
        self.canvas.coords(self.pcb_anchors[1], x2-5, y2-5, x2+5, y2+5)
        self.canvas.coords(self.pcb_anchors[2], x2-5, y1-5, x2+5, y1+5)
        self.canvas.coords(self.pcb_anchors[3], x1-5, y1-5, x1+5, y1+5)
        
        # Update PCB dimensions
        self.pcb_width = x2 - x1
        self.pcb_length = y2 - y1
        
        # Rescale components
        self.rescale_components()
        
        self._resize_data['x'] = event.x
        self._resize_data['y'] = event.y

        # Update coordinates display
        self.update_coordinates(event)

    def place_components(self):
        print("Starting place_components method")
        if self.pcb_outline is None:
            messagebox.showerror("Error", "Please set PCB outline and place PCB first.")
            return

        current_width, current_length = get_pcb_dimensions(self.pcb_outline)
        scale_x, scale_y = calculate_scale_factor(self.original_pcb_width, self.original_pcb_length, current_width, current_length)

        pcb_data = self.read_pcb_data()
        footprints = self.read_footprints()
        
        if not pcb_data or not footprints:
            messagebox.showerror("Error", "Failed to read PCB data or footprints.")
            return

        print("PCB data and footprints loaded successfully.")
        print(f"Number of components: {len(pcb_data)}")
        print(f"Number of footprints: {len(footprints)}")

        # Clear previous components
        self.canvas.delete("component")

        print(f"PCB outline: {self.pcb_outline}")
        print(f"Scale factors: x={scale_x}, y={scale_y}")

        # Set origin to bottom-left corner of PCB (canvas coordinate system)
        origin_x = self.pcb_outline[0]
        origin_y = self.pcb_outline[3]

        missing_footprints = set()
        plotted_components = 0

        self.all_components.clear()  # Clear previous components

        # Plot components
        for component in pcb_data:
            footprint_name = component.get('Footprint', '')
            normalized_footprint_name = re.sub(r'[^a-zA-Z0-9]', '', footprint_name.lower())
            
            # Try to find a matching footprint
            footprint = None
            for fp_name, fp_data in footprints.items():
                if normalized_footprint_name in re.sub(r'[^a-zA-Z0-9]', '', fp_name.lower()):
                    footprint = fp_data
                    break
            
            if footprint:
                try:
                    # Replace comma with period and convert to float
                    comp_x = float(component['Center-X(mm)'].replace(',', '.'))
                    comp_y = float(component['Center-Y(mm)'].replace(',', '.'))
                    rotation = float(component.get('Rotation', '0').replace(',', '.'))
                    
                    # Scale component position
                    scaled_x, scaled_y = scale_component_position(comp_x, comp_y, scale_x, scale_y)
                    
                    # Convert mm to pixels and adjust coordinates to start from bottom-left corner
                    x = origin_x + scaled_x
                    y = origin_y - scaled_y  # Subtract because canvas Y increases downwards
                    
                    print(f"Plotting component: {component.get('Designator', '')}")
                    print(f"  Original position: ({comp_x}, {comp_y}), Scaled position: ({scaled_x}, {scaled_y})")
                    print(f"  Canvas position: ({x}, {y}), Rotation: {rotation}")
                    
                    fill_color = "white" if self.fill_var.get() else ""
                    if footprint['Shape'].lower() == 'rectangle':
                        width = float(footprint['Width']) * scale_x
                        height = float(footprint['Height']) * scale_y
                        shape_item = self.create_rotated_rectangle(x, y, width, height, rotation, fill=fill_color, outline="yellow", tags=("component", "component_shape"))
                    elif footprint['Shape'].lower() == 'circle':
                        diameter = float(footprint['Width']) * scale_x
                        shape_item = self.canvas.create_oval(x - diameter/2, y - diameter/2, x + diameter/2, y + diameter/2,
                                                outline="yellow", fill=fill_color, tags=("component", "component_shape"))
                    else:
                        print(f"Unknown shape for footprint {footprint_name}: {footprint['Shape']}")
                        continue
                    
                    text_state = "normal" if self.names_var.get() else "hidden"
                    text_item = self.create_rotated_text(x, y, component.get('Designator', ''), rotation, fill="white", tags=("component", "component_text"), state=text_state)
                    self.adjust_text_orientation(text_item)
                    
                    plotted_components += 1

                    # Store the component items
                    designator = component.get('Designator', '')
                    self.all_components[designator] = {
                        'shape': shape_item,
                        'text': text_item
                    }
                except (KeyError, ValueError) as e:
                    print(f"Error plotting component {component.get('Designator', '')}: {e}")
            else:
                missing_footprints.add(footprint_name)

        print(f"Plotted {plotted_components} components")
        print(f"Missing footprints: {len(missing_footprints)}")
        print("First 10 missing footprints:")
        for footprint in list(missing_footprints)[:10]:
            print(f"  {footprint}")

        self.debug_print()

        # After placing components, update the page label and highlight components
        self.update_page_label()
        self.highlight_components()

    def create_rotated_rectangle(self, x, y, width, height, angle, **kwargs):
        points = [
            (-width/2, -height/2),
            (width/2, -height/2),
            (width/2, height/2),
            (-width/2, height/2)
        ]
        
        cos_val = math.cos(math.radians(angle))
        sin_val = math.sin(math.radians(angle))
        
        rotated_points = []
        for px, py in points:
            rx = px * cos_val - py * sin_val + x
            ry = px * sin_val + py * cos_val + y
            rotated_points.append(rx)
            rotated_points.append(ry)
        
        return self.canvas.create_polygon(rotated_points, **kwargs)

    def create_rotated_text(self, x, y, text, angle, **kwargs):
        text_item = self.canvas.create_text(x, y, text=text, angle=angle, **kwargs)
        return text_item

    def read_pcb_data(self):
        if not self.pcbdata_path or not os.path.exists(self.pcbdata_path):
            messagebox.showerror("Error", "PCB data file not found. Please set the correct path.")
            return None
        
        pcb_data = []
        try:
            with open(self.pcbdata_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    pcb_data.append(row)
            if not pcb_data:
                raise ValueError("PCB data is empty")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read PCB data: {str(e)}")
            return None
        return pcb_data

    def read_footprints(self):
        if not self.footprints_path or not os.path.exists(self.footprints_path):
            messagebox.showerror("Error", "Footprints file not found. Please set the correct path.")
            return None
        
        footprints = {}
        try:
            with open(self.footprints_path, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                for row in reader:
                    if len(row) < 6:
                        print(f"Warning: Invalid row format: {row}")
                        continue
                    name = row[0]
                    footprints[name] = {
                        'Shape': row[1],
                        'Width': row[2],
                        'Height': row[3],
                        'CenterX': row[4],
                        'CenterY': row[5]
                    }
            if not footprints:
                raise ValueError("Footprints data is empty")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read footprints: {str(e)}")
            return None
        return footprints

    def debug_print(self):
        print(f"PCB Outline: {self.pcb_outline}")
        print(f"PCB Dimensions: {self.pcb_width}mm x {self.pcb_length}mm")
        
        pcb_data = self.read_pcb_data()
        if pcb_data:
            print("First 5 components:")
            for component in pcb_data[:5]:
                print(f"  {component}")
        else:
            print("No PCB data available")

        footprints = self.read_footprints()
        if footprints:
            print("First 5 footprints:")
            for name, data in list(footprints.items())[:5]:
                print(f"  {name}: {data}")
        else:
            print("No footprint data available")

    def rotate_pcb(self):
        if not self.pcb_outline:
            messagebox.showerror("Error", "Please place the PCB first.")
            return

        # Calculate the center of the PCB
        center_x = (self.pcb_outline[0] + self.pcb_outline[2]) / 2
        center_y = (self.pcb_outline[1] + self.pcb_outline[3]) / 2

        # Rotate the PCB outline
        self.canvas.delete("pcb")
        rotated_outline = self.rotate_points(self.pcb_outline, center_x, center_y, 90)
        self.pcb_rect = self.canvas.create_polygon(rotated_outline, outline="green", width=2, fill="", tags="pcb")

        # Rotate the PCB anchors
        for anchor in self.pcb_anchors:
            self.canvas.delete(anchor)
        self.pcb_anchors = []
        for i in range(0, len(rotated_outline), 2):
            x, y = rotated_outline[i], rotated_outline[i+1]
            anchor = self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="blue", outline="blue", tags="pcb_anchor")
            self.pcb_anchors.append(anchor)

        # Rotate all components
        for item in self.canvas.find_withtag("component"):
            item_type = self.canvas.type(item)
            
            if item_type == "polygon":  # Rotated rectangle
                coords = self.canvas.coords(item)
                rotated_coords = self.rotate_points(coords, center_x, center_y, 90)
                self.canvas.coords(item, *rotated_coords)
            elif item_type == "oval":  # Circle
                coords = self.canvas.coords(item)
                x1, y1, x2, y2 = coords
                center_x_item = (x1 + x2) / 2
                center_y_item = (y1 + y2) / 2
                rotated_center = self.rotate_point(center_x_item, center_y_item, center_x, center_y, 90)
                radius = (x2 - x1) / 2
                self.canvas.coords(item, rotated_center[0]-radius, rotated_center[1]-radius,
                                 rotated_center[0]+radius, rotated_center[1]+radius)
            elif item_type == "text":  # Component designator
                x, y = self.canvas.coords(item)
                rotated_point = self.rotate_point(x, y, center_x, center_y, 90)                
                self.canvas.coords(item, *rotated_point)
                current_angle = float(self.canvas.itemcget(item, "angle"))
                new_angle = (current_angle + 90) % 360
                self.canvas.itemconfig(item, angle=new_angle)
                self.adjust_text_orientation(item)

        # Update PCB outline
        self.pcb_outline = rotated_outline

        # Swap PCB width and length
        self.pcb_width, self.pcb_length = self.pcb_length, self.pcb_width

        # Update coordinates display
        self.update_coordinates(None)  # Pass None instead of tk.Event()

    def adjust_text_orientation(self, text_item):
        angle = float(self.canvas.itemcget(text_item, "angle"))
        if 90 < angle <= 270:
            # Flip the text if it's upside down
            new_angle = (angle + 180) % 360
            self.canvas.itemconfig(text_item, angle=new_angle)

    def rotate_points(self, points, center_x, center_y, angle):
        rotated_points = []
        for i in range(0, len(points), 2):
            x, y = points[i], points[i+1]
            rotated_point = self.rotate_point(x, y, center_x, center_y, angle)
            rotated_points.extend(rotated_point)
        return rotated_points

    def rotate_point(self, x, y, center_x, center_y, angle):
        angle_rad = math.radians(angle)
        cos_val = math.cos(angle_rad)
        sin_val = math.sin(angle_rad)
        dx = x - center_x
        dy = y - center_y
        new_x = center_x + dx * cos_val - dy * sin_val
        new_y = center_y + dx * sin_val + dy * cos_val
        return (new_x, new_y)

    def update_coordinates(self, event):
        if self.pcb_outline:
            # Calculate scale (pixels per mm)
            pcb_width_px = self.pcb_outline[2] - self.pcb_outline[0]
            scale = pcb_width_px / self.pcb_width

            # Calculate PCB origin (bottom-left corner)
            origin_x = self.pcb_outline[0]
            origin_y = self.pcb_outline[3]

            # Calculate mouse position relative to PCB origin
            x_mm = (event.x - origin_x) / scale
            y_mm = (origin_y - event.y) / scale

            # Update labels
            self.x_coord_label.config(text=f"X: {x_mm:.2f} mm")
            self.y_coord_label.config(text=f"Y: {y_mm:.2f} mm")
        else:
            # If PCB is not placed, show canvas coordinates
            self.x_coord_label.config(text=f"X: {event.x} px")
            self.y_coord_label.config(text=f"Y: {event.y} px")

    def on_window_resize(self, event):
        # Update the position of the coordinate frame
        self.coord_frame.place(relx=1, rely=1, anchor="se", x=-10, y=-10)

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page_label()
            self.highlight_components()

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_page_label()
            self.highlight_components()

    def highlight_components(self):
        # Hide all components first
        for component in self.all_components.values():
            self.canvas.itemconfig(component['shape'], state='hidden')
            self.canvas.itemconfig(component['text'], state='hidden')

        if self.current_page == 0:
            # Show all components for the setup page
            for component in self.all_components.values():
                self.canvas.itemconfig(component['shape'], state='normal', outline='yellow', width=1)
                self.canvas.itemconfig(component['text'], state='normal')
            return

        # Show and highlight components for the current page
        current_row = self.bom_data[self.current_page - 1]
        designators = current_row.get('Designator', '').split(',')
        for designator in designators:
            designator = designator.strip()
            if designator in self.all_components:
                component = self.all_components[designator]
                self.canvas.itemconfig(component['shape'], state='normal', outline='red', width=2)
                self.canvas.itemconfig(component['text'], state='normal')

    def load_bom_data(self):
        if not hasattr(self, 'pcbdata_path') or not self.pcbdata_path:
            messagebox.showwarning("Warning", "PCB data path not set. BOM data cannot be loaded.")
            return

        bom_path = os.path.join(os.path.dirname(self.pcbdata_path), "BOM.csv")
        try:
            with open(bom_path, 'r') as f:
                reader = csv.DictReader(f)
                self.bom_data = list(reader)
            self.total_pages = len(self.bom_data) + 1  # +1 for the setup page
            self.update_page_label()
        except FileNotFoundError:
            messagebox.showerror("Error", f"BOM.csv not found at {bom_path}")

    def update_page_label(self):
        self.page_label.config(text=f"Page {self.current_page + 1} of {self.total_pages}")

    def rescale_components(self):
        if not self.pcb_outline:
            return

        old_width = self.pcb_outline[2] - self.pcb_outline[0]
        old_height = self.pcb_outline[3] - self.pcb_outline[1]
        scale_x = self.pcb_width / old_width
        scale_y = self.pcb_length / old_height

        origin_x, origin_y = self.pcb_outline[0], self.pcb_outline[3]  # Bottom-left corner

        for item in self.canvas.find_withtag("component"):
            coords = self.canvas.coords(item)
            new_coords = []
            for i, coord in enumerate(coords):
                if i % 2 == 0:  # X coordinate
                    new_coords.append(origin_x + (coord - origin_x) * scale_x)
                else:  # Y coordinate
                    new_coords.append(origin_y + (coord - origin_y) * scale_y)
            self.canvas.coords(item, *new_coords)

        self.canvas.update()

if __name__ == "__main__":
    app = ProjectionGUI()
    app.mainloop()
