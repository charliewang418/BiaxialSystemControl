##
##This code permits to run an experiment with the biaxial compression experiment setting.
##It must be run as a super user.
##For a classical use only Input arguments must be changed.
##For more information ask zhenghu@tongji.edu.cn or dong.wang@yale.edu
##
##This code move the four walls of the setup step by step at a given speed on a given distance,
##it triggers camera for 3 kind of pictures,
##it turns the white and UV light on and off
##

#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#
#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#
#Import usefull libraries:
import time
import RPi.GPIO as GPIO
import os
import numpy 
from threading import Thread

#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#
#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#
#Input arguments:

##Freely tunable parameters:
###Name of the experiment (chain of characters):
NamExpe='/home/pi/Desktop/ExpeTest'
###Speed of the translation motor (mm/s, maximum=??):
TransSpeed    = 0.5
###Length of one step for each of the two motors (mm, minimum=??):
StepDist1     = 0.5 
###Number of steps forward:
NbStepFor     = 100
###Relaxation time after motion:
RelTime       = 6

##Calculate displacements for the other two motors
###Total Displacement of the first set of two motors
DispTot1 = range(1, NbStepFor+1) * StepDist1 * 2
###Length of the other side of the shear box
Leng2 = [400.0]

for i in DispTot1:
    Leng2.append(160000.0/(400.0-i))

###Displacement of the second set of motors for each step
for i in range(NbStepFor):
    Disp2.append((Leng2[i+1]-Leng2[i])/2)

##Possibly tunable parameters:
###Camera:
####Iso:
IsoCam1       = '200'
####Shutter speed:
ExpoCam1      = '1'
####Aperture:
AperCam1      = '32'
###Camera white light:
####Iso:
IsoCam2       = '125'
####Shutter speed:
ExpoCam2      = '0.5'
####Aperture:
AperCam2      = '32'
###Camera UV light:
####Iso:
IsoCam3       = '800'
####Shutter speed:
ExpoCam3      = '0.5'
####Aperture:
AperCam3      = '32'
####Coefficient between step and displacement for the linear step motor (step/mm):
CoeffTrans    = 1600
####Number of steps for the polarizer motor:
NbStpPol      = 300
####Speed of the polarizer motor (step/s, Hz):
SpeedPol      = 400

#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#
#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#
#Initializations:

##Create a folder for storage:
os.system('mkdir '+ NamExpe)
os.system('mkdir '+ NamExpe + '/Input')

##Save inputs:
print 'Save inputs'
f=open(NamExpe + '/Input/TranslationSpeed.txt', 'w'); f.write('%f' % TransSpeed); f.close()
f=open(NamExpe + '/Input/StepLength.txt', 'w'); f.write('%f' % StepDist); f.close()
f=open(NamExpe + '/Input/NumberStepForward.txt', 'w'); f.write('%f' % NbStepFor); f.close() 
f=open(NamExpe + '/Input/IsoCamera1.txt', 'w'); f.write(IsoCam1); f.close()
f=open(NamExpe + '/Input/IsoCamera2.txt', 'w'); f.write(IsoCam2); f.close()
f=open(NamExpe + '/Input/IsoCamera3.txt', 'w'); f.write(IsoCam3); f.close()
f=open(NamExpe + '/Input/ExposureCamera1.txt', 'w'); f.write(ExpoCam1); f.close()
f=open(NamExpe + '/Input/ExposureCamera2.txt', 'w'); f.write(ExpoCam2); f.close()
f=open(NamExpe + '/Input/ExposureCamera3.txt', 'w'); f.write(ExpoCam3); f.close()
f=open(NamExpe + '/Input/ApertureCamera1.txt', 'w'); f.write(AperCam1); f.close()
f=open(NamExpe + '/Input/ApertureCamera2.txt', 'w'); f.write(AperCam2); f.close()
f=open(NamExpe + '/Input/ApertureCamera3.txt', 'w'); f.write(AperCam3); f.close()
f=open(NamExpe + '/Input/RelaxationTime.txt', 'w'); f.write('%f' % RelTime); f.close()

##Name of the inputs/outputs :
###Set the mode of numbering the pins of the Raspberry Pi:
GPIO.setmode(GPIO.BCM)
###Camera switch:
OutCam           = 25
###UV light switcher:
OutUV            = 22
###Light switcher:
OutLight         = 27
###Main motor 1 clock:
OutMotClock1     = 5
###Main motor 1 direction:
OutMotDir1       = 6
###Main motor 1 on/off:
OutMotOn1        = 13
###Main motor 2 clock:
OutMotClock2     = 19
###Main motor 2 direction:
OutMotDir2       = 26
###Main motor 2 on/off:
OutMotOn2        = 21
###Polarizer motor clock:
OutMotPolClock   = 18
###Polarizer motor direction:
OutMotPolDir     = 23
###Polarizer motor on/off:
OutMotPolOn      = 24
###Limit tester:
InLim            = 17

#Declare a flab as a global variable to stop limit checking thread:
global FlagStop
FlagStop = 1
												
#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#
#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#
#Define functions:

#################
##Function to check that the stage does not reach a limit:
def CheckLimit(OutMotOn1, OutMotOn2, InLim1, InLim2):
    #Set up the motor driver on/off pin:
    GPIO.setup(InLim1, GPIO.IN)
    GPIO.setup(InLim2, GPIO.IN)
    #Set up the motor driver on/off pin:
    GPIO.setup(OutMotOn1, GPIO.OUT) 	
    GPIO.setup(OutMotOn2, GPIO.OUT) 	
    #Turn the motor on:
    GPIO.output(OutMotOn1, False)   	
    GPIO.output(OutMotOn2, False)   	
    print 'Stage motors are turned on \n'
    time.sleep(2)           
    #Check limit loop
    Flag0 = 1
    while Flag0 & FlagStop:
	Flag1 = GPIO.input(InLim1) #Check limit 1
	Flag2 = GPIO.input(InLim2) #Check limit 2
	if Flag1 or Flag2:
        GPIO.output(OutMotOn, True)
	    print 'Stage motor is turned off' 
	    Flag0 = 0
	time.sleep(0.1)

#################
##Function to move one step :
def StepMove(OutMotClock, OutMotDir, CoeffTrans, StepDist, TransSpeed, Direction):
    #Set the motor direction:
    GPIO.output(OutMotDir, Direction)
    #Compute the pause:
    PauseClock = 0.5 / (TransSpeed * CoeffTrans)
    #Run the clock:
    for itRun in range(int(StepDist * CoeffTrans)): 
        GPIO.output(OutMotClock, True)
        time.sleep(PauseClock)
        GPIO.output(OutMotClock, False)
        time.sleep(PauseClock)

#################
##Function to remove and set the polarizer :
def MovePolarizer(OutMotPolClock, OutMotPolDir, NbStpPol, SpeedPol, Direction):
    #Set the motor direction:
    GPIO.output(OutMotPolDir, Direction)
    #Run the clock:
    PauseClock = 0.5 / SpeedPol
    for itRun in range(NbStpPol): 
        GPIO.output(OutMotPolClock, True)
        time.sleep(PauseClock)
        GPIO.output(OutMotPolClock, False)
        time.sleep(PauseClock)

#################
##Function to take pitures :
def TakePicture(IsoCam1, IsoCam2, IsoCam3, ExpoCam1, ExpoCam2, ExpoCam3, AperCam1, AperCam2, AperCam3, OutMotPolClock, OutMotPolDir, OutLight):
    #Turn the white light on: 
    GPIO.output(OutLight, False)
    time.sleep(0.5)
    #Take Polarized picture:
    os.system('gphoto2 --set-config /main/settings/capturetarget=1 --set-config "/main/imgsettings/iso"='+IsoCam1+' --set-config "/main/capturesettings/aperture"='+AperCam1+' --set-config "/main/capturesettings/focusmode"=Manual --set-config "/main/capturesettings/shutterspeed"='+ExpoCam1+' --trigger-capture')
    time.sleep(float(ExpoCam1) + 0.5)
    #Remove the polarizer:
    MovePolarizer(OutMotPolClock, OutMotPolDir, NbStpPol, SpeedPol, False)
    #Take White picture:
    os.system('gphoto2 --set-config /main/settings/capturetarget=1 --set-config "/main/imgsettings/iso"='+IsoCam2+' --set-config "/main/capturesettings/aperture"='+AperCam2+' --set-config "/main/capturesettings/focusmode"=Manual --set-config "/main/capturesettings/shutterspeed"='+ExpoCam2+' --trigger-capture')
    time.sleep(float(ExpoCam2) + 0.5)
    #Turn the white light off: 
    GPIO.output(OutLight, True)
    #Turn the UV light on:
    GPIO.output(OutUV, False)
    time.sleep(0.5)
    #Take UV picture:
    os.system('gphoto2 --set-config /main/settings/capturetarget=1 --set-config "/main/imgsettings/iso"='+IsoCam3+' --set-config "/main/capturesettings/aperture"='+AperCam3+' --set-config "/main/capturesettings/focusmode"=Manual --set-config "/main/capturesettings/shutterspeed"='+ExpoCam3+' --trigger-capture')
    time.sleep(float(ExpoCam3) + 0.5)
    #Turn the UV light off:
    GPIO.output(OutUV, True)
    #Set the polarizer back:
    MovePolarizer(OutMotPolClock, OutMotPolDir, NbStpPol, SpeedPol, True)

#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#
#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#/~\#
#Run the experiment:

##Set and initialize GPIO:
GPIO.setup(OutCam, GPIO.OUT) 		#Camera external trigger
GPIO.output(OutCam, True)   		#Camera down
GPIO.setup(OutLight, GPIO.OUT) 		#Light switcher
GPIO.output(OutLight, True)   		#light off
GPIO.setup(OutUV, GPIO.OUT) 		#UV light switcher
GPIO.output(OutUV, True)   		#UV light off
GPIO.setup(OutMotClock1, GPIO.OUT) 	#Main motor 1 clock
GPIO.output(OutMotClock1, False)   	
GPIO.setup(OutMotDir1, GPIO.OUT) 	#Main motor 1 direction
GPIO.output(OutMotDir1, False)   		
GPIO.setup(OutMotClock2, GPIO.OUT) 	#Main motor 2 clock
GPIO.output(OutMotClock2, False)   	
GPIO.setup(OutMotDir2, GPIO.OUT) 	#Main motor 2 direction
GPIO.output(OutMotDir2, False)   		
GPIO.setup(OutMotPolClock, GPIO.OUT) 	#Polarizer motor clock
GPIO.output(OutMotPolClock, False)   	
GPIO.setup(OutMotPolDir, GPIO.OUT) 	#Polarizer motor direction
GPIO.output(OutMotPolDir, False)   
GPIO.setup(OutMotPolOn, GPIO.OUT) 	#Polarizer motor on-off
GPIO.output(OutMotPolOn, True)   	#Turn Polarizer motor on

##Take the initial pictures:
print 'Take the first pictures'
TakePicture(IsoCam1, IsoCam2, IsoCam3, ExpoCam1, ExpoCam2, ExpoCam3, AperCam1, AperCam2, AperCam3, OutMotPolClock, OutMotPolDir, OutLight)

##Turn the main motor on:
T1 = Thread(target = CheckLimit, args = (OutMotOn1, OutMotOn2, InLim1, InLim2))
T1.start()

##Run the linear shear:
###Steps forward:
for itFor in range(NbStepFor):
    ####Move the stage to isotropically compress:
    T2 = Thread(target = StepMove, args = (OutMotClock1, OutMotDir1, CoeffTrans, StepDist, TransSpeed, True))
    T3 = Thread(target = StepMove, args = (OutMotClock2, OutMotDir2, CoeffTrans, Disp2[itFor], TransSpeed, False))
    T2.start()
    T3.start()
    time.sleep(RelTime)
    ####Take pictures
    TakePicture(IsoCam1, IsoCam2, IsoCam3, ExpoCam1, ExpoCam2, ExpoCam3, AperCam1, AperCam2, AperCam3, OutMotPolClock, OutMotPolDir, OutLight)
	

print 'I am done ! :-)'

##Kill the limit checking thread:
FlagStop = 0
time.sleep(1)

##GPIO house keeping
GPIO.setup(OutLight, GPIO.OUT) 		#Light switcher
GPIO.output(OutLight, True)   		#light off
GPIO.setup(OutUV, GPIO.OUT) 		#UV light switcher
GPIO.output(OutUV, True)   		#UV light off
GPIO.setup(OutMotPolOn, GPIO.OUT) 	#Polarizer motor on-off
GPIO.output(OutMotPolOn, False)   	#Turn Polarizer motor off

##Clean channels:
GPIO.cleanup()
