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
![Screenshot 2025-04-03 151842](https://github.com/user-attachments/assets/0a061af0-2151-45da-8ebc-712783f5ecc9)
- This is either a rectangle(or Square) or a Circle. You input the dimensions of the component and save it. This is just an outline of your Resistors,Caps, ICs, Pin header ETC. This 'Footprint" is what will be displayed as the componnent using the positional data from the pick and place.
![Screenshot 2025-04-03 151912](https://github.com/user-attachments/assets/2d08b016-3ca2-4c90-9083-10a5ecb393fa)
- Once all the footprints are green you can press the "PCB Outline", this is where you put the max dimensions of your PCB Length and Width. This creates the rectangle that is projected onto the table to align with the PCB.
![Screenshot 2025-04-03 151936](https://github.com/user-attachments/assets/91a8847a-e223-4b27-a984-0b5859117e7e)
- Press "Place PCB" and a Rectangle/Square appears with three blue corners and one red corner. The blue corners can skew and scale while the red corner is used to move the PCB.
![Screenshot 2025-04-03 151953](https://github.com/user-attachments/assets/66b0a962-ab6d-43c7-8c52-d46bb7eb1f52)
- At this point you can click the "Toggle Fill" button that fills the PCB with white, this allows you to more easily align the virtual PCB and real PCB. Would make sense to move the Toggle Fill button up but this project is currently deployed with no scope for future work.
![Screenshot 2025-04-03 152033](https://github.com/user-attachments/assets/7665cf08-6e86-4469-a6a7-8436ef5a1d87)
- Once the alignment is done you can press "Place Componennts" this places all component outlines along with their designators. 
![Screenshot 2025-04-03 152005](https://github.com/user-attachments/assets/f4c3b141-e716-404a-b07d-fb4dc2dfcd19)
- I would recomend checking the box that says "Fill Footrpints", this highlits all components so you can check that they all line up.
![Screenshot 2025-04-03 152046](https://github.com/user-attachments/assets/7c398b09-8e4a-4dc2-a7ad-5460c93e4453)
- I do not remember if the "Rotate PCB" works.
- You will notice you are currently on Page 1 of 50 or X. Pressing "Next" moves onto the first line of your BOM, this means it only shows all components on the first line and removes the other components.
![Screenshot 2025-04-03 152059](https://github.com/user-attachments/assets/1de41c3f-af3d-4388-81a2-8b4304ec13cc)
![Screenshot 2025-04-03 152128](https://github.com/user-attachments/assets/e089c825-3acc-4bb8-8e64-c93c6d2869a1)
