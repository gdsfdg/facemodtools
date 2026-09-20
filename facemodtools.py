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

CURRENT_VERSION = "2.0"

app = customtkinter.CTk()
app.geometry("600x300")
app.title("Genshin Face Modding Tools")
awesomeicon = app.iconbitmap('_internal/funny/magolor.ico')

settings = "_internal/funny/settings.json"

def load_json():
    if os.path.exists(settings):
        with open(settings, "r") as file:
            return json.load(file)
    else: 
        data = {}
        with open(settings, "w") as f:
            f.write(json.dumps(data))
            return data
    
def update_json(**updates):
    data = load_json()
    data.update(updates)
    with open(settings, "w") as file:
        json.dump(data, file, indent=4)

def get_folders():
    update_json(dumpfolder=entry0.get(), modfolder=entry1.get())

    dumpfolder = entry0.get()
    if dumpfolder == "":
        printlog("Please select a Dump Folder!")
        return
    modfolder = entry1.get()
    if modfolder == "":
        printlog("Please select a Mod Folder!")
        return
    return [dumpfolder, modfolder]
    
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

data = load_json()
if data:
    entry0.insert(0, data.get("dumpfolder", ""))
    entry1.insert(0, data.get("modfolder", ""))

def printlog(message):
    logbox.configure(state="normal")
    logbox.insert(END, message + "\n")
    logbox.configure(state="disabled")

# printlog("https://gamebanana.com/tuts/18672")

# buttons
def origbuf_func():
    data = get_folders()
    if data: dumpfolder, modfolder = data 
    else: return

    # read parts from hash.json
    hashfile = dumpfolder + "\hash.json"
    if not os.path.exists(hashfile):
        printlog("Couldn't find hash.json, exiting.")
        return
    
    with open(hashfile, 'r') as file:
        data = json.load(file)

    parts = []
    success = False
    for part in data:
        parts.append([part['component_name'], part['draw_vb']])
        # make subfolders to export into later
        if len(data) > 1:
            output = modfolder + "/" + part['component_name']
            if not os.path.exists(output):
                os.makedirs(output)
                success = True

    if success: printlog("Please save your \"base\" and \"key\" into the generated subfolders.")


    pathfolder = os.path.join(dumpfolder, "originalbuffers")
    if os.path.exists(pathfolder):
        printlog("originalbuffers folder found in dump, skipping frameanalysis step.")
        return

    # get orig.buf - pretty much unchanged
    # try to get 3dm folder from settings
    framepath = ""
    text = "FrameAnalysis folder:"
    setting = load_json()
    if setting: 
        migotopath = setting.get("migotofolder", "")
        if migotopath:
            folders = [
                name
                for name in os.listdir(migotopath)
                if name.startswith("FrameAnalysis-")
                and os.path.isdir(os.path.join(migotopath, name))
            ]
            if folders: latest = max(folders)
            if latest: 
                framepath = os.path.join(migotopath, latest)
                text = "Auto filled latest FrameAnalysis folder!\n" + text
    
    # new window
    dialog = customtkinter.CTkInputDialog(text=text, title="Getting original buffer")
    dialog.after(15, lambda: dialog._entry.insert(0, framepath)) # IDK WHY I DID THIS BROOOOOOO
    frameanalysis = dialog.get_input()
    if not frameanalysis: return

    print("3dm folder:", os.path.dirname(frameanalysis))
    update_json(migotofolder=os.path.dirname(frameanalysis))

    # ok unchanged now for real heh
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
            pathfolder = os.path.join(dumpfolder, "originalbuffers", part[0])
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
            shutil.copy2(result, dumpfolder + "/originalbuffers/" + finalname)
            printlog("Found " + finalname)
        else:
            printlog("Couldn't find " + finalname)

    # printlog("Done!")

origbuf = customtkinter.CTkButton(master=app, text="Setup", height=50, command=origbuf_func)
origbuf.place(relx=0.05, rely=0.4, anchor=customtkinter.W)

modtexturestoggle = customtkinter.CTkCheckBox(app, text="Mod textures")
modtexturestoggle.place(relx=0.32, rely=0.38, anchor=customtkinter.W)

reordertoggle = customtkinter.CTkCheckBox(app, text="Reorder", onvalue=True, offvalue=False)
reordertoggle.place(relx=0.32, rely=0.5, anchor=customtkinter.W)
reordertoggle.select()

initoggle = customtkinter.CTkCheckBox(app, text="Write ini", onvalue=True, offvalue=False)
initoggle.place(relx=0.32, rely=0.62, anchor=customtkinter.W)
initoggle.select()

def slice_buf(data, oldstride):
    out = bytearray()
    newstride = 12
    for i in range(0, len(data), oldstride):
        out.extend(data[i:i + newstride])
    return bytes(out)

# Yare yare.......
def ini_func():
    data = get_folders()
    if data: dumpfolder, modfolder = data 
    else: return

    modname = os.path.basename(dumpfolder)

    # read parts from hash.json
    hashfile = dumpfolder + "\hash.json"
    with open(hashfile, 'r') as file:
        data = json.load(file)

    parts = []
    diffuse = ""
    vertcount = 0
    objstride = str(40)
    strd = str(40)

    for part in data:
        vertcount = 0
        strd = str(40)
        # i have to get the vert count too hamtaroold
        # opening and searching once for every part heh
        for root, dirs, files in os.walk(dumpfolder):
            if "uncleaned" in dirs: dirs.remove("uncleaned")
            if "originalbuffers" in dirs: dirs.remove("originalbuffers")
            else:
                printlog("No originalbuffers folder found in dump, mod might be broken!")
            for name in files:
                if fnmatch.fnmatch(name, "*vb0=" + part['draw_vb'] + ".txt"):
                    with open(os.path.join(root, name), 'r') as file:
                        lines = file.readlines()
                        objstride = lines[0].replace("stride: ", "").replace("\n", "")
                        vertcount = lines[2].replace("vertex count: ", "").replace("\n", "")
                        if len(data) > 1: origlocation = os.path.join(dumpfolder, "originalbuffers", part['component_name'], "orig.buf")
                        else: origlocation = os.path.join(dumpfolder, "originalbuffers", "orig.buf")
                        if os.path.isfile(origlocation):
                            strd = str (os.path.getsize(origlocation) // int(vertcount))
                            print(part['component_name'], strd)
                        else: printlog("Couldn't find necessary files in dump, mod might be broken!")

        parts.append([part['component_name'], part['draw_vb'], vertcount, strd, objstride])

        if part['texture_hashes'][0] and diffuse == "":
            # turns out diffuse is not always first
            for texture in part['texture_hashes'][0]:
                if texture[0] == 'Diffuse':
                    diffuse = texture[2]
                    break

    if initoggle.get():
        # copy hlsl file to mod folder
        shutil.copy2("_internal/funny/s.hlsl", modfolder)

        # read template files
        header = ""
        templateini = ""

        if diffuse:
            with open("_internal/funny/template_header.ini", 'r') as file:
                header = file.readlines()
            with open("_internal/funny/template_diffuse.ini", 'r') as file:
                templateini = file.readlines()
        else:
            with open("_internal/funny/template.ini", 'r') as file:
                templateini = file.readlines()

        # create subfolders for parts if necessary
        if len(parts) > 1:
            for part in parts:
                pathfolder = os.path.join(modfolder, part[0])
                if not os.path.exists(pathfolder):
                    os.makedirs(pathfolder)

        ini = []
        if header:
            for line in header:
                ini.append(line.replace("DIFFUSEHASH", diffuse))
            if modtexturestoggle.get():
                # get textures
                textures = []
                for part in data:
                    if part['texture_hashes'][0]:
                        for texture in part['texture_hashes'][0]:
                            name = texture[0]
                            if name not in textures: textures.append(name)
                if len(textures)>0:
                    ini.append("; Textures\n")
                    # get and copy .dds files
                    for texture in textures:
                        for root, dirs, files in os.walk(dumpfolder):
                            for name in files:
                                if fnmatch.fnmatch(name, "*"+texture+".dds"):
                                    shutil.copy2(os.path.join(dumpfolder, name), os.path.join(modfolder, texture+".dds"))
                        ini.append("Resource\GIMI\\"+texture+" = ref Resource"+texture+"\n")
                    ini.append("run = CommandList\GIMI\SetTextures\n\n")
                    for texture in textures:
                        ini.append("[Resource" + texture + "]\n")
                        ini.append("filename = " + texture + ".dds\n\n")
                printlog("Added textures.")

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
                epic = epic.replace("STRD", part[3])
                epic = epic.replace("PATH", pathtrans)
                ini.append(epic)
            ini.append("\n")

        ini.append("; Generated by facemodtools " + CURRENT_VERSION)
        ini.append("; https://github.com/gdsfdg/facemodtools")
        
        with open(modfolder + "/" + modname + ".ini", 'w') as file:
            file.writelines(ini)
        
        printlog("Wrote ini and hlsl.")

    blender_func(modfolder)

    chopcounter = 0
    fixed = False
    # Choppening
    for part in parts:
        # match folder name - modfolder/['component_name']/base.buf and modfolder/['component_name']/key.buf
        dirr = os.path.join(modfolder, part[0])
        for buf in ['base', 'key']:
            path = os.path.join(dirr, buf + ".EXPORT")
            if not os.path.isfile(path): continue
            # Check if stride is applicable
            oldstride = int(part[4])
            if os.path.getsize(path) % oldstride != 0:
                if os.path.getsize(path) // int(part[2]) == 12: print("Already 12 stride", part[0])
                else: print("Amogus", os.path.getsize(path) / oldstride)
                continue
            # Chop if yes
            with open(path, 'rb') as file: buffy = file.read()
            chopped = slice_buf(buffy, oldstride)
            with open(path, 'wb') as file: file.write(chopped)
            os.rename(path, os.path.join(dirr, buf + ".buf"))
            print("Chopped", part[0], buf, "Old stride", oldstride)
            print(str(len(buffy)) + " -> " + str(len(chopped)))
            fixed=True
        if fixed: printlog("Fixed " + part[0])
        fixed=False
    # if chopcounter>0: printlog("Fixed " + str(chopcounter) + " file(s).")

    # Reorder step... heh
    reordercounter = 0
    if not reordertoggle.get(): return

    for part in parts:
        # Why did i write this out like that
        dumpdir = os.path.join(dumpfolder, "originalbuffers", part[0])
        orig = os.path.join(dumpdir, "orig.buf")
        if not os.path.isfile(orig): continue

        moddir = os.path.join(modfolder, part[0])
        previous_base = os.path.join(dumpdir, "base.buf")
        if not os.path.isfile(previous_base): 
            base = (os.path.join(moddir, "base.buf"))
            if not os.path.isfile(base): continue
            else: shutil.copy2(base, previous_base)
            if not os.path.isfile(previous_base): continue

        key = os.path.join(moddir, "key.buf")
        if not os.path.isfile(key): continue

        # Ok now we have all our files yipppieeeeee
        if reorder(orig, previous_base, moddir, part[3]):
            printlog("Reordered " + part[0] + ".")
            reordercounter+=1
    
    if reordercounter==0: printlog("Found nothing to reorder or failed.")


def get_pos(filepath, stride):
    positions = []
    with open(filepath, "rb") as f:
        while True:
            position = f.read(12)
            if not position or len(position) != 12: break
            positions.append(position)

            # only need positions
            skip = int(stride) - 12
            if skip>0: f.seek(skip, 1)
    return positions


def reorder(origbuf, basebuf, moddir, origstrd):
    orig = get_pos(origbuf, origstrd)
    base = get_pos(basebuf, 12)
    key = get_pos(os.path.join(moddir, 'key.buf'), 12)

    if len(base) != len(key):
        printlog("base and key have different vertex counts.")
        return False

    if len(orig) > len(base):
        printlog("base is missing vertices.")
        return False

    # map position and index
    base_lookup = {}
    for i, position in enumerate(base): base_lookup[position] = i

    # reorder
    ordering = []
    for i, position in enumerate(orig):
        if position not in base_lookup: 
            print("position not found in base.buf at i", i)
            ordering = None
            break
        ordering.append(base_lookup[position])

    if not ordering:
        offset = offset_helper(orig, base)
        if offset:
            print("offset:", offset)
            ordering = fuzzy_order(orig, base, offset)
            if ordering:
                printlog("Using offset for reorder.")

    if not ordering:
        ordering = fuzzy_order(orig, base)
        if ordering:
            printlog("Using fuzzy reorder.")
        else:
            printlog("Couldn't match vertices.")
            return False

    with open(os.path.join(moddir, 'base.buf'), "wb") as f:
        for i in ordering: f.write(base[i])
    with open(os.path.join(moddir, 'key.buf'), "wb") as f:
        for index in ordering: f.write(key[index])

    return True

import struct

def distance_sq(a, b):
    ax, ay, az = a
    bx, by, bz = b

    dx = ax - bx
    dy = ay - by
    dz = az - bz

    return dx * dx + dy * dy + dz * dz

# try to find a consistent offset.
def offset_helper(orig, base):
    offset_tolerance = 0.000002

    orig_xyz = [struct.unpack("<3f", p) for p in orig]
    base_xyz = [struct.unpack("<3f", p) for p in base]

    offsets = []
    for orig_pos in orig_xyz:
        best_dist = float("inf")
        best_base = None

        for base_pos in base_xyz:
            dist = distance_sq(orig_pos, base_pos)
            if dist < best_dist:
                best_dist = dist
                best_base = base_pos

        if best_base is not None:
            offsets.append((
                best_base[0] - orig_pos[0],
                best_base[1] - orig_pos[1],
                best_base[2] - orig_pos[2]
            ))

    if not offsets:
        return None

    offsets_x = sorted(o[0] for o in offsets)
    offsets_y = sorted(o[1] for o in offsets)
    offsets_z = sorted(o[2] for o in offsets)

    middle = len(offsets) // 2

    if len(offsets) % 2:
        offset = (offsets_x[middle], offsets_y[middle], offsets_z[middle])
    else:
        offset = ((offsets_x[middle - 1] + offsets_x[middle]) / 2,
                  (offsets_y[middle - 1] + offsets_y[middle]) / 2,
                  (offsets_z[middle - 1] + offsets_z[middle]) / 2)

    # check if consistent
    good = 0
    tolerance_sq = offset_tolerance ** 2

    for orig_pos in orig_xyz:
        adjusted = (orig_pos[0] + offset[0], orig_pos[1] + offset[1], orig_pos[2] + offset[2])
        best_dist = float("inf")
        for base_pos in base_xyz:
            dist = distance_sq(adjusted, base_pos)
            if dist < best_dist:
                best_dist = dist

        if best_dist <= tolerance_sq:
            good += 1

    if good < len(orig) * 0.99:
        return None

    return offset

def fuzzy_order(orig, base, offset):
    if offset: fuzzy_tolerance = 0.000002
    else: fuzzy_tolerance = 0.00005
    orig_xyz = [struct.unpack("<3f", p) for p in orig]
    base_xyz = [struct.unpack("<3f", p) for p in base]

    used = set()
    ordering = []

    tolerance_sq = fuzzy_tolerance ** 2

    for i, orig_pos in enumerate(orig_xyz):

        if offset:  target = (orig_pos[0] + offset[0], orig_pos[1] + offset[1], orig_pos[2] + offset[2])
        else:       target = orig_pos

        best_index = None
        best_dist = float("inf")

        for j, base_pos in enumerate(base_xyz):

            if j in used:
                continue

            dist = distance_sq(target, base_pos)

            if dist < best_dist:
                best_dist = dist
                best_index = j

        if best_index is None or best_dist > tolerance_sq:
            print("Could not fuzzy-match orig vertex", i, "distance:",
                  best_dist if best_dist != float("inf") else "inf")
            return None

        used.add(best_index)
        ordering.append(best_index)

    return ordering

createmod = customtkinter.CTkButton(master=app, text="Create Mod", height=50, command=ini_func)
createmod.place(relx=0.05, rely=0.6, anchor=customtkinter.W)

# ini = customtkinter.CTkButton(master=app, text="Generate .ini and .hlsl", height=50, command=ini_func)
# ini.place(relx=0.05, rely=0.8, anchor=customtkinter.W)

def blender_func(modfolder):
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
                newfile = os.path.join(root, epic + ".EXPORT")
                os.renames(os.path.join(root, name), newfile)
                epic = ""
                rename += 1
    
    if rename > 0:
        printlog("Renamed " + str(rename) + " .vb0 file(s) to .buf.")
    if deletion > 0:
        printlog("Deleted " + str(deletion) + " .fmt and .ib files.")
    print(deletion + rename)
    # if deletion + rename == 0:
        # printlog("Found nothing to clean.")
# blender = customtkinter.CTkButton(master=app, text="Clean blender export", height=50, command=blender_func)
# blender.place(relx=0.3, rely=0.4, anchor=customtkinter.W)


def legacy_reorder():
    data = get_folders()
    if data: dumpfolder, modfolder = data 
    else: return

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

# reorder = customtkinter.CTkButton(master=app, text="Reorder legacy", height=50, command=reorder_func)
# reorder.place(relx=0.05, rely=0.8, anchor=customtkinter.W)

# noooo more dumpcleaning
def cleandump_func():
    data = get_folders()
    if data: dumpfolder = data 
    else: return

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

        SEMANTICS_TO_REMOVE = {
            "COLOR",
            "TEXCOORD",
            "BLENDWEIGHTS",
            "BLENDINDICES"
        }

        SEMANTICS = {
            "POSITION",
            "NORMAL",
            "TANGENT"
        }

        stride = 0

        for i, line in enumerate(lines):
            if "element[" in line:
                if any(f"SemanticName: {s}" in lines[i+1] for s in SEMANTICS_TO_REMOVE):
                    # delete this element
                    print("deleting " + line + "because it contains " + lines[i+1], end="")
                    counter = 0
                    while counter <= 7:
                        lines[i+counter] = "DELETETHIS\n"
                        counter+=1
                else:
                    # count them for stride... probably pointless to construct it so faithfully
                    semantic = lines[i+1].removeprefix("  SemanticName: ").strip()
                    if semantic in SEMANTICS:
                        print("found", semantic)
                        stride += 16 if semantic == "TANGENT" else 12
                started = i
            if lines[i] == "\n":
                break
            # if started:
            #     lines[i] = "DELETETHIS\n"
        
        lines[0] = "stride: " + str(stride) + "\n"

        # filtered_lines = [line for line in lines if 'COLOR' not in line and 'TEXCOORD' not in line and 'DELETETHIS' not in line]
        filtered_lines = [
            line for line in lines
            if not any(s in line for s in SEMANTICS_TO_REMOVE)
            and "DELETETHIS" not in line
        ]

        with open(vb0, 'w') as file:
            file.writelines(filtered_lines)

    printlog("Copied original files to \"uncleaned\" folder.") 
    printlog("Deleted COLOR and TEXCOORD attributes from every vb0 file in dump folder.")

import random

num = random.random()

image = customtkinter.CTkImage(light_image=Image.open("_internal/funny/mags.png"), size=(58, 48))
image_label = customtkinter.CTkLabel(app, image=image, text="")
# # image_label.place(relx=0.3, rely=0.8, anchor=customtkinter.W)
# image_label.place(relx=0.44, rely=0.8, anchor=customtkinter.W)

image2 = customtkinter.CTkImage(light_image=Image.open("_internal/funny/marx.png"), size=(58, 60))
image_label2 = customtkinter.CTkLabel(app, image=image2, text="")
# image_label2.place(relx=0.33, rely=0.8, anchor=customtkinter.W)

image3 = customtkinter.CTkImage(light_image=Image.open("_internal/funny/trole.png"), size=(90, 54))
image_label3 = customtkinter.CTkLabel(app, image=image3, text="")

if num > 0.8: image_label3.place(relx=0.375, rely=0.81, anchor=customtkinter.W) # troll
else: 
    image_label.place(relx=0.44, rely=0.8, anchor=customtkinter.W)
    if num < 0.25: image_label2.place(relx=0.33, rely=0.8, anchor=customtkinter.W) # marx


import webbrowser
def open_guide():
    webbrowser.open("https://gamebanana.com/tuts/18672")

# ini = customtkinter.CTkButton(master=app, text="Guide", height=50, width=65, command=open_guide)
# ini = customtkinter.CTkButton(master=app, text="Open Guide", command=open_guide)
# ini.place(relx=0.05, rely=0.765, anchor=customtkinter.W)

# more = customtkinter.CTkButton(master=app, text="More", height=50, width=65, command=open_guide)
# more.place(relx=0.176, rely=0.8, anchor=customtkinter.W)

logbox.configure(state="normal")
logbox.insert("end", "Open Gamebanana Guide", "link")
logbox.tag_config("link", underline=True)

# Open browser when clicked
logbox.tag_bind("link", "<Button-1>", lambda event: open_guide())
logbox.tag_bind("link", "<Enter>", lambda event: logbox.configure(cursor="hand2"))
logbox.tag_bind("link", "<Leave>", lambda event: logbox.configure(cursor=""))
logbox.configure(state="disabled")

# update lohl
import requests
from packaging import version

GITHUB_API = "https://api.github.com/repos/gdsfdg/facemodtools/releases/latest"

def check_for_update():
    try:
        response = requests.get(GITHUB_API, timeout=5)
        response.raise_for_status()

        data = response.json()
        latest = data["tag_name"].replace("v", "")

        if version.parse(latest) > version.parse(CURRENT_VERSION):
            return {"version": latest, "url": data["html_url"], "text": data["body"]}

    except Exception as e: print("Update check failed:", e)
    return False

update = check_for_update()
if update:
    setting = load_json()
    ignora = False
    if setting: 
        ignoredversion = setting.get("ignoreupdates", "")
        if ignoredversion == CURRENT_VERSION: ignora = True

    if not ignora:
        popup = customtkinter.CTkToplevel(app)
        popup.title(f"Version {update['version']} is available!")
        popup.geometry("400x200")
        popup.attributes("-topmost", True)
        popup.grab_set()

        label = customtkinter.CTkLabel(popup, text=f"Version {update['version']} is available!")
        textbox = customtkinter.CTkTextbox(popup, height=110, width=300)
        textbox.insert("0.0", update['text'])
        textbox.configure(state="disabled") 
        def open_release(): 
            webbrowser.open(update["url"])
            popup.destroy()
        def ignore():
            update_json(ignoreupdates=CURRENT_VERSION)
            popup.destroy()
        update_button = customtkinter.CTkButton(popup, text="Download Update", command=open_release)
        close_button = customtkinter.CTkButton(popup,text="Ignore", command=ignore)

        # label.place(relx=0.375, rely=0.2, anchor=customtkinter.W)
        textbox.place(x=50, y=70, anchor=customtkinter.W)
        update_button.place(x=50, rely=0.8, anchor=customtkinter.W)
        close_button.place(x=205, rely=0.8, anchor=customtkinter.W)


app.mainloop()