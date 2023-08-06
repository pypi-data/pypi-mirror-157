#!/usr/bin/env python3
#
# Marc Compere, comperem@erau.edu
# created : 29 Dec 2021
# modified: 24 Jan 2022


import logging
import threading
import time
from datetime import datetime
import code # drop into a python interpreter to debug using: code.interact(local=locals())

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )




class MissionState:
    """A class for advancing through mission sequences, which essentially is a"""
    """mode-control or mode manager for a specific vehicle.                   """
    """Each missionState has a set of criteria to meet and makes assignments  """
    """to the priority list in the behavior table to prioritize the behavior  """
    """that increases progress to complete the current missionState.          """
    """Every missionState enabled behavior must report percent complete       """
    """to compute the progress at each missionState.                          """
    """                                                                       """
    """The mission sequencer is modeled after a waypoint follower with a      """
    """sequence of missionStates, analogous to waypoints, with conditions and """
    """thresholds monitored periodically. When the condition triggers, the    """
    """next missionState is assigned which has it's own new set of conditions """
    """to monitor. Advancing the missionState is analogous to passing by a    """
    """waypoint within a certain radius and advancing to the next waypoint.   """
    
    def __init__(self,cfg,veh):
        self.vid    = veh.vid
        self.veh    = veh
        self.v2v    = veh.v2v
        self.cfg    = cfg
        self.beh    = veh.beh
        #self.debug  = cfg.debug
        
        # persistent class variables to accomplish each mission's logic in evaluateMissionAction()
        self.tStart = 0.0 # (s) elapsed time variable must be persistent across function calls to evaluateMissionAction()
        self.mStateIterationCnt=0
        self.missionComplete=False
        
        self.runState     = cfg.runState # use mutable list so classes can access; note: ints and floats are immutable!
        self.runStatePrev = cfg.runStatePrev
        
        self.e = veh.e
        
        if hasattr(cfg,'missionCommands') and len(cfg.missionCommands)>0: # if exists and not empty...
            logging.debug('missionCommands detected: starting mission state sequence thread')
            w1 = threading.Thread(name='mStateSeq', target=self.missionStateSequencer, args=())
            w1.start()
        else:
            logging.debug('no missionCommands; not starting mission state sequencer')
        
    
    # ==============================================================================
    # *thread* that is launched with awareness of: veh, beh, and v2v objects
    # primary outputs: periodic updates to (a) this vid's v2v outbound messages and
    #                  (b) updates to the behavior table to accomplish each mission command
    # =======================================================================================
    def missionStateSequencer(self):
        dt=0.2 # (s) 0.2 is 5Hz
        #dt=1
        
        runStateChanged=False
        
        # start this vid's mission at the beginning
        mIdx=0 # index into mStateKeys (this controls the missionState selection)
        mStateKeys       = list( self.cfg.missionCommands.keys() ) # ['missionCmd1', 'missionCmd2', 'missionCmd3', 'missionCmd4', 'missionCmd10', 'missionCmd5']
        mStateKey        = mStateKeys[ mIdx ] # mStateKey='missionCmd2' ; mStateKeys are from config file:  ['missionCmd1', 'missionCmd2', 'missionCmd3', 'missionCmd4', 'missionCmd10', 'missionCmd5']
        missionState     = self.cfg.missionCommands[ mStateKey ]['missionState'] # integer from config file: missionCmd1:  {'vid':100, 'missionState':  1 , 'action':'waitElapsed',      'eTimeThresh'    :  5.1 }
        missionStateLast = -1 # previouos missionState (gets reset in this method); must be different at t=0 to trigger newState in evaluateMissionAction()
        pctComplete      = 0.0
        missionProgress  = -1
        
        while self.e.is_set() == False:
            
            missionProgress             = missionState + pctComplete
            self.veh.missionPctComplete = pctComplete # update veh class attribute so it's conveyed to core dashboard and all others on v2v
            self.veh.missionProgress    = missionProgress # update errbody else on v2v network
            
            logging.debug('')
            logging.debug('{0}: runState=[{1}], runStatePrev=[{2}], missionState=[{3}], missionProgress=[{4}]'.format('missionStateSequencer()',self.veh.runState[0],self.veh.runStatePrev,missionState,missionProgress))
            logging.debug('')
            
            # only evaluate missionState conditions while runState==3: "GO!"
            if (self.veh.runState[0]==3):
                
                # is this missionState completed yet?
                if self.missionComplete==False:
                    logging.debug('[{0}] missionState={1}, pctComplete={2:0.2f}, missionProgress={3:0.2f} for vid={1}'.format( datetime.now().strftime('%c') , missionState, pctComplete, missionProgress, self.vid ))
                    condition, pctComplete, missionStateLast, mIdx = self.evaluateMissionAction( mStateKey , missionState, missionStateLast, missionProgress, mIdx )
                
                if (condition==True):
                    # advance to next missionState
                    #missionStateLast = missionState # store previous missionState
                    mIdx +=1 # increment index to next missionState
                    # assign new missionState
                    if mIdx<len(mStateKeys):
                        mStateKey    = mStateKeys[ mIdx ] # mStateKey='missionCmd2' ; mStateKeys are from config file:  ['missionCmd1', 'missionCmd2', 'missionCmd3', 'missionCmd4', 'missionCmd10', 'missionCmd5']
                        missionState = self.cfg.missionCommands[ mStateKey ]['missionState'] # assign new missionState in this thread; missionState is an integer, like 20 or 50
                        pctComplete  = 0.0 # reset pctComplete on this new missionState
                        
                        # veh assignments will get sent out on v2v network
                        self.veh.missionAction      = self.cfg.missionCommands[ mStateKey ]['action']       # report new missionAction   to v2v network; veh object gets sent as v2v outbound message in myVehicle.py | gather_outputs()
                        self.veh.missionState       = self.cfg.missionCommands[ mStateKey ]['missionState'] # report new missionState    to v2v network
                        self.veh.missionProgress    = self.veh.missionState + 0.0                           # report new missionProgress to v2v network; progress is zero if this just triggered to a new missionState
                        self.veh.missionLastCmdTime = datetime.now().strftime('%c') # when was last command changed?
                        self.veh.missionStatus      = 'active'
                        self.veh.missionCounter    += 1 # counter for every state change; note: this will be different from missionCommands list if there are any 'goToMissionState' loop-arounds
                    else:
                        logging.debug('[{0}] mission complete for vid={1}!'.format( datetime.now().strftime('%c') , self.vid ))
                        logging.debug('\tlast missionAction     = [{0}]'.format(self.veh.missionAction))
                        logging.debug('\tlast missionState      = [{0}]'.format(self.veh.missionState))
                        logging.debug('\tlast missionProgress   = [{0}]'.format(self.veh.missionProgress))
                        logging.debug('\tlast missionLastCmdTime= [{0}]'.format(self.veh.missionLastCmdTime))
                        logging.debug('\tlast missionCounter    = [{0}]'.format(self.veh.missionCounter))
                        self.missionComplete=True # mission sequence complete; stop evaluating evaluateMissionAction(); condition==False
                        condition==False
                        pctComplete=1.0
                        self.veh.missionStatus      = 'complete'
                
                #self.veh.assignBehPriorities() # flip switches in behavior table to accomplish the current mission command
                
            self.e.wait( dt ) # (s)
        
        logging.debug('Exiting')
    
    
    # mission action library - evaluate the condition for this missionCommand
    # a method only called in mStateSeq()
    def evaluateMissionAction( self, mStateKey, missionState, missionStateLast, missionProgress, mIdx ):
        
        thisVehCmd = self.cfg.missionCommands[mStateKey] # dictionary straight from the config file: {'vid': 100, 'missionState': 10, 'action': 'waitOnVeh', 'otherVeh': 101, 'progress': 11.0}
        thisVehAction = thisVehCmd['action'] # 'waitElapsed' or 'waitOnVeh' or 'goToPoint', straight from the config file in [missionCommands]
        #print('thisVehAction={0}'.format(thisVehAction))
        
        condition = False # default answer: nope
        newState  = False # leading edge flag for a new missionState
        pctComplete = 0.0
        if missionState != missionStateLast:
            newState = True # a new missionState has just been detected, even at t=0
            logging.debug('[{0}] detected new missionState={1}!   new action: [{2}] from config file entry [{3}] for vid={4}'.format( datetime.now().strftime('%c') , missionState, thisVehAction, mStateKey, self.vid))
        
        
        # wait a certain duration; based on this vehicle's local time only; no v2v network involved
        # thisVehCmd={'vid':100, 'missionState':  1 , 'action':'waitElapsed',      'eTimeThresh'    :  5.1 }
        if thisVehAction == 'waitElapsed':
            eTimeThresh = thisVehCmd['eTimeThresh'] # (s)
            if newState == True:
                self.tStart = time.time() # (s) capture timer starting time in seconds since the epoch, 01 Jan 1970
                logging.debug('\t[action]: {0} from config file entry [{1}]: threshold is {2}(s)'.format(thisVehAction,mStateKey,eTimeThresh))
            eTime       = time.time() - self.tStart # (s)
            pctComplete = eTime/eTimeThresh # (%) on [0 1]
            if (eTime >= eTimeThresh):
                condition=True # bingo! report this elapsed missionState as done
        
        
        # thisVehCmd={'vid':100, 'missionState':100 , 'action':'goToMissionState', 'newMissionState':    1 , 'maxIterations': 3 }
        if thisVehAction == 'goToMissionState':
            maxIterations = thisVehCmd['maxIterations']
            self.mStateIterationCnt += 1
            if (self.mStateIterationCnt <= maxIterations):
                # prepare for new missionState; walk the entire missionCommands dictionary and find first that matches newMissionState
                newMissionState = thisVehCmd['newMissionState']
                pctComplete=0 # <-- this integer zero is a flag for 9 lines below!
                logging.debug('\t[action]: {0} from config file entry [{1}]: incremented mStateIterationCnt to {2}, maxIterations={3}'.format(thisVehAction,mStateKey,self.mStateIterationCnt,maxIterations))
                logging.debug('\t\tnow, where is newMissionState={0} in the missionCommands? searching in vid={1}...'.format(newMissionState,self.vid))
                for i, (k,v) in enumerate( self.cfg.missionCommands.items() ):
                    logging.debug('\t\t\ti={0}, k={1}, v={2}'.format(i,k,v))
                    if v['missionState']==newMissionState:
                        mIdx=i-1 # subtract 1 so when mIdx+=1 it gets it right in missionStateSequencer()
                        pctComplete=1.0 # 100% complete in 1 step because 'goToMissionState' is a 1-evaluation command
                        break # stop walking through the missionCommands dictionary
                if pctComplete==0:
                    # didn't find the newMissionState; report this but don't barf
                    logging.debug('error!: did not find newMissionState={0} in missionCommands - probably a typo! check [{1}] in config file for vid={2}'.format(newMissionState,mStateKey,self.vid))
                else:
                    # ok, we found the newMissionState and prepared mIdx that is 1 smaller than necessary so when mIdx+=1 in mStateSeq() it'll get it right
                    condition=True
            else:
                # proceed to the next missionCommand (do not adjust mIdx, just trigger condition==True)
                logging.debug('already reached maxIterations={0} for this action [{1}]! this mission command is complete for vid={2}!   mStateIterationCnt={3}'.format(maxIterations,thisVehAction,self.vid,self.mStateIterationCnt))
                logging.debug('no change. reporting complete. proceeding to the next mission command...')
                condition=True
                pctComplete=1.0
        
        # ------------------------------------
        # decode action-specific data fields
        # ------------------------------------
        
        # evaluate waitOnVeh action:
        if thisVehAction == 'waitOnVehProgress':
            otherVeh   = thisVehCmd['otherVeh']   # who are you waiting on?     'otherVeh': 101
            progThresh = thisVehCmd['progThresh'] # how far must they be?       'progress': 11.0
            logging.debug('[action]: {0} from config file entry [{1}]: vid={2}, missionState={3}, wait until progress of {4} is >={5}'.format(thisVehAction,mStateKey,self.vid,missionState,otherVeh,progThresh))
            # we only know about the other vehicle from the v2v communications
            # debug: veh.gather_behavior_inputs()
            if otherVeh in self.v2v.v2vState: # if the other vehicle is in the v2vState (from the v2v network)
                staleFlag = self.v2v.v2vState[otherVeh]['stale'] # is the v2vState data recent and relevant?
                if staleFlag == False: # this means there's good data (it's not stale)
                    otherAction      = self.v2v.v2vState[otherVeh]['missionAction']
                    otherState       = self.v2v.v2vState[otherVeh]['missionState']
                    otherProgress    = self.v2v.v2vState[otherVeh]['missionProgress']
                    otherPctComplete = self.v2v.v2vState[otherVeh]['missionPctComplete']
                    pctComplete      = otherPctComplete
                    logging.debug('[action]: {0}, [vid={1}] waiting for progress of {2} to be >= {3}; it is currently at {4} during {5} (pctComplete={6})'.format(thisVehAction,self.vid,otherVeh,progThresh,  otherProgress,otherAction,otherPctComplete))
                    condition = ( otherProgress >= progThresh )
                    if condition==True:
                        logging.debug('[action]: {0}, [vid={1}] boom! progress of {2} was >= {3}. this veh done with missionState={4}'.format(thisVehAction,self.vid,otherVeh,progThresh,missionState))
        
        
        # evaluate goToPoint action
        if thisVehAction == 'goToPoint':
            pt          = thisVehCmd['point']
            vel         = thisVehCmd['speed'] # (m/s) or whatever user puts in config file; note: all vehicle dynamics are in (m/s)
            riseRate    = thisVehCmd['riseRate'] # (m/s) rise rate, mainly for quad-copter commands
            rThresh     = thisVehCmd['rThresh'] # (m) or whatever user puts in config file; note: radius is assumed to be meters in behaviors() threads
            arrivalType = thisVehCmd['arrivalType']
            
            if newState == True:
                logging.debug('[action]: {0} from config file entry [{1}]: sending pt=[{2}] and vel=[{3}] to goToPoint() behavior'.format(thisVehAction,mStateKey,pt,vel))
                self.veh.goToPointCmd.append( {'pt':pt, 'vel':vel, 'riseRate':riseRate, 'rThresh':rThresh, 'arrivalType':arrivalType} ) # send this message to goToPoint() behavior
                pctComplete = 0.0
            else:
                pctComplete = self.beh.pctCompleteGoToPoint # this is computed in behaviors | goToPoint()
            
            if self.veh.goToPointDone.is_set():
                condition=True # bingo! goToPoint() has reported it moved to within the radius threshold of the current point
                self.veh.goToPointDone.clear() # clear the 'finished' flag b/c we're done with this mission action
        
        
        
        
        #condition=False
        #pctComplete=0.1
        if condition==True:
            logging.debug(' ')
            logging.debug('[{0}] condition==True! during [{1}], missionState={2} from action [{3}] for vid={4}'.format( datetime.now().strftime('%c') , mStateKey, missionState, thisVehAction,self.vid))
            logging.debug(' ')
            #pctComplete=0.0 # <-- reest to zero to prevent next missionStateSequencer() loop from accidentally triggering next command complete
        
        if newState==True:
            missionStateLast = missionState # store previous missionState
        
        return condition, pctComplete, missionStateLast, mIdx
    
    
    # =======================================================================================
    #                                   missionCmdsToBeh()
    # =======================================================================================
    # method: (not a thread)
    # missionCmdsToBeh() manages messages to behaviors from missionStateSequencer()
    #       --> behavior enable or disable
    #       --> goToPoint(), ok, which point? do what when you arrive?
    #
    def missionCmdsToBeh(self, enabled):
        
        # send boolean enable message to this behavior; it's either True or False
        #self.veh.deqGoToPointEnable.append( enabled ) # inform goToPoint() behavior (once) that runState just changed
        
        pass






if __name__ == "__main__":
    
    from myVehicle import MyVehicle
    from readConfigFile import readConfigFile
    from route_init import route_init
    from veh_udp_io import Veh_udp_io
    
    # class MyVehicle:
    #     pass # dummy vehicle class for testing Behaviors class
    
    debug=1 # (0/1/2/3) 0->none, 1->some, 2->more, 3->lots
    vid = 100 # vid == vehicle identifier for this vehicle process, assigned by MoVE core
    
    #cfgFile = '../scenario/default.cfg' # python's .ini format config file
    #cfgFile = '../scenario/missionDefault.cfg' # python's .ini format config file
    cfgFile = '../scenario/missionTestWaitTimes.cfg' # config file with easily-test-able time-based delays
    #cfgFile = '../scenario/missionTestWaitTimesAndgoToPoint.cfg' # time delays and goToPoint() to develop missionState behavior enable/disable
    cfg, veh_names_builtins, veh_names_live_gps   = readConfigFile( cfgFile, vid ) 
    
    cfg.udp_port_gps=0
    cfg.live_gps_follower = False # (True/False)
    cfg.name = "missionState testing"
    cfg.runState     = [1]   # initial runstate; valid range is: [1 5]
    cfg.runStatePrev =  0    # created in cfg. for behavior accessibility
    
    
    timeout = 0.5 # periodically loop to catch the graceful exit signal, e.is_set()
    
    
    cfg = route_init(cfg) # this creates cfg.routeCfg ; the route_init() function is in routes_functions.py in ./veh_model directory
    #code.interact(local=dict(globals(), **locals())) # drop into a python interpreter with globals and locals available
    
    # init the vehicle object and launch behavior threads
    localLogFlag=1
    veh = MyVehicle(cfg, localLogFlag)
    veh.v2v.v2vPrtFlag=False #True # (True/False) print v2v console updates?
    
    #code.interact(local=dict(globals(), **locals())) # drop into a python interpreter with globals and locals available
    mState = MissionState(cfg,veh) # create the missionState object; start misson state sequencer thread
    
    # this is only necessary for emulating the vehicle model calls below (gather inputs and outputs)
    udp_io = Veh_udp_io(cfg, veh) # udp_io has visibility to this sinble veh object and behaviors
    
    
    
    # --------------------------------------
    # -------------- main loop -------------
    # --------------------------------------
    eMain = threading.Event()
    try:
        while True:
            
            if udp_io.eRunState.is_set() is True:
                payload = udp_io.qRunState.get(block=True,timeout=timeout) # Queue.get(block=True, timeout=None), timeout is for catching the thread exit signal, e.is_set()
                veh.runStatePrev = veh.runState # capture last runState
                veh.runState[0]  = [ payload['runStateCmd'] ] # assign runState from runStateCmd just received; note: this is the *only* way runState can change; all others read-only runState
                logging.debug('')
                logging.debug('t={0:0.6f}: assigning runState={1}, {2}'.format(time.time(),veh.runState, veh.runStateDesc[veh.runState]))
                logging.debug('')
                udp_io.eRunState.clear()
            
            
            # this works well except it does not set initial conditions at runState==2, so goToPoint() reports 'arrived' immediately for action=='goToPoint'
            
            
            # v2v updates are buried in the gather_behavior_inputs() and gather_outputs()
            if cfg.live_gps_follower==True:
                veh.gather_live_gps_inputs() # get latest UTM coordinates from GPS lat/lon; cannot block; veh.tick() controls loop rate with srt()
            else:
                veh.gather_behavior_inputs() # update v2vState and veh model behavior inputs; cannot block
            veh.gather_outputs( udp_io.recvCnt, udp_io.sendCnt, udp_io.errorCnt ) # update veh.vehData

            eMain.wait(1) # tick this loop as if it were the vehicle model in an active runState, like Ready or Go
    
    
    except KeyboardInterrupt:
        logging.debug('caught KeyboardInterrupt, exiting.')
        udp_io.e.set() # tell udp_io threads to exit
        veh.exit()     # exit myVehicle, v2v, behavior, and mState threads
    
    
    # monitoring the thread exit process
    main_thread = threading.main_thread()
    while len(threading.enumerate())>1:
        for t in threading.enumerate():
            if t is main_thread:
                continue
            logging.debug('{0} threads still remaining, including: {1}'.format( len(threading.enumerate()), t.getName() ))
        
        time.sleep(1)
    
    logging.debug('[{0}]: exiting veh, beh, v2v, mState threads'.format( datetime.now().strftime('%c') ))




