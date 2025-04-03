# Introduction
While waiting for my PCBs to arrive after placing an order, I decided to use the downtime to experiment with a side idea I'd had for a while. The goal: build a simple tool to make manual PCB assembly easier without spending too much time or effort on it.

I wanted to avoid the usual back-and-forth between BOMs and assembly drawings, and instead project the PCB layout directly onto a table. That way, I could align a real PCB with the projection, scale it as needed, and cycle through components page by page, visually highlighting where each one goes.

Around that same time, I started using Cursor, which is basically VS Code but with an integrated AI assistant that understands your codebase. To save some time and brain power I tried to build the entire using mostly the AI, writing mostly pseudocode and letting the AI handle the actual implementation.

The result is a quick-and-dirty but surprisingly functional GUI app that:
- Projects a scaled virtual PCB onto a physical one
- Loads BOM and component data
- Lets you step through components visually for manual pick-and-place

Definitely not polished, but it works—and it was a fun way to see how far you can push AI-assisted development and the extra 7 minutes of assembly it saved me was definitely worth it!
This was made in mid 2024 and only adding it to GitHub 3/4/25 details might be incorrect.

# How it works ?

- Output the Pick and place data form Altium and save it to the project folder as "inputdata.csv"
- Open the GUI
![Screenshot 2025-04-03 150922](https://github.com/user-attachments/assets/56867e21-c257-45c3-aae5-063b184f6ca9)
- Press "Load PCB" this trannslates the pick and place to PCB data (not sure why I did this but there was probably a reason, not a good one, but a reason). A popup should let you know things went well.
- You can then click on the "Footrpints" This opens a submenu where you have a list of components, If they are in red you can select it to add the footprint.
Image
- This is either a rectangle(or Square) or a Circle. You input the dimensions of the component and save it. This is just an outline of your Resistors,Caps, ICs, Pin header ETC. This 'Footprint" is what will be displayed as the componnent using the positional data from the pick and place.
- Once all the footprints are green you can press the "PCB Outline", this is where you put the max dimensions of your PCB Length and Width. This creates the rectangle that is projected onto the table to align with the PCB.
- Press "Place PCB" and a Rectangle/Square appears with three blue corners and one red corner. The blue corners can skew and scale while the red corner is used to move the PCB.
- At this point you can click the "Toggle Fill" button that fills the PCB with white, this allows you to more easily align the virtual PCB and real PCB. Would make sense to move that button up but this project is currently deployed with no scope for future work.
- Once the alignment is done you can press "Place Componennts" this places all component outlines along with their designators. I would recomend checking the box that says "Fill Footrpints", this highlits all components so you can check that they all line up.
- I do not remember if the "Rotate PCB" works.
- You will notice you are currently on Page 1 of 50 or X. Pressing "Next" moves onto the first line of your BOM, this means it only shows all components on the first line and removes the other components.

