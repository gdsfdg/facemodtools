# Dumping the face
You will need: 
- [GUI collector](https://github.com/Petrascyll/gui_collect/tree/main) and python to run it
- [XXMI](github.com/SpectrumQT/XXMI-Launcher) with [hunting enabled](https://i.imgur.com/kvjchOI.png) and `dump usage = 1`

Open your GIMI folder. The default location is `C:\Users\Admin\AppData\Roaming\XXMI Launcher\GIMI`. You can easily find it by clicking **Open Mods Folder** in the launcher. 

Open `d3dx.ini`. Hit **ctrl + F** and search for `dump_usage =`. If it says `dump usage = 0`, change it to `dump usage = 1`. Save and close. (You only have to do this once.)

Open the game with XXMI and navigate to the Character Archive. Open the "Details" and "Profile" page for your character. You can press **F6 to disable mods** if you already have some.  
Now press **0 on your numpad**. Green text should appear at the top and bottom of your screen.  
> (If you have no numpad, you can use On-Screen Keyboard. [Windows has a built-in one.](https://support.microsoft.com/en-us/windows/use-the-on-screen-keyboard-osk-to-type-ecbb5e08-5b4e-d8c8-f794-81dbf896267a#id0ebd=windows_11))

![Genshin character profile with green hunting text](https://i.imgur.com/eC8C2CG.jpeg)
Press **/ and * on your numpad** to cycle through vertex buffers. There should be roughly 10~20. If there are a lot more, press + on your numpad to reset.  
Keep cycling through them until the part you want to dump turns invisible.  
For this guide, that would be the eyebrows, face (eye area) and/or face (mouth area).

Once the part you want is invisible, **press - on your numpad to copy the hash**.

Open the GUI collector.  
> If double clicking `launch.bat` doesn't work, try right clicking in the folder, selecting `Open in Terminal` and running `python collect.py`

Click the Genshin tab on the left (the little chibi Sucrose).  
Paste the hash you just got in one of the `IB hash` fields and label it.  
![an image showing GUI collect and a selected part in genshin](https://i.imgur.com/tGDRbT2.png)

Repeat this for any other parts you want to edit (like I said above, a full face dump would include eyebrows, eye area and mouth area, three parts).

*Don't include the rest of the character (unless you know what you are doing).  
Face modding and normal modding is different, so automated tools can get confused if both are mixed in one dump.*

After you are done, **press + to reset** and **F8 to dump**. This might take a while, just wait until Genshin is responsive again.

Then, in the GUI collector, press the folder icon and navigate to your GIMI folder. 

There should be a folder called `FrameAnalysis-2025-04-13-130425` (The timestamp is when you dumped it). Select this folder and then hit the big red **Extract** button. 

**Don't check "Delete frame analysis after extraction"**, you will need it to get the original buffer.

Click on the **ps-t0 face texture** on the right (the one that looks "normal") and click **"Diffuse"**. This will include it in the dump. Then, click **Done**.

GUI collector will open the folder with your finished dump for you!

## Get orig.buf
Open Genshin Face Modding Tools.  
Select your dump folder (the one that GUI collector just opened) and a mod folder (the output directory).  
Then, click **Get orig.buf** and paste the path to your `FrameAnalysis-2025-04-13-130425` folder from before.  
It should put one orig.buf for each part in your selected mod folder.

Now, you can dump the rest of the character if you wish or delete the FrameAnalysis folder. These folders can get pretty large, so you should delete them after you got everything you need.