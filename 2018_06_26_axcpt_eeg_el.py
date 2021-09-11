######################################################################
#                          AXCPT-EEG
#                   BEHAVIORAL, EYELINK, EEG
#
# Cognitive Development Center - CU Boulder
# Contact Info:
#        Author: Hilary J. Traut
#        Email: Hilary.Traut@colorado.edu OR Hilary.Traut@gmail.com
#               (use subject line: CDC - AXCPT-EEG Script)
#
# Notes: Complete version. Images courtesy Lucenet & Blaye. Search
#        '!!!' for updating call to trial list .csv files; 'WARNING'
#        for important details; 'TODO' for unfinished components.
######################################################################

               #     #   #    ####  ######  ########
              # #     # #    #      #    #     #  
             #   #    ##    #       ######     #
            ######   #  #    #      #          #
           #      # #    #    ####  #          #

######################################################################
from psychopy import visual, core, event, gui, data, sound, monitors
import os, glob, time, sys, pyglet, math, csv, random, datetime
######################################################################


######################################################################
##                           DIALOG BOX                             ##
######################################################################
sessionInfo = {'Participant ID': '--   ', 'Date of Birth': '--/--/--   ',
                   'Age Group': ['7', '10', 'Adult'], 'Runner': '--  '}
    
infoDlg = gui.DlgFromDict(dictionary=sessionInfo, title='AXCPT-EEG-BEHAV', fixed=['Version'])

if infoDlg.OK:
    print sessionInfo
else: core.quit()

######################################################################
##                           FUNCTIONS                             ##
######################################################################
# A. Trial List Set Up Functions
######################################################################
'''
GOAL: Convert .csv file into array (i.e. list containing list of rows)
Input:
     file_name: name of file trial list is saved to (in 'filename')
Output:
     data: array copy of .csv file
'''

def trialArray(file_name):
    
    with open(file_name, 'rU') as f:
        reader = csv.reader(f)
        data = list(list(rec) for rec in csv.reader(f, delimiter = ","))
    return data

######################################################################
'''
GOAL: Check that the same condition repeats no more than 3 times in a row.
Input:
    order: randomized list of numbers corresponding to trial numbers for trial list.
Output:
    stim: acceptable row index for next trial stimuli
''' 
def weight(order):
    global Nmin1; global Nmin2; global Nmin3  #Set global variables for tracking prior trial conditions; used in func: weight
    
    ind = len(order)-1                        #ind: index for trial row
    ns = 1                                    #ns: number that can be subtracted for re-search
    searching = True                          #searching: while still looking for valid trial

    while searching:
        stim = order[ind]                     #Next row index for trial list defaults to last item
        
        #If the cond from the selected trial is the same as N-1, N-2, & N-3 but list length is not the same as ns....
        if trialList[stim][3] == Nmin1 and trialList[stim][3] == Nmin2 and trialList[stim][3] == Nmin3 and len(order)-1 > ns:
            
            ind = len(order) - ns             #New index to check is remaining length of trial list - 1
            ns = ns + 1                       #New allowance for subtraction is + 1
            
        else:
            #Reset priors
            Nmin3 = Nmin2
            Nmin2 = Nmin1
            Nmin1 =  trialList[stim][3]

            #Delete index to implement no replacement
            del order[ind]
            searching = False
    return stim

######################################################################
# B. Trial Presentation Functions
######################################################################
'''
GOAL: Display cue image.
Input:
    cueFile: cue image file name
Output: N/A
'''
def cue(cueFile):
    global cueImage                                                  #Set global variables for cue image object
    global cueStart; global probeStart; global probeEnd              #Set global variables for recording timestamps
    global cueEnd

    setTrig('sCUE')
    
    cueImage = visual.ImageStim(myWin, image = cueFile, pos=(0,0))   #Create cue image object
    cueImage.autoDraw = True
    myWin.flip()
    cueStart = core.getTime()                                        #cueStart: record time for start of cue presentation

    core.wait(0.5)                                                   #Cue display time: 500ms
    cueEnd = core.getTime()                                          #cueEnd: record time for end of cue presentation
    
    setTrig('eCUE')
    
    return

######################################################################
'''
GOAL: Display delay between probe and cue.
Input:  N/A
Output: N/A
'''
def delayScreen():
    global cueImage                                                  #Set global variables for cue image object
    global delayStart; global delayEnd                               #Set global variables for recording timestamps

    setTrig('sDELAY')
    
    cueImage.autoDraw = False; myWin.flip()
    delayStart = core.getTime()

    core.wait(1.2)                                                   #Delay display time: 1200ms
    delayEnd = core.getTime()
    
    setTrig('eDELAY')
    return

######################################################################
'''
GOAL: Display probe image; record response; call feedback functions.
Input:
    probeFile:  probe image file name
Output:
    keyPressed: key pressed or None if no key pressed
    acc:        response accuracy (0/1)
'''
def probe(probeFile,lst,indx):
    global probeImage                                                            #Set global variables for probe image object
    global probeStart; global probeEnd                                           #Set global variables for recording timestamps

    setTrig('sPROBE')
    
    probeImage = visual.ImageStim(myWin, image = probeFile, pos=(0,0))           #Create probe image object
    posResp.autoDraw = True; negResp.autoDraw = True; probeImage.autoDraw = True #Draw images
    myWin.flip()
    probeStart = core.getTime()                                                  #Set probeStart timestamp after window flip

    k = event.waitKeys(maxWait = 1.5, timeStamped = True)                        #Probe display time: 1500ms or until keypressed
    
    setTrig('ePROBE')
    
    if k == None:                                                                #If no response made, call snooze()
        acc = snoozeSlide()
        probeEnd = core.getTime()                                                #Set probeEnd timestamp
        keyPressed = None                                                        #Set keypress response to None
    else:                                                                        #If keypress made, call respFeedback() and pass keypress
        acc = respFeedback(k,lst,indx)
        probeEnd = k[0][1]                                                       #Set probeEnd timestamp
        keyPressed = k[0][0]                                                     #Set keypress response
        
    return keyPressed, acc

######################################################################
'''
GOAL: Display grey interval between trials.
Input:  N/A
Output: N/A
'''
def greyInterval():
    global probeImage

    setTrig('sITI')
    
    posResp.autoDraw = False; negResp.autoDraw = False                           #Undraw all images
    posFeed.autoDraw = False; negFeed.autoDraw = False; snooze.autoDraw = False  #Undraw all images con't
    
    myWin.flip()
    core.wait(1)                                                                 #Grey interval display time: 1000ms
    
    setTrig('eITI')
    return

######################################################################
'''
GOAL: Display snooze feedback for response outside time limit.
Input:  N/A
Output: N/A
'''
def snoozeSlide():
    acc = 0
    setTrig('sSNZ')
    
    probeImage.autoDraw = False      #remove probe from screen
    snooze.autoDraw = True           #present snooze image
    
    myWin.flip(); core.wait(1.5)     #Snooze display time: 1500ms

    setTrig('eSNZ')
    
    return acc

######################################################################
'''
GOAL: Display accuracy feedback if keypress recorded.
Input:
    k:    list output from call to waitKeys in probeSlide(); value is either 'None' or list of tuples [key, timestamp]
    lst:  trial array to pull from.
    indx: index at which to access trial array
Output:
    acc: response accuracy (0/1)
''' 
def respFeedback(k, lst, indx):
    probeImage.autoDraw = False               #Remove probe from screen
    setTrig('sFB')
    
    if k[0][0] == lst[indx][2]:               #Does keypress match correct answer?
        posFeed.autoDraw = True               #Draw positive feedback
        acc = 1                               #Set response accuracy
        
    elif k[0][0] != lst[indx][2]:             #Does keypress mismatch correct answer?
        negFeed.autoDraw = True               #Draw negative feedback
        acc = 0                               #Set response accuracy

    myWin.flip()
    core.wait(1.5)                            #Feedback display time: 1500ms
    setTrig('eFB')
    
    return acc

######################################################################
'''
Goal: Display break slide between blocks.
Input:  N/A
Output: N/A
'''
def blockInterval():
    setTrig('sIBI')
    
    instruct = visual.TextStim(win = myWin, text = 'Nice work! You have finished ' + str(block) + ' out of 10 blocks of the study.\n\nPress SPACE to continue.',
                                    pos = (0,0.5), height = 0.05, wrapWidth = 1.5, color = 'black'); instruct.draw()
    myWin.flip(); event.waitKeys(keyList = 'space')
    instruct.autoDraw = False
    
    setTrig('eIBI')
    return

######################################################################
'''
GOAL: Display instructions at start of experiment.
Input:  N/A
Output: N/A
'''
def instruct():
    title = visual.TextStim(win = myWin, text = 'Welcome to the Farm Yard!', pos = (0,0.7), height = 0.09,
                                wrapWidth = 1.5, color = 'black'); title.draw()

    instruct1 = visual.TextStim(win = myWin, text = 'You are going to see some pictures of animals. All the animals travel in pairs, one after the other.',
                                    pos = (0,0.5), height = 0.05, wrapWidth = 1.5, color = 'black'); instruct1.autoDraw = True
    

    duck = visual.ImageStim(win = myWin, image = 'duck.bmp', pos = (-0.3,0.2)); duck.draw()
    pig = visual.ImageStim(win = myWin, image = 'pig.bmp', pos = (0.3,0.2)); pig.draw()

    posResp.draw(); negResp.draw()
    
    instruct2 = visual.TextStim(win = myWin, text = 'The Duck and the Pig are good friends, so if you see a Duck followed by a Pig press the food button so they can eat together!\n\nIf you see any other animal pairs, press the X.',
                                    pos = (0,-0.2), height = 0.05, wrapWidth = 1.5, color = 'black'); instruct2.autoDraw = True
    
    myWin.flip(); event.waitKeys(keyList = 'space')

    title.autoDraw = False; instruct1.autoDraw = False; instruct2.autoDraw = False
    return

######################################################################
'''
GOAL: Present a series of three practice trials.
Input:  N/A
Output: N/A
'''
def prac():
    pracTrial = -1                                         #Init pracTrial index at -1
    pracList = trialArray('prac_trials.csv')               #Read in list of practice trials stored in .csv.

    #PART 1: Start practice section.
    pracText = visual.TextStim(win = myWin, text = 'Lets try some practice - remember: press the key for the food only if the duck is followed by the pig. Otherwise, press the key for the X.', pos = (0,0), height = 0.05, wrapWidth = 1.5, color = 'black')

    pracText.autoDraw = True; myWin.flip()                 #Display practice instructions.

    event.waitKeys(); pracText.autoDraw = False            #Undraw practice instructions after keypress.

    #PART 2: Admin practice trials.
    while pracTrial < len(pracList) - 1:                   #Con't administering practice until no more trials available.
        repeatText = visual.TextStim(win = myWin, text = 'Press SPACE to go on. Press any other key to try again.',
                                             pos = (0,0), height = 0.05, wrapWidth = 1.5, color = 'black'); repeatText.autoDraw = True; myWin.flip()
        pracKey = event.waitKeys()
        repeatText.autoDraw = False

        if pracKey[0] == 'space':                           #If experimenter presses space, con't to next prac trial.
            pracTrial = pracTrial + 1                       #Increment prac trial number, then present trial sequence.
            cue(pracList[pracTrial][0]); delayScreen()
            keyPressed_prac, acc_prac = probe(pracList[pracTrial][1], pracList, pracTrial); greyInterval()
            
        else:                                               #If experimenter presses any key other than space, repeat the previous trial.
                                                            #WARNING: If the experimenter presses anything other than space before the first prac trial, script will fault.
            cue(pracList[pracTrial][0]); delayScreen()
            keyPressed_prac, acc_prac = probe(pracList[pracTrial][1], pracList, pracTrial); greyInterval()

    pracText.setText('Great work! Ready to play for real?'); pracText.autoDraw = True; myWin.flip()   #Notify that prac as ended.
    event.waitKeys(); pracText.autoDraw = False                                                       #Wrap sequence
    return

######################################################################
'''
GOAL: Display complete trial sequence.
Input:
    trialnum:   objective trial number
    trialIndex: row in trial list accessed for current trial stimuli
Output:
    tr:         new trialnum
    cond:       trial condition
    cueFile:    cue image file name
    probeFile:  probe image file name
    keyPressed: key pressed or None if no key pressed
    acc:        response accuracy (0/1)
'''  
def trial(trialnum, trialIndex):
  
    cond = trialList[trialIndex][3]                                                   #Set 'cond' variable for current trial
    
    if cond != 'by':                                                                  #If not BY, select images from standard trial list file
        cueFile = trialList[trialIndex][0]
        probeFile = trialList[trialIndex][1]
        
    else:                                                                             #If BY, select images from BY list file                     
        cueFile = byList[orderBY[int(trialList[trialIndex][4])]][0]
        probeFile = byList[orderBY[int(trialList[trialIndex][4])]][1]     
    
    cue(cueFile); delayScreen()                                                       #Call func: cue() and func: delayScreen()
    keyPressed, acc = probe(probeFile, trialList, trialIndex); greyInterval()         #Call func: probe() and func: greyInterval()

    tr = trialnum + 1                                                                 #Increment trial number
    return tr, cond, cueFile, probeFile, keyPressed, acc

######################################################################
# C. Helper Functions (like elves, but real!)
######################################################################
'''
GOAL: Record data to write to dataFile.
Input:
    trialIndex: row in trial list accessed for current trial stimuli
    block:      objective block number
    trialnum:   objective trial number
    cond:       trial condition (ax, ay, bx, or by)
    cueFile:    cue image file name
    probeFile:  probe image file name
    keyPressed: key pressed or None if no key pressed
    acc:        response accuracy (0/1)
Output: N/A
'''
def recordTrial(trialIndex, block, trialnum, cond, cueFile, probeFile, keyPressed, acc):
    
    global cueStart; global cueEnd                         #Set global variables for recording timestamps
    global delayStart; global delayEnd                     #con't
    global probeStart; global probeEnd                     #con't
    
    
    dataFile = file(str(fileName), 'a')                    #Check dataFile name for participant - will keep adding data w/out overwrites

    rt = probeEnd - probeStart                             #rt: calculate reaciton time to trial response
    now = datetime.datetime.now()                          #now: current date and time
    now = now.strftime("%Y-%m-%d %H:%M")
    
    newline = str(sessionInfo['Participant ID']) + "," + str(sessionInfo['Date of Birth']) + ","  \
      + str(sessionInfo['Age Group']) + "," + str(sessionInfo['Runner']) + "," + str(now) + ","   \
      + str(block) + "," + str(trialnum) + ","   + cond + "," + cueFile + "," + probeFile + ","   \
      + str(keyPressed) + "," + str(acc) + "," + str(cueStart) + "," + str(cueEnd) + ","          \
      + str(delayStart) + "," + str(delayEnd) + "," + str(probeStart) + "," + str(probeEnd) + "," + str(rt) + "\n"
    
    dataFile.writelines(newline)                           #Write lines to file
    dataFile.close()                                       #Close dataFile

    return

######################################################################
'''
GOAL: Call calibration function for Eyelink.
Input:  N/A
Output: N/A
'''
def calibrateEL():
    tracker.calibrate(cnum=9)
    return

######################################################################
'''
GOAL: Set triggers for EGI and EyeLink
Input:  
    trig_name: name to be outputed in data for trigger event
Output: N/A
'''
def setTrig(trig_name):
    ns.send_event(trig_name, timestamp = eqi.ms_localtime())             #EGI trigger
    tracker.send_message(trig_name)                                      #EyeLink trigger

######################################################################
'''
GOAL: Clean up equipment after experiment presentation ends.
Input:  N/A
Output: N/A
'''
def cleanUp():
    #Clean-Up: EEG Equipment
    ns.StopRecording()
    ns.EndSession()
    ns.disconnect()

    #Clean-Up: Eyelink
    tracker.end_experiment('./data') #filenmae will be defined above at INIT (pylink...) EL

    #Clean-Up: Behav Task
    myWin.close()  #Close window
    core.quit()    #Close core
    return

######################################################################
##                        OUTPUT FILES                              ##
######################################################################

#WARNING: Ensure that relative paths start from the same directory as this script.
_thisDir = os.path.dirname(os.path.abspath(__file__)); os.chdir(_thisDir)                                            #Set data directory

fileName = _thisDir + os.sep + u'data' + os.sep + 'Sbj_' + sessionInfo['Participant ID'] + '_axcpt.csv'              #Create participant's unique filename
dataFile = file(str(fileName), 'a')

rowlist = ["part_id", "dob", "age_group", "runner", "date", "block", "trial", "cond", "cue", "probe", \
               "resp", "acc", "cueStart", "cueEnd", "delayStart", "delayEnd", "probeStart", "probeEnd", "rt"]        #rowList

rowformat = "{:18}"*(len(rowlist))

header = "part_id" + ","+ "dob" + ", "+ "age_group" + ","+ "runner" + "," + "date" + "," + "block" + "," \           #Write headers
  + "trial" + "," + "cond" + "," + "cue" + "," + "probe" + "," + "resp" + "," + "acc" + "," + "cueStart" \
  + "," + "cueEnd" + "," + "delayStart" + "," + "delayEnd" + "," + "probeStart" + "," + "probeEnd" + "," + "rt"

dataFile.writelines(header); dataFile.writelines('\n'); dataFile.close()

######################################################################
##                           DEFAULTS                              ##
######################################################################
#Presentation screen
myWin = visual.Window(size = (1280,1024), fullscr = True,
                          winType = 'pyglet', color = '#BFBFBF') 

#Response image objects
posResp = visual.ImageStim(myWin, image = "food.bmp", pos=(-0.5, -0.5)) 
negResp = visual.ImageStim(myWin, image = "cross.bmp", pos=(0.5,-0.5)) 

#Feedback image objects
snooze = visual.ImageStim(myWin, image = "alarmclock.bmp", pos = (0,0))
posFeed = visual.ImageStim(myWin, image = "reward1.bmp", pos = (0,0))
negFeed = visual.ImageStim(myWin, image = "garbage.bmp", pos = (0,0))

#Trial list:
trialList = trialArray('cond_map_exp.csv')  #!!!READ IN TRIAL LIST!!!

#by specific list:
byList = trialArray('by_cond.csv')          #!!!READ IN BY TRIAL LIST!!!

######################################################################
##                     LOAD EGI & EyeLink                           ##
######################################################################

##################
#   EGI import   #
##################
import egi.simple as egi
ms_localtime = egi.ms_localtime; ns = egi.Netstation()
ns.connect('10.0.0.42', 55513)                                         #WARNING: May change depending on room; IP/Port number
ns.BeginSession(); ns.sync(); ns.StartRecording()

##################
#   EL import    #
##################
import pylinkwrapper            
tracker = pylinkwrapper.Connect(myWin, sessionInfo['Participant ID'])  #WARNING: coordinate filename w/ part_id

######################################################################
##                        TASK ADMIN                                ##
######################################################################

##################
#   Block        #
##################
global Nmin1; global Nmin2; global Nmin3                  #Set global variables for tracking prior trial conditions; used in func: weight
global cueStart; global probeStart; global probeEnd       #Set global variables for recording timestamps

block = 0                                                 #Init block count

myWin.mouseVisible = False

while block < 10:                                         #Set number of blocks to admin.
    if block == 5:
        calibrateEL()
        
    if block != 0:                                        #Display block break after every block
        blockInterval()
        
    else:
        calibrateEL()                                     #Call calibrateEL
        instruct()                                        #Display instructions for first block
        prac()                                            #Admin. practice trials for first block
        
    block = block + 1                                     #Increment block
    trialnum = 0                                          #Init trial count for each block

    Nmin1 = 'xx'; Nmin2 = 'xx'; Nmin3 = 'xx'              #Init trackers for prior trial condition; used in func: weight
    order = random.sample(range(18),18)                   #order: create a randomized list of row indicies; used in func: weight
    orderBY = random.sample(range(9),9)                   #orderBY: create a randomized list of row indicies just for BY combinations
    
    ##################
    #   Trial        #
    ################## 
    while trialnum != len(trialList):                                                          #Administer trials within the block
        ns.sync()
        ns.send_event('sTRL', timestamp=egi.ms_localtime())                              

        tracker.set_status('TrialActive')                                                      #EL: trigger start
        tracker.set_trialid()
        tracker.send_message('BeginTrial')
        tracker.record_on()
        
        trialIndex = weight(order)                                                             #trialIndex: determine next acceptable row index to be called from trial list
        
        trialnum, cond, cueFile, probeFile, keyPressed, acc = trial(trialnum, trialIndex)      #run func: trial to administer complete trial sequence
        recordTrial(trialIndex, block, trialnum, cond, cueFile, probeFile, keyPressed, acc)    #run func: recordTrial to write data to dataFile
        
        ns.send_event('eTRL', timestamp=egi.ms_localtime())                                       #EEG: trigger end
                          
        tracker.record_off()                                                                   #EL: trigger end
        tracker.send_message('EndTrial')
        tracker.set_status('TrialInactive')
        tracker.set_trialresult()

cleanUp()
######################################################################################################################################################################################################################################################################################################################################################################
