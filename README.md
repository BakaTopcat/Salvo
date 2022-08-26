# Salvo
Python script which reads and writes the Blackmagic Videohub state and saves it to file.

This script is very raw and untested, I'd suggest not using it in production.

Any commits/comments/tests/bugreports/discussions appreciated [here](https://github.com/BakaTopcat/Salvo/discussions)

Features:
- GUI interface (tkinter)
- Dynamic router size, read either from file or from router, no need to enter it manually
- Max router size 256x256
- Currently only square routers supported
- Read from file, save to file
- Automatic file name suggestion according to date and time
- Router size and access address saved to file along with all the crosspoints
- All the router crosspoints displayed in the textbox
- Command line window with timestamps and lot of debug information

To-do:
- Locked crosspoints handling
- Thorough testing
- Bug checking
- Making code neat and tidy
- More comments
- More exception handling
- Snell SW-P-08 protocol implementing (serial port)
