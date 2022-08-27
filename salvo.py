# Reads and restores the video router snapshots
# Works with Blackmagic Videohub
# Originally created by Kirill Ageyev, ageyev.k@gmail.com
# 2022

import time
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import scrolledtext
from tkinter import messagebox
from Router import Router

window = tk.Tk()
# this needed for router state textbox
router_state_columns = 8

router = Router()


def router1_write(router_state: bytearray):
    global router_size  # do we really need to declare global variable? TO-DO: check this out
    if messagebox.askyesno(title="Confirmation", message="Confirm router overwrite?"):
        time.sleep(0.4)
        router.write_state(router_state)
        print(f"[{time.ctime()}] Router updated")
    else:
        print(f"[{time.ctime()}] Router overwrite canceled")


# TO-DO
def router1_read():
    router.read_state()
    router_state_update(router)


# this needed for file open/save dialogs
filetypes = (("BIN files", "*.bin"), ("All files", "*.*"))

# .bin file format:
# first 2 bytes: router size (integer, big endian)
# then 256 bytes of router sources per destination
# then the ip address until EOF
# TO-DO: check whether COMx is okay too


def load_from_file():
    filename = fd.askopenfilename(filetypes=filetypes)
    if filename:
        # received file name, let's open the file
        # TO-DO: wrap this into try..except statement
        newfile = open(filename, "rb")
        router_size = int.from_bytes(newfile.read(2), "big")
        # otherwise it will convert bytearray to bytes, need to strictly specify
        router_state = bytearray(newfile.read(256))
        router_ip = newfile.read().decode()
        newfile.close()
        router = Router(router_ip)
        router.write_state(router_state)
        print(f"[{time.ctime()}] {filename} loaded successfully")
        print(
            f"[{time.ctime()}] Router size read from file: {router_size}; Access path: {router_ip}")
        # print(router_state) # debug
        # updating the textbox
        router_state_update(router)
        return router
    else:
        print(f"[{time.ctime()}] File opening dialog canceled")
        return None


def fil_open():
    global router
    router = load_from_file()


def fil_saveas(router: Router):
    # global router_size
    # there is no need to declare a global for a variable which you only read
    # default file name, we create it based on current date and time
    def_fn = time.strftime("%y%m%d-%H%M", time.localtime())
    filename = fd.asksaveasfilename(
        initialfile=def_fn, defaultextension=".bin", filetypes=filetypes
    )
    if filename:
        # TO-DO: wrap this into try..except statement
        newfile = open(filename, "wb")
        newfile.write(router.router_size.to_bytes(2, "big"))
        newfile.write(router.read_state())
        newfile.write(router.router_ip)
        newfile.close
        print(
            f"[{time.ctime()}] {filename} saved successfully, router size {router.router_size}")
    else:
        print(f"[{time.ctime()}] Saving to file canceled")


# update the GUI text boxes
def router_state_update(router: Router):
    # global router_size
    # there is no need to declare a global for a variable which you only read
    # we assume router_size is dividable by router_state_columns without remainder
    router_state_rows = router.router_size // router_state_columns
    e_ip_text.set(router.router_ip)                    # update IP field
    t_router_state.config(state=tk.NORMAL)    # enable textbox

    router_state = router.read_state()

#    t_router_state.tag_configure('yll', background='yellow') # yellow background for changed values

    t_router_state.delete(1.0, tk.END)          # erase the text box contents
    for j in range(router_state_rows):
        for i in range(router_state_columns):
            i_dest = i * router_state_rows + j
#           t_router_state.insert(tk.END, f"{i_dest+1:03d}:", 'yll') # yellow background for changed values
            t_router_state.insert(tk.END, f"{i_dest+1:03d}:")
            i_src = router_state[i_dest]
            t_router_state.insert(tk.END, f"{i_src+1:03d} ")
    t_router_state.config(state=tk.DISABLED)    # disable textbox


# ------ TKINTER PACK STARTS HERE ------
f_file = tk.LabelFrame(window, text="File")
f_file.pack(expand=0, fill="both")

b_open = tk.Button(f_file, text="Open...", command=fil_open)
b_open.pack(side="left", padx=3, pady=3)
b_saveas = tk.Button(f_file, text="Save As...",
                     command=lambda: fil_saveas(router))
b_saveas.pack(side="left", padx=3, pady=3)
# l_file = tk.Label(f_file, text="no file loaded")
# l_file.pack(side="left", padx=3, pady=3)

f_router1 = tk.LabelFrame(window, text="Router Control")
f_router1.pack(expand=0, fill="both")

b_read1 = tk.Button(f_router1, text="Read", command=router1_read)
b_read1.pack(side="left", expand=0, fill="both", padx=3, pady=3)
b_write1 = tk.Button(f_router1, text="Write", command=router1_write)
b_write1.pack(side="left", expand=0, fill="both", padx=3, pady=3)
e_ip_text = tk.StringVar()
e_ip = tk.Entry(f_router1, textvariable=e_ip_text)
e_ip.pack(side="left", expand=0, fill="both", padx=3, pady=3)

f_router_state = tk.LabelFrame(window, text="Router State")
f_router_state.pack(expand=0, fill="both")

# height and width are in chars!!!
# one xpt 'dst:src ' = 8 chars, the router state has router_state_columns xpt's width
t_router_state = scrolledtext.ScrolledText(
    f_router_state, height=16, width=router_state_columns * 8
    #    f_router_state, height=router_state_rows, width=router_state_columns * 8
)
t_router_state.pack(side="left", expand=0, fill="both", padx=3, pady=3)
# ------ TKINTER PACK ENDS HERE ------

# one-time execution
router_state_update(router)

# main loop
window.mainloop()
