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
- 

