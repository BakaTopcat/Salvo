# Reads and restores the video router snapshots
# Works with Blackmagic Videohub
# Originally created by Kirill Ageyev, ageyev.k@gmail.com
# 2022

import time
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import scrolledtext
from tkinter import messagebox

# Videohub
import socket

# initial value
# filename = "filename"

window = tk.Tk()
window.title("Salvo control")

# assume we work only with square router
# default router size
router_size = 128
# initialize the mutable array and fill it with zeros
# max size of our router is 256x256
router_state = bytearray(256)
# router access path, could be "COMx" port in case of Snell SW-P-08
router_ip = "192.168.4.20"
    
print(f"[{time.ctime()}] Default router size: {router_size}")
# this needed for router state textbox
router_state_columns = 8


def router1_write():
    global router_size # do we really need to declare global variable? TO-DO: check this out
    if messagebox.askyesno(title = "Confirmation", message = "Confirm router overwrite?"):
        # Videohub
        sockvh = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (e_ip.get(), 9990)
        print(f"[{time.ctime()}] Trying to connect to: {server_address} ...")
        try:
            sockvh.connect(server_address)
        except TimeoutError:
            print(f"[{time.ctime()}] Timeout error")
            tk.messagebox.showerror("Error", "Timeout error!")
            return # exit the function
        except:
            print(f"[{time.ctime()}] Connection error")
            return # exit the function
        time.sleep(0.4)
        # Okay, we've connected. Now let's read the first message router sends to us (lot of text)
        data = sockvh.recv(8888)
        time.sleep(0.4)
# TO-DO: arrange sleep timings, perhaps we don't need so much delay
        sockvh.send(("VIDEO OUTPUT ROUTING:\n").encode("cp1250"))
        for i in range(router_size):
            sockvh.send((str(i) + " " + str(router_state[i]) + "\n").encode("cp1250"))
        sockvh.send("\n".encode("cp1250"))
        print(f"[{time.ctime()}] Router updated")
    else:
        print(f"[{time.ctime()}] Router overwrite canceled")


# TO-DO
def router1_read():
    global router_size
    # Videohub
    sockvh = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (e_ip.get(), 9990)
    print(f"[{time.ctime()}] Trying to connect to: {server_address} ...")
    try:
        sockvh.connect(server_address)
    except TimeoutError:
        print(f"[{time.ctime()}] Timeout error")
        tk.messagebox.showerror("Error", "Timeout error!")
        return # exit the function
    except:
        print(f"[{time.ctime()}] Connection error")
        return
#   print(f"[{time.ctime()}] {server_address}")
    time.sleep(0.4)
    # okay, we've connected. now let's read the first message router sends to us (lot of text)
    # TO-DO: detect whether router retuns "Video outputs string" and process the exception on case of error
    data = sockvh.recv(8888)
    time.sleep(0.4)
    # read and decode from router
    data = data.decode("cp1250")
    data = data.split('\n')
    print(data)
    print("\n")
    # let's search for "Video outputs:" string
    # the next string has been copypasted from stackoverflow, need to figure out what it actually does
    s = next(i for i in data if i.startswith("Video outputs:"))
    print(s)
    s = s.split(":")
    router_size = int(s[1])
    print(f"[{time.ctime()}] Router size read: ")
    print(router_size)
    
# send command to read output routing
    sockvh.send(b"video output routing:\n\n")
    time.sleep(0.1)
# read and decode from router
    outrouting = sockvh.recv(4096)
    outrouting = outrouting.decode("cp1250")
    outrouting = outrouting.split('\n')
##    print("\n----- OUTROUTING O<I: -----")
##    print(outrouting)
# delete first three rows
    for i in range(3):
        a = outrouting.pop(0)
    print("\n----- OUTROUTING O<I CLEAN (3 first rows removed, zero-based): -----")
    print(outrouting)
    
    for i in range(router_size):
        splitted = outrouting[i].split(' ')
        router_state[int(splitted[0])] = int(splitted[1])

    router_state_update()


# this needed for file open/save dialogs
filetypes = (("BIN files", "*.bin"), ("All files", "*.*"))

# .bin file format:
# first 2 bytes: router size (integer, big endian)
# then 256 bytes of router sources per destination
# then the ip address until EOF
# TO-DO: check whether COMx is okay too
def fil_open():
    global router_size
    global router_state
    global router_ip
    filename = fd.askopenfilename(filetypes = filetypes)
    if filename:
        # received file name, let's open the file
        # TO-DO: wrap this into try..except statement
        newfile = open(filename, "rb")
        router_size = int.from_bytes(newfile.read(2), "big")
        router_state = bytearray(newfile.read(256)) #otherwise it will convert bytearray to bytes, need to strictly specify
        router_ip = newfile.read().decode()
        newfile.close
        print(f"[{time.ctime()}] {filename} loaded successfully")
        print(f"[{time.ctime()}] Router size read from file: {router_size}; Access path: {router_ip}")
        # print(router_state) # debug
        # updating the textbox
        router_state_update()
    else:
        print(f"[{time.ctime()}] File opening dialog canceled")


def fil_saveas():
    # global router_size
    # there is no need to declare a global for a variable which you only read
    def_fn = time.strftime("%y%m%d-%H%M", time.localtime())     # default file name, we create it based on current date and time
    filename = fd.asksaveasfilename(
        initialfile = def_fn, defaultextension = ".bin", filetypes = filetypes
    )
    if filename:
        # TO-DO: wrap this into try..except statement
        newfile = open(filename, "wb")
        newfile.write(router_size.to_bytes(2, "big"))
        newfile.write(router_state)
        newfile.write(str.encode(e_ip.get()))
        newfile.close
        print(f"[{time.ctime()}] {filename} saved successfully, router size {router_size}")
    else:
        print(f"[{time.ctime()}] Saving to file canceled")


# update the GUI text boxes
def router_state_update():
    # global router_size
    # there is no need to declare a global for a variable which you only read
    # we assume router_size is dividable by router_state_columns without remainder
    router_state_rows = router_size // router_state_columns
    e_ip_text.set(router_ip)                    # update IP field
    t_router_state.config(state = tk.NORMAL)    # enable textbox

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
f_file = tk.LabelFrame(window, text = "File")
f_file.pack(expand = 0, fill = "both")

b_open = tk.Button(f_file, text = "Open...", command = fil_open)
b_open.pack(side = "left", padx = 3, pady = 3)
b_saveas = tk.Button(f_file, text = "Save As...", command = fil_saveas)
b_saveas.pack(side = "left", padx = 3, pady = 3)
# l_file = tk.Label(f_file, text="no file loaded")
# l_file.pack(side="left", padx=3, pady=3)

f_router1 = tk.LabelFrame(window, text = "Router Control")
f_router1.pack(expand = 0, fill = "both")

b_read1 = tk.Button(f_router1, text = "Read", command = router1_read)
b_read1.pack(side = "left", expand = 0, fill = "both", padx = 3, pady = 3)
b_write1 = tk.Button(f_router1, text="Write", command = router1_write)
b_write1.pack(side = "left", expand = 0, fill = "both", padx = 3, pady = 3)
e_ip_text = tk.StringVar()
e_ip = tk.Entry(f_router1, textvariable = e_ip_text)
e_ip.pack(side = "left", expand = 0, fill = "both", padx = 3, pady = 3)

f_router_state = tk.LabelFrame(window, text = "Router State")
f_router_state.pack(expand = 0, fill = "both")

# height and width are in chars!!!
# one xpt 'dst:src ' = 8 chars, the router state has router_state_columns xpt's width
t_router_state = scrolledtext.ScrolledText(
    f_router_state, height=16, width=router_state_columns * 8
#    f_router_state, height=router_state_rows, width=router_state_columns * 8
    )
t_router_state.pack(side="left", expand=0, fill="both", padx=3, pady=3)
# ------ TKINTER PACK ENDS HERE ------

# one-time execution
router_state_update()

# main loop
window.mainloop()
