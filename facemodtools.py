import customtkinter
from tkinter import END
from tkinter import filedialog
from PIL import Image

import os, fnmatch
import json
import shutil
import fixface

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.geometry("600x300")
app.title("Genshin Face Modding Tools")
awesomeicon = app.iconbitmap('_internal/funny/magolor.ico')

# main window

# log
logbox = customtkinter.CTkTextbox(master=app, width=240, height=180, wrap="word")
logbox.place(relx=0.55, rely=0.61, anchor=customtkinter.W)
logbox.configure(state="disabled")

# file selection dialog
def filebutton0():
    dumpfolder = filedialog.askdirectory()
    entry0.delete(0, 999)
    entry0.insert(0, dumpfolder)

filebutton0 = customtkinter.CTkButton(master=app, text="Dump Folder", command=filebutton0)
filebutton0.place(relx=0.05, rely=0.1, anchor=customtkinter.W)
entry0 = customtkinter.CTkEntry(app, width=390)
entry0.place(relx=0.3, rely=0.1, anchor=customtkinter.W)

def filebutton1():
    modfolder = filedialog.askdirectory()
    entry1.delete(0, 999)
    entry1.insert(0, modfolder)

filebutton1 = customtkinter.CTkButton(master=app, text="Mod Folder", command=filebutton1)
filebutton1.place(relx=0.05, rely=0.2, anchor=customtkinter.W)
entry1 = customtkinter.CTkEntry(app, width=390)
entry1.place(relx=0.3, rely=0.2, anchor=customtkinter.W)

def printlog(message):
    logbox.configure(state="normal")
    logbox.insert(END, message + "\n")
    logbox.configure(state="disabled")
    
# buttons
def origbuf_func():
    dumpfolder = entry0.get()
    modfolder = entry1.get()
    if dumpfolder == "":
        printlog("Please select a Dump Folder!")
        return
    if modfolder == "":
        printlog("Please select a Mod Folder!")
        return

    # read parts from hash.json
    hashfile = dumpfolder + "\hash.json"
    with open(hashfile, 'r') as file:
        data = json.load(file)
        file.close()

    parts = []
    for part in data:
        parts.append([part['component_name'], part['draw_vb']])
    print(parts)

    # new window
    dialog = customtkinter.CTkInputDialog(text="FrameAnalysis folder:", title="Test")
    frameanalysis = dialog.get_input()
    # printlog("Selected folder: " + frameanalysis + "...")

    for part in parts:
        # printlog("Getting orig.buf for " + part[0] + "...")
        result = ""
        pattern = "*" + part[1] + "*.buf"
        # find original buffers
        # takes the first buffer it finds, should be first draw since it's sorted alphabetically?
        for root, dirs, files in os.walk(frameanalysis):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    # result.append(os.path.join(root, name))
                    result = os.path.join(root, name)
                    break

        if len(parts) > 1:
            pathfolder = modfolder + "/" + part[0]
            if not os.path.exists(pathfolder):
                os.makedirs(pathfolder)
            finalname = part[0] + "/orig.buf"
        else:
            finalname = "orig.buf"

        if result:
            print(result)
            printable_result = result
            printable_result = printable_result.replace(frameanalysis + "\\", "")

            printlog("Draw: " + printable_result.split('-vb0=', 1)[0])
            # shutil.copyfile(result, modfolder + "/" + finalname)
            shutil.copy2(result, modfolder + "/" + finalname)
            printlog("Found " + finalname)
        else:
            printlog("Couldn't find " + finalname)

    # printlog("Done!")

origbuf = customtkinter.CTkButton(master=app, text="Get orig.buf", height=50, command=origbuf_func)
origbuf.place(relx=0.05, rely=0.4, anchor=customtkinter.W)

def cleandump_func():
    dumpfolder = entry0.get()
    if dumpfolder == "":
        printlog("Please select a Dump Folder!")
        return

    # check old backup
    backup_path = dumpfolder + "/uncleaned"
    if os.path.exists(backup_path):
        # shutil.rmtree(backup_path)
        printlog("It looks like the dump got cleaned already. Remove \"uncleaned\" folder to proceed anyways.")
        return

    # find vb0 files
    vb0s = []
    for root, dirs, files in os.walk(dumpfolder):
            for name in files:
                if fnmatch.fnmatch(name, "*vb0*.txt"):
                    vb0s.append(os.path.join(root, name))

    # copy original files as backup
    if not os.path.exists(backup_path):
        os.makedirs(backup_path)

    for vb0 in vb0s:
        shutil.copy2(vb0, backup_path)

        # process files
        with open(vb0, 'r') as file:
            lines = file.readlines()
            file.close()

        lines[0] = "stride: 40\n"

        # very stinky
        # started = False
        # for i, line in enumerate(lines):
        #     if "element[3]:" in lines[i]:
        #         started = True
        #     if lines[i] == "\n":
        #         break
        #     if started:
        #         lines[i] = "DELETETHIS\n"

        for i, line in enumerate(lines):
            if "element[" in lines[i]:
                if "SemanticName: COLOR" in lines[i+1] or "SemanticName: TEXCOORD" in lines[i+1]:
                    
                    # delete this element
                    print("deleting " + lines[i] + "because it contains " + lines[i+1])
                    counter = 0
                    while counter <= 7:
                        lines[i+counter] = "DELETETHIS\n"
                        counter+=1
                started = i
            if lines[i] == "\n":
                break
            # if started:
            #     lines[i] = "DELETETHIS\n"

        filtered_lines = [line for line in lines if 'COLOR' not in line and 'TEXCOORD' not in line and 'DELETETHIS' not in line]

        with open(vb0, 'w') as file:
            file.writelines(filtered_lines)
            file.close()

    printlog("Copied original files to \"uncleaned\" folder.") 
    printlog("Deleted COLOR and TEXCOORD attributes from every vb0 file in dump folder.")

cleandump = customtkinter.CTkButton(master=app, text="Clean dump", height=50, command=cleandump_func)
cleandump.place(relx=0.05, rely=0.6, anchor=customtkinter.W)

def ini_func():
    dumpfolder = entry0.get()
    modfolder = entry1.get()
    if dumpfolder == "":
        printlog("Please select a Dump Folder!")
        return
    if modfolder == "":
        printlog("Please select a Mod Folder!")
        return

    # read parts from hash.json
    hashfile = dumpfolder + "\hash.json"
    with open(hashfile, 'r') as file:
        data = json.load(file)
        file.close()

    # print(data)

    parts = []
    diffuse = ""
    vertcount = 0
    for part in data:
        # i have to get the vert count too hamtaroold
        # opening and searching once for every part heh
        for root, dirs, files in os.walk(dumpfolder):
            for name in files:
                if fnmatch.fnmatch(name, "*vb0=" + part['draw_vb'] + ".txt"):
                    with open(os.path.join(root, name), 'r') as file:
                        lines = file.readlines()
                        file.close()
                        vertcount = lines[2].replace("vertex count: ", "").replace("\n", "")

        parts.append([part['component_name'], part['draw_vb'], vertcount])

        if part['texture_hashes'][0] and diffuse == "":
            if 'Diffuse' in part['texture_hashes'][0][0]:
                # i think diffuse is always first but i have to test it hehe
                diffuse = part['texture_hashes'][0][0][2]
    
    # print(parts)
    # print(diffuse)

    # copy hlsl file to mod folder
    shutil.copy2("_internal/funny/Face.hlsl", modfolder)

    # read template files
    header = ""
    templateini = ""

    if diffuse:
        with open("_internal/funny/template_header.ini", 'r') as file:
            header = file.readlines()
            file.close()
        with open("_internal/funny/template_diffuse.ini", 'r') as file:
            templateini = file.readlines()
            file.close()
    else:
        with open("_internal/funny/template.ini", 'r') as file:
            templateini = file.readlines()
            file.close()

    # create subfolders for parts if necessary
    if len(parts) > 1:
        for part in parts:
            pathfolder = modfolder + "/" + part[0]
            if not os.path.exists(pathfolder):
                os.makedirs(pathfolder)

    ini = []
    if header:
        for line in header:
            ini.append(line.replace("DIFFUSEHASH", diffuse))

    for part in parts:
        pathtrans = ""
        if len(parts) > 1:
            pathtrans = part[0] + "/"
            ini.append("; " + part[0] + " ---------------------\n\n")
                
        # close your eyes
        for line in templateini:
            epic = line.replace("PART", part[0])
            epic = epic.replace("VBHASH", part[1])
            epic = epic.replace("VERTCOUNT", part[2])
            epic = epic.replace("PATH", pathtrans)
            ini.append(epic)

        ini.append("\n")

    ini.append("; This ini was automatically generated.")

    with open(modfolder + "/Face.ini", 'w') as file:
        file.writelines(ini)
        file.close()

    printlog("Generated mod folder files.")
    if len(parts) > 1:
        printlog("Please save your \"base.buf\" and \"key.buf\" into the generated subfolders.")

ini = customtkinter.CTkButton(master=app, text="Generate .ini and .hlsl", height=50, command=ini_func)
ini.place(relx=0.05, rely=0.8, anchor=customtkinter.W)

def blender_func():
    modfolder = entry1.get()
    if modfolder == "":
        printlog("Please select a Mod Folder!")
        return

    delete_patterns = ["*key*.ib", "*key*.fmt", "*base*.ib", "*base*.fmt"]
    deletion = 0
    rename = 0

    for root, dirs, files in os.walk(modfolder):
        for name in files:
            
            for pattern in delete_patterns:
                if fnmatch.fnmatch(name, pattern):
                    os.remove(os.path.join(root, name))
                    deletion += 1

            epic = ""
            if fnmatch.fnmatch(name, "*base*.vb0"):
                epic = "base"
            if fnmatch.fnmatch(name, "*key*.vb0"):
                epic = "key"

            if epic:
                newfile = os.path.join(root, epic + ".buf")
                newfile2 = os.path.join(root, "old_" + epic + ".buf")
                if os.path.isfile(newfile):
                    if os.path.isfile(newfile2):
                        os.remove(newfile2)
                    os.renames(newfile, os.path.join(root, "old_" + epic + ".buf"))
                os.renames(os.path.join(root, name), newfile)
                epic = ""
                rename += 1
    
    if rename > 0:
        printlog("Renamed " + str(rename) + " .vb0 file(s) to .buf.")
    if deletion > 0:
        printlog("Deleted " + str(deletion) + " .fmt and .ib files.")
    print(deletion + rename)
    if deletion + rename == 0:
        printlog("Found nothing to clean.")
blender = customtkinter.CTkButton(master=app, text="Clean blender export", height=50, command=blender_func)
blender.place(relx=0.3, rely=0.4, anchor=customtkinter.W)

def reorder_func():
    modfolder = entry1.get()
    if modfolder == "":
        printlog("Please select a Mod Folder!")
        return

    origfolders = []
    unfixedfolder = 0
    print(len(origfolders))
    for root, dirs, files in os.walk(modfolder):
        for name in files:
            # check for key and buf
            if fnmatch.fnmatch(name, "orig.buf"):
                if os.path.isfile(root + "/key.buf") and os.path.isfile(root + "/base.buf"):
                    # check if the folder is "UNFIXED"!!!
                    rootcopy = root
                    if "unfixed" in rootcopy.replace(modfolder, ""):
                        unfixedfolder += 1
                    else:
                        origfolders.append(root)

    print(origfolders)

    if len(origfolders) == 0:
        if unfixedfolder:
            # reorder.text = "Reorder points (REPLACE)"
            if unfixedfolder > 1:
                printlog("Found " + str(unfixedfolder) + " unfixed folders. Move orig.buf out of them to run this function again.")
            else:
                printlog("Found an unfixed folder. Move orig.buf out of it to run this function again.")
        else:
            printlog("Found no base.buf/key.buf/orig.buf pair. Aborting.")
        return

    for folder in origfolders:
        olddir = os.getcwd()
        os.chdir(folder)

        if os.path.exists(folder + "/unfixed"):
            # heh i checked for this at the wrong location
            os.remove("unfixed/base.buf")
            os.remove("unfixed/key.buf")
            os.rmdir("unfixed")
            # printlog("Found unfixed folder, skipping")
            # os.chdir(olddir)
        os.makedirs("unfixed")
        shutil.copy2("base.buf", "unfixed/base.buf")
        shutil.copy2("key.buf", "unfixed/key.buf")
        shutil.copy2("orig.buf", "unfixed/orig.buf")
    
        os.makedirs("fixed")
        fixface.fixthis("orig.buf", "base.buf", "base.buf", folder)
        fixface.fixthis("orig.buf", "base.buf", "key.buf", folder)

        # hehe
        os.remove("orig.buf")
        os.remove("base.buf")
        os.remove("key.buf")

        shutil.copy2("fixed/base.buf", "base.buf")
        shutil.copy2("fixed/key.buf", "key.buf")

        shutil.rmtree("fixed")

        foldername = folder.replace(modfolder, "")
        if foldername == "":
            foldername = "mod folder"

        printlog("Fixed files in " + foldername)
        os.chdir(olddir)

reorder = customtkinter.CTkButton(master=app, text="Reorder points", height=50, command=reorder_func)
reorder.place(relx=0.3, rely=0.6, anchor=customtkinter.W)

image = customtkinter.CTkImage(light_image=Image.open("_internal/funny/mags.png"), size=(58, 48))
image_label = customtkinter.CTkLabel(app, image=image, text="")
# image_label.place(relx=0.3, rely=0.8, anchor=customtkinter.W)
image_label.place(relx=0.44, rely=0.8, anchor=customtkinter.W)

image2 = customtkinter.CTkImage(light_image=Image.open("_internal/funny/marx.png"), size=(58, 60))
image_label2 = customtkinter.CTkLabel(app, image=image2, text="")
image_label2.place(relx=0.33, rely=0.8, anchor=customtkinter.W)

app.mainloop()